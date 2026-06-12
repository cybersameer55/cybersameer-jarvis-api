"""
@api /nasa
@method GET
@param date (optional, YYYY-MM-DD)
@usage /nasa?key=YOUR_API_KEY&date=2024-01-01
"""

from flask import Blueprint, request
from core import check_access, clean_response, fetch_api, send_response, get_time_now

nasa_bp = Blueprint("nasa", __name__)

NASA_KEY = "DEMO_KEY"


@nasa_bp.route("/nasa")
def nasa():
    key  = request.args.get("key", "")
    date = request.args.get("date", "")

    user, err = check_access(key)
    if err:
        return err

    date_param = f"&date={date}" if date else ""

    apod    = clean_response(fetch_api(f"https://api.nasa.gov/planetary/apod?api_key={NASA_KEY}{date_param}") or {})
    mars    = clean_response(fetch_api(f"https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos?sol=1000&api_key={NASA_KEY}&page=1") or {})
    neo     = clean_response(fetch_api(f"https://api.nasa.gov/neo/rest/v1/feed/today?api_key={NASA_KEY}") or {})

    if not apod:
        return send_response("error", {}, {"message": "No NASA data found"})

    return send_response("success", {
        "date":          date or get_time_now()[:10],
        "apod":          apod,
        "mars_photos":   mars,
        "near_earth":    neo
    }, {"user": user["name"]})
