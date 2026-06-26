"""
@api /tiktok
@method GET
@param username
@usage /tiktok?key=YOUR_API_KEY&username=charlidamelio
"""

from flask import Blueprint, request
from urllib.parse import quote
from core import check_access, clean_response, fetch_api, send_response

tiktok_bp = Blueprint("tiktok", __name__)


@tiktok_bp.route("/tiktok")
def tiktok():
    key      = request.args.get("key", "")
    username = request.args.get("username", "")

    user, err = check_access(key)
    if err:
        return err

    if not username:
        return send_response("error", {}, {"message": "Username required"})

    u = quote(username.lstrip("@"))

    api1 = clean_response(fetch_api(f"https://api.socialcounts.org/tiktok-live-follower-count/{u}") or {})
    api2 = clean_response(fetch_api(f"https://www.tiktok.com/api/user/detail/?uniqueId={u}") or {})

    return send_response("success", {
        "username":      username,
        "social_counts": api1,
        "profile":       api2
    }, {"user": user["name"]})
