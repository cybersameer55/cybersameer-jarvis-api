"""
@api /ytdownloader
@method GET
@param url
@usage /ytdownloader?key=YOUR_API_KEY&url=YOUTUBE_LINK
"""

import os
import re
import tempfile
import shutil
from urllib.parse import urlparse, parse_qs
from flask import Blueprint, request, send_file
import yt_dlp

# ---------- Core functions (आपके पास पहले से हैं) ----------
from core import check_access, clean_response, send_response

ytdownloader_bp = Blueprint("ytdownloader", __name__)

# ---------- Helper: YouTube URL से Video ID निकालें ----------
def extract_video_id(url):
    if not url:
        return None
    parsed = urlparse(url)
    if parsed.hostname in ('www.youtube.com', 'youtube.com', 'm.youtube.com'):
        if parsed.path == '/watch':
            query = parse_qs(parsed.query)
            if 'v' in query:
                return query['v'][0]
    patterns = [
        r'(?:youtu\.be\/)([\w-]+)',
        r'(?:youtube\.com\/shorts\/)([\w-]+)',
        r'(?:youtube\.com\/live\/)([\w-]+)',
        r'(?:youtube\.com\/embed\/)([\w-]+)',
        r'(?:youtube\.com\/v\/)([\w-]+)',
        r'(?:youtube\.com\/watch\?.*?v=)([\w-]+)'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

# ---------- मुख्य एंडपॉइंट: /ytdownloader ----------
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

    # Access check
    user, err = check_access(key)
    if err:
        return err

    if not url:
        return send_response("error", {}, {"message": "YouTube URL required"})

    # Playlist check – single video only
    if "playlist" in url or "list=" in url:
        return send_response("error", {}, {"message": "Playlist URLs not supported"})

    video_id = extract_video_id(url)
    if not video_id:
        return send_response("error", {}, {"message": "Invalid YouTube URL"})

    # yt-dlp से सारी जानकारी लें (बिना डाउनलोड किए)
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": False,
        "ignoreerrors": True,
        "verbose": False,
        "format": "all",  # सभी formats लाने के लिए
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if info is None:
                return send_response("error", {}, {"message": "Video unavailable (private, age-restricted, or region-blocked)"})

            # Metadata
            metadata = {
                "video_id": video_id,
                "title": info.get("title"),
                "description": info.get("description"),
                "channel_name": info.get("uploader"),
                "channel_id": info.get("channel_id"),
                "publish_date": info.get("upload_date"),
                "duration": info.get("duration"),
                "views": info.get("view_count"),
                "likes": info.get("like_count"),
                "tags": info.get("tags", []),
                "category": info.get("categories", [''])[0] if info.get("categories") else None,
                "thumbnail": info.get("thumbnail"),
                "live_status": info.get("live_status") == "is_live",
                "language": info.get("language") or info.get("default_language")
            }

            # सभी unique resolutions के साथ formats
            formats = []
            seen_resolutions = set()
            for f in info.get("formats", []):
                if f.get("vcodec") != "none":  # वीडियो वाला format
                    resolution = f.get("resolution")
                    if not resolution or resolution == "none":
                        height = f.get("height")
                        if height:
                            resolution = f"{height}p"
                        else:
                            resolution = "unknown"
                    # केवल unique resolutions रखें (पहली बार जो मिला वही लें)
                    if resolution in seen_resolutions:
                        continue
                    seen_resolutions.add(resolution)

                    filesize = f.get("filesize") or f.get("filesize_approx")
                    # डाउनलोड लिंक – इसमें key और video_id, itag शामिल करें
                    download_link = (
                        f"/download?key={key}&video_id={video_id}&itag={f['format_id']}"
                    )
                    formats.append({
                        "itag": f["format_id"],
                        "resolution": resolution,
                        "fps": f.get("fps"),
                        "filesize": filesize,
                        "ext": f["ext"],
                        "format_note": f.get("format_note", ""),
                        "download_url": download_link
                    })

            # सॉर्ट – 144p से 2160p तक
            def sort_key(f):
                res = f["resolution"]
                if res and "p" in res:
                    try:
                        return int(res.split("p")[0])
                    except:
                        pass
                return 0
            formats.sort(key=sort_key)

            response_data = {
                "metadata": metadata,
                "formats": formats
            }

            # clean_response (यदि आपके core में कोई विशेष क्लीनिंग हो तो)
            # यहाँ हम सीधे send_response कर रहे हैं, लेकिन अगर clean_response चाहिए तो उसे call कर सकते हैं।
            # उदाहरण: cleaned = clean_response(response_data)
            # return send_response("success", cleaned, {...})
            return send_response("success", response_data, {
                "user": user["name"],
                "input_url": url,
                "video_id": video_id
            })

    except Exception as e:
        error_msg = str(e)
        if "Sign in to confirm your age" in error_msg:
            return send_response("error", {}, {"message": "Age-restricted video. Provide cookies."})
        elif "This video is not available" in error_msg:
            return send_response("error", {}, {"message": "Video unavailable"})
        return send_response("error", {}, {"message": f"Internal error: {error_msg}"})

# ---------- डाउनलोड एंडपॉइंट (key + video_id + itag) ----------
@ytdownloader_bp.route("/download", methods=["GET"])
def download_video():
    key = request.args.get("key", "")
    video_id = request.args.get("video_id")
    itag = request.args.get("itag")

    # Access check
    user, err = check_access(key)
    if err:
        return err

    if not video_id or not itag:
        return send_response("error", {}, {"message": "Missing video_id or itag"})

    url = f"https://youtu.be/{video_id}"

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "format": itag,
        "outtmpl": "%(title)s.%(ext)s",
        "ignoreerrors": True,
        "retries": 5,
        "fragment_retries": 5,
        "verbose": False,
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
            # अगर filename exact न मिले तो ढूँढें
            if not os.path.exists(filename):
                for f in os.listdir("."):
                    if f.startswith(info.get("title", "")):
                        filename = f
                        break

            if not os.path.exists(filename):
                return send_response("error", {}, {"message": "File not found after download"})

            # Absolute path बनाकर send करें
            abs_path = os.path.join(temp_dir, filename)
            return send_file(abs_path, as_attachment=True)

    except Exception as e:
        error_msg = str(e)
        if "Sign in to confirm your age" in error_msg:
            return send_response("error", {}, {"message": "Age-restricted video"})
        elif "This video is not available" in error_msg:
            return send_response("error", {}, {"message": "Video unavailable"})
        return send_response("error", {}, {"message": f"Download error: {error_msg}"})
    finally:
        os.chdir(original_cwd)
        shutil.rmtree(temp_dir, ignore_errors=True)