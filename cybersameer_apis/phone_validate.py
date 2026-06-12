"""
@api /phonevalidate
@method GET
@param number (with country code), country (optional: IN/US/PK)
@usage /phonevalidate?key=YOUR_API_KEY&number=+919876543210&country=IN
"""

from flask import Blueprint, request
from urllib.parse import quote
from core import check_access, clean_response, fetch_api, send_response, get_time_now

phone_validate_bp = Blueprint("phone_validate", __name__)


@phone_validate_bp.route("/phonevalidate")
def phone_validate():
    key     = request.args.get("key", "")
    number  = request.args.get("number", "")
    country = request.args.get("country", "")

    user, err = check_access(key)
    if err:
        return err

    if not number:
        return send_response("error", {}, {"message": "Phone number required"})

    n = quote(number)
    c = f"&country_code={country}" if country else ""

    api1 = clean_response(fetch_api(f"https://phonevalidate.com/api/v1?phone={n}{c}") or {})
    api2 = clean_response(fetch_api(f"https://api.veriphone.io/v2/verify?phone={n}&key=free") or {})
    api3 = clean_response(fetch_api(f"https://api.numlookupapi.com/v1/info/{n}?apikey=free") or {})

    if not api1 and not api2 and not api3:
        return send_response("error", {}, {"message": "Could not validate number"})

    return send_response("success", {
        "number":      number,
        "time":        get_time_now(),
        "validate_1":  api1,
        "veriphone":   api2,
        "numlookup":   api3
    }, {"user": user["name"]})
