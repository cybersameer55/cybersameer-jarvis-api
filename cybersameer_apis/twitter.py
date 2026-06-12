"""
@api /twitter
@method GET
@param username
@usage /twitter?key=YOUR_API_KEY&username=elonmusk
"""

from flask import Blueprint, request
from urllib.parse import quote
from core import check_access, clean_response, fetch_api, send_response

twitter_bp = Blueprint("twitter", __name__)


@twitter_bp.route("/twitter")
def twitter():
    key      = request.args.get("key", "")
    username = request.args.get("username", "")

    user, err = check_access(key)
    if err:
        return err

    if not username:
        return send_response("error", {}, {"message": "Username required"})

    u = quote(username.lstrip("@"))

    api1 = clean_response(fetch_api(f"https://api.socialcounts.org/twitter-live-follower-count/{u}") or {})
    api2 = clean_response(fetch_api(f"https://api.twitter.com/1.1/users/show.json?screen_name={u}") or {})

    return send_response("success", {
        "username":      username,
        "social_counts": api1,
        "profile":       api2
    }, {"user": user["name"]})
