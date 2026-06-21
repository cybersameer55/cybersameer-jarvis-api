"""
@api /ytdownloader
@method GET
@param url
@usage /ytdownloader?key=YOUR_API_KEY&url=YOUTUBE_LINK
"""
from flask import Blueprint, request, send_file, redirect
from urllib.parse import quote, urlparse, parse_qs
import os
import re
import tempfile
import shutil
import yt_dlp
from core import check_access, clean_response, fetch_api, send_response

ytdownloader_bp = Blueprint("ytdownloader", __name__)

# ---------- YouTube URL se Video ID nikaalna - STRONG VERSION ----------
def extract_video_id(url):
    if not url:
        return None
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    # Sabse pehle 'v' parameter check karo
    if 'v' in query:
        return query['v'][0]
    # Agar nahi mila toh regex se try karo (shorts, youtu.be, embed, etc.)
    patterns = [
        r'(?:youtu\.be\/)([\w-]+)',
        r'(?:youtube\.com\/shorts\/)([\w-]+)',
        r'(?:youtube\.com\/live\/)([\w-]+)',
        r'(?:youtube\.com\/embed\/)([\w-]+)',
        r'(?:youtube\.com\/v\/)([\w-]+)',
        r'(?:youtube\.com\/watch\?.*?v=)([\w-]+)'  # fallback
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

# ---------- Main endpoint: /ytdownloader ----------
@ytdownloader_bp.route("/ytdownloader", methods=["GET"])
def ytdownloader():
    """
    @api /ytdownloader
    @method GET
    @param url
    @usage /ytdownloader?key=YOUR_API_KEY&url=YOUTUBE_LINK
    """
    key = request.args.get("key", "")
    url = request.args.get("url", "")

    user, err = check_access(key)
    if err:
        return err

    if not url:
        return send_response("error", {}, {"message": "YouTube URL required"})

    # Video ID nikaalo
    video_id = extract_video_id(url)
    if not video_id:
        return send_response("error", {}, {"message": "Invalid YouTube URL – cannot extract video ID"})

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'ignoreerrors': True,
        'verbose': False,
        'format': 'all',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if info is None:
                return send_response("error", {}, {"message": "Video unavailable. Private, age-restricted, or region-blocked."})

            # Agar playlist hai toh entries hongi – reject
            if 'entries' in info:
                return send_response("error", {}, {"message": "Playlist URLs are not supported. Provide a single video URL."})

            # Metadata
            metadata = {
                "video_id": video_id,
                "title": info.get('title'),
                "description": info.get('description'),
                "channel_name": info.get('uploader'),
                "channel_id": info.get('channel_id'),
                "publish_date": info.get('upload_date'),
                "duration": info.get('duration'),
                "views": info.get('view_count'),
                "likes": info.get('like_count'),
                "tags": info.get('tags', []),
                "category": info.get('categories', [''])[0] if info.get('categories') else None,
                "thumbnail": info.get('thumbnail'),
                "live_status": info.get('live_status') == 'is_live',
                "language": info.get('language') or info.get('default_language')
            }

            # Sabhi formats – sirf video waale
            formats = []
            for f in info.get('formats', []):
                if f.get('vcodec') != 'none':
                    resolution = f.get('resolution')
                    if not resolution or resolution == 'none':
                        height = f.get('height')
                        resolution = f"{height}p" if height else 'unknown'
                    filesize = f.get('filesize') or f.get('filesize_approx')
                    download_link = f"/ytdownloader/download?video_id={video_id}&itag={f['format_id']}&key={key}"
                    formats.append({
                        "itag": f['format_id'],
                        "resolution": resolution,
                        "fps": f.get('fps'),
                        "filesize": filesize,
                        "ext": f['ext'],
                        "format_note": f.get('format_note', ''),
                        "download_url": download_link
                    })

            # Resolution ke hisaab se sort
            def sort_key(f):
                res = f['resolution']
                if res and 'p' in res:
                    try:
                        return int(res.split('p')[0])
                    except:
                        pass
                return 0
            formats.sort(key=sort_key)

            # Unique resolutions
            seen = set()
            unique_formats = []
            for f in formats:
                key_res = f['resolution']
                if key_res not in seen:
                    seen.add(key_res)
                    unique_formats.append(f)
            formats = unique_formats

            clean_data = clean_response({
                "metadata": metadata,
                "formats": formats
            })

            return send_response("success", clean_data, {
                "user": user["name"],
                "input_url": url
            })

    except Exception as e:
        error_msg = str(e)
        if "Sign in to confirm your age" in error_msg:
            return send_response("error", {}, {"message": "Age-restricted video. Provide cookies."})
        elif "This video is not available" in error_msg:
            return send_response("error", {}, {"message": "Video unavailable"})
        return send_response("error", {}, {"message": error_msg})

# ---------- Download endpoint (unchanged) ----------
@ytdownloader_bp.route("/download", methods=["GET"])
def download_video():
    key = request.args.get("key", "")
    video_id = request.args.get("video_id")
    itag = request.args.get("itag")

    user, err = check_access(key)
    if err:
        return err

    if not video_id or not itag:
        return send_response("error", {}, {"message": "Missing 'video_id' or 'itag' parameter"})

    url = f"https://youtu.be/{video_id}"

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': itag,
        'outtmpl': '%(title)s.%(ext)s',
        'ignoreerrors': True,
        'retries': 5,
        'fragment_retries': 5,
        'verbose': False,
    }

    temp_dir = tempfile.mkdtemp()
    original_cwd = os.getcwd()
    os.chdir(temp_dir)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if info is None:
                return send_response("error", {}, {"message": "Video unavailable"})

            filename = ydl.prepare_filename(info)
            if not os.path.exists(filename):
                for f in os.listdir('.'):
                    if f.startswith(info.get('title', '')):
                        filename = f
                        break

            if not os.path.exists(filename):
                return send_response("error", {}, {"message": "File not found"})

            return send_file(filename, as_attachment=True)

    except Exception as e:
        error_msg = str(e)
        if "Sign in to confirm your age" in error_msg:
            return send_response("error", {}, {"message": "Age-restricted video"})
        elif "This video is not available" in error_msg:
            return send_response("error", {}, {"message": "Video unavailable"})
        return send_response("error", {}, {"message": error_msg})
    finally:
        os.chdir(original_cwd)
        shutil.rmtree(temp_dir, ignore_errors=True)

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