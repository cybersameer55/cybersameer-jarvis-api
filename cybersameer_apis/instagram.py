"""
@api /instagram
@method GET
@param username
@usage /instagram?key=YOUR_API_KEY&username=USERNAME
"""

from flask import Blueprint, request
from urllib.parse import quote
from core import check_access, clean_response, fetch_api, send_response

instagram_bp = Blueprint("instagram", __name__)


@instagram_bp.route("/instagram")
def instagram():
    key      = request.args.get("key", "")
    username = request.args.get("username", "")

    user, err = check_access(key)
    if err:
        return err

    if not username:
        return send_response("error", {}, {"message": "Username required"})

    base = "https://instagraminfo.anshapi.workers.dev"
    u    = quote(username)

    info    = clean_response(fetch_api(f"{base}/info?username={u}") or {})
    posts   = clean_response(fetch_api(f"{base}/posts?username={u}") or {})
    reels   = clean_response(fetch_api(f"{base}/reels?username={u}") or {})
    stories = clean_response(fetch_api(f"{base}/stories?username={u}") or {})

    sources = {k: v for k, v in {
        "info": info, "posts": posts,
        "reels": reels, "stories": stories
    }.items() if v}

    if not sources:
        return send_response("error", {}, {"message": "No data found"})

    return send_response("success", {
        "username":      username,
        "total_sources": len(sources),
        "sources":       sources
    }, {"user": user["name"]})
