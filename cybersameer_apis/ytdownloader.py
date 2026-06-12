"""
@api /ytdownloader
@method GET
@param url
@usage /ytdownloader?key=YOUR_API_KEY&url=YOUTUBE_LINK
"""

from flask import Blueprint, request
from urllib.parse import quote
from core import check_access, clean_response, fetch_api, send_response

ytdownloader_bp = Blueprint("ytdownloader", __name__)


@ytdownloader_bp.route("/ytdownloader")
def ytdownloader():
    key = request.args.get("key", "")
    url = request.args.get("url", "")

    user, err = check_access(key)
    if err:
        return err

    if not url:
        return send_response("error", {}, {"message": "YouTube URL required"})

    data = fetch_api(f"https://ytvideownloader.ytansh038.workers.dev/?url={quote(url)}")

    if not data:
        return send_response("error", {}, {"message": "API failed"})

    data = clean_response(data)

    if not data:
        return send_response("error", {}, {"message": "No data found"})

    return send_response("success", data, {
        "user":      user["name"],
        "input_url": url
    })
