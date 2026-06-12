"""
@api /terabox
@method GET
@param url
@usage /terabox?key=YOUR_API_KEY&url=TERABOX_URL
"""

from flask import Blueprint, request
from urllib.parse import quote
from core import check_access, clean_response, fetch_api, send_response

terabox_bp = Blueprint("terabox", __name__)


@terabox_bp.route("/terabox")
def terabox():
    key = request.args.get("key", "")
    url = request.args.get("url", "")

    user, err = check_access(key)
    if err:
        return err

    if not url:
        return send_response("error", {}, {"message": "URL required"})

    u    = quote(url)
    api1 = clean_response(fetch_api(f"https://ansh-apis.is-dev.org/api/terbox?key=ansh&url={u}") or {})
    api2 = clean_response(fetch_api(f"https://terabox.anshapi.workers.dev/api/terabox-down?url={u}") or {})

    if not api1 and not api2:
        return send_response("error", {}, {"message": "No data found"})

    return send_response("success", {
        "input_url": url,
        "source_1":  api1,
        "source_2":  api2
    }, {"user": user["name"]})
