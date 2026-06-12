"""
@api /youtubeinfo
@method GET
@param channel (channel name or ID)
@usage /youtubeinfo?key=YOUR_API_KEY&channel=MrBeast
"""

from flask import Blueprint, request
from urllib.parse import quote
from core import check_access, clean_response, fetch_api, send_response

youtube_info_bp = Blueprint("youtube_info", __name__)


@youtube_info_bp.route("/youtubeinfo")
def youtube_info():
    key     = request.args.get("key", "")
    channel = request.args.get("channel", "")

    user, err = check_access(key)
    if err:
        return err

    if not channel:
        return send_response("error", {}, {"message": "Channel name or ID required"})

    c = quote(channel)

    api1 = clean_response(fetch_api(f"https://api.socialcounts.org/youtube-live-subscriber-count/{c}") or {})
    api2 = clean_response(fetch_api(f"https://www.googleapis.com/youtube/v3/channels?part=statistics,snippet&forUsername={c}&key=AIzaSyD-9tSrke72PouQMnMX-a7eZSW0jkFMBWY") or {})

    return send_response("success", {
        "channel":       channel,
        "social_counts": api1,
        "yt_api":        api2
    }, {"user": user["name"]})
