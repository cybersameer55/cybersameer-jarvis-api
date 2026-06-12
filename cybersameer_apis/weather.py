"""
@api /weather
@method GET
@param city
@usage /weather?key=YOUR_API_KEY&city=Delhi
"""

from flask import Blueprint, request
from urllib.parse import quote
from core import check_access, clean_response, fetch_api, send_response, get_time_now

weather_bp = Blueprint("weather", __name__)


@weather_bp.route("/weather")
def weather():
    key  = request.args.get("key", "")
    city = request.args.get("city", "")

    user, err = check_access(key)
    if err:
        return err

    if not city:
        return send_response("error", {}, {"message": "City name required"})

    c = quote(city)

    api1 = clean_response(fetch_api(f"https://wttr.in/{c}?format=j1") or {})
    api2 = clean_response(fetch_api(f"https://api.weatherapi.com/v1/current.json?key=free&q={c}") or {})
    api3 = clean_response(fetch_api(f"https://geocoding-api.open-meteo.com/v1/search?name={c}&count=1") or {})

    geo = None
    if api3 and isinstance(api3.get("results"), list) and api3["results"]:
        r = api3["results"][0]
        lat, lon = r.get("latitude"), r.get("longitude")
        if lat and lon:
            geo = clean_response(fetch_api(
                f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
                f"&current_weather=true&hourly=temperature_2m,relativehumidity_2m,windspeed_10m"
            ) or {})

    if not api1 and not geo:
        return send_response("error", {}, {"message": "No weather data found"})

    return send_response("success", {
        "city":          city,
        "time":          get_time_now(),
        "wttr_data":     api1,
        "open_meteo":    geo,
        "weather_api":   api2
    }, {"user": user["name"]})
