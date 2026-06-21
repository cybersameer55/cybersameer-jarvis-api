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
from flask import Flask, request, send_file, jsonify
import yt_dlp

app = Flask(__name__)

# ---------- SIMPLE API KEY CHECK (example) ----------
VALID_KEYS = {"BHAI": "User"}   # आप और keys जोड़ सकते हैं

def check_access(key):
    if key in VALID_KEYS:
        return {"name": VALID_KEYS[key]}, None
    return None, jsonify({"status": "error", "message": "Invalid API key"}), 401

def send_response(status, data, extra=None):
    response = {"status": status, "data": data}
    if extra:
        response.update(extra)
    return response

# ---------- EXTRACT VIDEO ID FROM ANY YOUTUBE URL ----------
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

# ---------- MAIN ENDPOINT : /ytdownloader ----------
@app.route("/ytdownloader", methods=["GET"])
def ytdownloader():
    key = request.args.get("key", "")
    url = request.args.get("url", "")

    user, err = check_access(key)
    if err:
        return err

    if not url:
        return send_response("error", {}, {"message": "YouTube URL required"})

    if "playlist" in url or "list=" in url:
        return send_response("error", {}, {"message": "Playlist URLs not supported"})

    video_id = extract_video_id(url)
    if not video_id:
        return send_response("error", {}, {"message": "Invalid YouTube URL"})

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": False,
        "ignoreerrors": True,
        "verbose": False,
        "format": "all",
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if info is None:
                return send_response("error", {}, {"message": "Video unavailable"})

            # ----- Metadata -----
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

            # ----- All unique resolutions -----
            formats = []
            seen = set()
            for f in info.get("formats", []):
                if f.get("vcodec") != "none":
                    resolution = f.get("resolution")
                    if not resolution or resolution == "none":
                        height = f.get("height")
                        if height:
                            resolution = f"{height}p"
                        else:
                            resolution = "unknown"
                    if resolution in seen:
                        continue
                    seen.add(resolution)
                    filesize = f.get("filesize") or f.get("filesize_approx")
                    download_link = f"/download?key={key}&video_id={video_id}&itag={f['format_id']}"
                    formats.append({
                        "itag": f["format_id"],
                        "resolution": resolution,
                        "fps": f.get("fps"),
                        "filesize": filesize,
                        "ext": f["ext"],
                        "format_note": f.get("format_note", ""),
                        "download_url": download_link
                    })

            formats.sort(key=lambda x: int(x["resolution"].split("p")[0]) if x["resolution"] and "p" in x["resolution"] else 0)

            return send_response("success", {"metadata": metadata, "formats": formats}, {
                "user": user["name"],
                "input_url": url,
                "video_id": video_id
            })

    except Exception as e:
        error_msg = str(e)
        if "Sign in to confirm your age" in error_msg:
            return send_response("error", {}, {"message": "Age-restricted video"})
        elif "This video is not available" in error_msg:
            return send_response("error", {}, {"message": "Video unavailable"})
        return send_response("error", {}, {"message": f"Internal error: {error_msg}"})

# ---------- DOWNLOAD ENDPOINT (key + video_id + itag) ----------
@app.route("/download", methods=["GET"])
def download_video():
    key = request.args.get("key", "")
    video_id = request.args.get("video_id")
    itag = request.args.get("itag")

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
            if not os.path.exists(filename):
                for f in os.listdir("."):
                    if f.startswith(info.get("title", "")):
                        filename = f
                        break

            if not os.path.exists(filename):
                return send_response("error", {}, {"message": "File not found"})

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

# ---------- HEALTH CHECK (यह भी जोड़ दिया) ----------
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ok", "message": "YouTube Downloader API is running"})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)