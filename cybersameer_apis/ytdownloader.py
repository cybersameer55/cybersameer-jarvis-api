"""
@api /ytdownloader
@method GET
@param url
@usage /ytdownloader?key=YOUR_API_KEY&url=YOUTUBE_LINK
"""
from flask import Blueprint, request, redirect
from urllib.parse import quote, urlparse, parse_qs, unquote
import re
import yt_dlp
from core import check_access, clean_response, send_response

ytdownloader_bp = Blueprint("ytdownloader", __name__)


# ---------- YouTube URL se Video ID nikaalna ----------
def extract_video_id(url):
    if not url:
        return None

    url = unquote(url)
    parsed = urlparse(url)
    query = parse_qs(parsed.query)

    # Method 1: 'v' parameter
    if 'v' in query:
        return query['v'][0]

    # Method 2: Path based patterns
    path = parsed.path
    patterns = [
        r'^/shorts/([\w-]+)',
        r'^/live/([\w-]+)',
        r'^/embed/([\w-]+)',
        r'^/v/([\w-]+)',
        r'^/([\w-]+)$',
    ]
    for pattern in patterns:
        match = re.search(pattern, path)
        if match:
            return match.group(1)

    # Method 3: Full URL regex fallback
    full_patterns = [
        r'(?:youtu\.be\/)([\w-]+)',
        r'(?:youtube\.com\/shorts\/)([\w-]+)',
        r'(?:youtube\.com\/live\/)([\w-]+)',
        r'(?:youtube\.com\/embed\/)([\w-]+)',
        r'(?:youtube\.com\/v\/)([\w-]+)',
        r'(?:youtube\.com\/watch\?.*?v=)([\w-]+)'
    ]
    for pattern in full_patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return None


# ---------- Main endpoint: /ytdownloader ----------
@ytdownloader_bp.route("/ytdownloader", methods=["GET"])
def ytdownloader():
    key = request.args.get("key", "")
    url = request.args.get("url", "")

    user, err = check_access(key)
    if err:
        return err

    if not url:
        return send_response("error", {}, {"message": "YouTube URL required"})

    video_id = extract_video_id(url)
    if not video_id:
        return send_response("error", {}, {"message": f"Invalid YouTube URL. URL: {url}"})

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'ignoreerrors': True,
        'verbose': False,
        'format': 'all',
        'socket_timeout': 15,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            if info is None:
                return send_response("error", {}, {"message": "Video unavailable. Private, age-restricted, or region-blocked."})

            if 'entries' in info:
                return send_response("error", {}, {"message": "Playlist URLs not supported. Please provide a single video URL."})

            # ---------- Metadata ----------
            metadata = {
                "video_id": video_id,
                "title": info.get('title'),
                "description": info.get('description'),
                "channel_name": info.get('uploader'),
                "channel_id": info.get('channel_id'),
                "channel_url": info.get('channel_url'),
                "publish_date": info.get('upload_date'),
                "duration": info.get('duration'),
                "duration_string": info.get('duration_string'),
                "views": info.get('view_count'),
                "likes": info.get('like_count'),
                "comment_count": info.get('comment_count'),
                "tags": info.get('tags', []),
                "categories": info.get('categories', []),
                "thumbnail": info.get('thumbnail'),
                "thumbnails": [
                    {
                        "url": t.get('url'),
                        "width": t.get('width'),
                        "height": t.get('height')
                    }
                    for t in info.get('thumbnails', []) if t.get('url')
                ],
                "is_live": info.get('live_status') == 'is_live',
                "language": info.get('language') or info.get('default_language'),
                "age_limit": info.get('age_limit'),
                "webpage_url": info.get('webpage_url'),
            }

            # ---------- Formats (with direct stream URLs, no download) ----------
            formats = []
            seen_resolutions = set()

            for f in info.get('formats', []):
                # Sirf video formats
                if f.get('vcodec') == 'none':
                    continue

                resolution = f.get('resolution')
                if not resolution or resolution == 'none':
                    height = f.get('height')
                    resolution = f"{height}p" if height else 'unknown'

                # Unique resolutions only
                if resolution in seen_resolutions:
                    continue
                seen_resolutions.add(resolution)

                filesize = f.get('filesize') or f.get('filesize_approx')

                formats.append({
                    "itag": f.get('format_id'),
                    "resolution": resolution,
                    "width": f.get('width'),
                    "height": f.get('height'),
                    "fps": f.get('fps'),
                    "filesize": filesize,
                    "ext": f.get('ext'),
                    "vcodec": f.get('vcodec'),
                    "acodec": f.get('acodec'),
                    "format_note": f.get('format_note', ''),
                    "stream_url": f.get('url'),  # Direct YouTube stream URL
                    "has_audio": f.get('acodec') != 'none',
                })

            # Resolution ke hisaab se sort (low to high)
            def sort_key(f):
                res = f['resolution']
                if res and 'p' in res:
                    try:
                        return int(res.split('p')[0])
                    except:
                        pass
                return 0

            formats.sort(key=sort_key)

            # ---------- Audio only formats ----------
            audio_formats = []
            for f in info.get('formats', []):
                if f.get('vcodec') == 'none' and f.get('acodec') != 'none':
                    audio_formats.append({
                        "itag": f.get('format_id'),
                        "ext": f.get('ext'),
                        "acodec": f.get('acodec'),
                        "abr": f.get('abr'),
                        "filesize": f.get('filesize') or f.get('filesize_approx'),
                        "stream_url": f.get('url'),
                    })

            clean_data = clean_response({
                "metadata": metadata,
                "video_formats": formats,
                "audio_formats": audio_formats,
            })

            return send_response("success", clean_data, {
                "user": user["name"],
                "input_url": url,
                "total_video_formats": len(formats),
                "total_audio_formats": len(audio_formats),
            })

    except Exception as e:
        error_msg = str(e)
        if "Sign in to confirm your age" in error_msg:
            return send_response("error", {}, {"message": "Age-restricted video."})
        elif "This video is not available" in error_msg:
            return send_response("error", {}, {"message": "Video unavailable."})
        return send_response("error", {}, {"message": error_msg})


# ---------- Backward compatibility ----------
@ytdownloader_bp.route("/formats", methods=["GET"])
def get_formats():
    key = request.args.get("key", "")
    url = request.args.get("url", "")
    return redirect(f"/ytdownloader?key={key}&url={quote(url)}")


@ytdownloader_bp.route("/video/<video_id>", methods=["GET"])
def get_video(video_id):
    key = request.args.get("key", "")
    url = f"https://youtu.be/{video_id}"
    return redirect(f"/ytdownloader?key={key}&url={quote(url)}")


@ytdownloader_bp.route("/health", methods=["GET"])
def health():
    return send_response("success", {"status": "ok"}, {})
