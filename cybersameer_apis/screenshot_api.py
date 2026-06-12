"""
@api /screenshot
@method GET
@param url, width (optional), height (optional)
@usage /screenshot?key=YOUR_API_KEY&url=https://google.com
"""

from flask import Blueprint, request
from urllib.parse import quote
from core import check_access, clean_response, fetch_api, send_response

screenshot_bp = Blueprint("screenshot_api", __name__)


@screenshot_bp.route("/screenshot")
def screenshot():
    key    = request.args.get("key", "")
    url    = request.args.get("url", "")
    width  = request.args.get("width", "1280")
    height = request.args.get("height", "720")

    user, err = check_access(key)
    if err:
        return err

    if not url:
        return send_response("error", {}, {"message": "URL required"})

    u = quote(url)

    sc1 = f"https://api.pikwy.com/screenshot?url={u}&width={width}&height={height}&type=png"
    sc2 = f"https://mini.s-shot.ru/{width}x{height}/PNG/1024/Z1/?{url}"
    sc3 = f"https://api.microlink.io/?url={u}&screenshot=true&meta=false&embed=screenshot.url"

    api3 = clean_response(fetch_api(f"https://api.microlink.io/?url={u}&screenshot=true&meta=false") or {})

    return send_response("success", {
        "url":          url,
        "width":        width,
        "height":       height,
        "screenshot_1": sc1,
        "screenshot_2": sc2,
        "microlink":    api3
    }, {"user": user["name"]})
