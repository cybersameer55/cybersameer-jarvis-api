"""
@api /alldownloader
@method GET
@param url
@usage /alldownloader?key=YOUR_API_KEY&url=POST_LINK
"""

from flask import Blueprint, request
from urllib.parse import quote
from core import check_access, clean_response, fetch_api, send_response

alldownloader_bp = Blueprint("alldownloader", __name__)


@alldownloader_bp.route("/alldownloader")
def alldownloader():
    key = request.args.get("key", "")
    url = request.args.get("url", "")

    user, err = check_access(key)
    if err:
        return err

    if not url:
        return send_response("error", {}, {"message": "URL required"})

    api1 = clean_response(fetch_api(f"https://ansh-apis.is-dev.org/api/social-downloader?key=ansh&url={quote(url)}") or {})
    api2 = clean_response(fetch_api(f"https://instadownload.ytansh038.workers.dev/?url={quote(url)}") or {})

    if not api1 and not api2:
        return send_response("error", {}, {"message": "No data found"})

    return send_response("success", {
        "input_url": url,
        "social_downloader": api1,
        "insta_downloader": api2
    }, {"user": user["name"]})
