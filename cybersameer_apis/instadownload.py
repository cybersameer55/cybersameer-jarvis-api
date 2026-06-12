"""
@api /instadownload
@method GET
@param url
@usage /instadownload?key=YOUR_API_KEY&url=INSTAGRAM_LINK
"""

from flask import Blueprint, request
from urllib.parse import quote
from core import check_access, clean_response, fetch_api, send_response

instadownload_bp = Blueprint("instadownload", __name__)


@instadownload_bp.route("/instadownload")
def instadownload():
    key = request.args.get("key", "")
    url = request.args.get("url", "")

    user, err = check_access(key)
    if err:
        return err

    if not url:
        return send_response("error", {}, {"message": "URL required"})

    data = fetch_api(f"https://instadownload.ytansh038.workers.dev/?url={quote(url)}")

    if not data:
        return send_response("error", {}, {"message": "API failed"})

    data = clean_response(data)

    if not data:
        return send_response("error", {}, {"message": "No data found"})

    return send_response("success", data, {
        "user":      user["name"],
        "input_url": url
    })
