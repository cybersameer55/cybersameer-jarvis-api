"""
@api /github
@method GET
@param username
@usage /github?key=YOUR_API_KEY&username=torvalds
"""

from flask import Blueprint, request
from urllib.parse import quote
from core import check_access, clean_response, fetch_api, send_response

github_bp = Blueprint("github", __name__)


@github_bp.route("/github")
def github():
    key      = request.args.get("key", "")
    username = request.args.get("username", "")

    user, err = check_access(key)
    if err:
        return err

    if not username:
        return send_response("error", {}, {"message": "Username required"})

    u = quote(username)

    profile = clean_response(fetch_api(f"https://api.github.com/users/{u}") or {})
    repos   = clean_response(fetch_api(f"https://api.github.com/users/{u}/repos?per_page=10&sort=stars") or {})
    events  = clean_response(fetch_api(f"https://api.github.com/users/{u}/events/public?per_page=5") or {})

    if not profile:
        return send_response("error", {}, {"message": "GitHub user not found"})

    return send_response("success", {
        "username":    username,
        "profile":     profile,
        "top_repos":   repos,
        "recent_activity": events
    }, {"user": user["name"]})
