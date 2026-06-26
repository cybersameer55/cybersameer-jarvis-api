"""
@api /bin
@method GET
@param bin (first 6-8 digits of card)
@usage /bin?key=YOUR_API_KEY&bin=411111
"""

from flask import Blueprint, request
from urllib.parse import quote
from core import check_access, clean_response, fetch_api, send_response, get_time_now

bin_bp = Blueprint("bin_checker", __name__)


@bin_bp.route("/bin")
def bin_check():
    key = request.args.get("key", "")
    bin_ = request.args.get("bin", "")

    user, err = check_access(key)
    if err:
        return err

    if not bin_ or not bin_.isdigit() or len(bin_) < 6:
        return send_response("error", {}, {"message": "Valid BIN (6-8 digits) required"})

    b = bin_[:8]

    api1 = clean_response(fetch_api(f"https://lookup.binlist.net/{b}") or {})
    api2 = clean_response(fetch_api(f"https://api.bincodes.com/bin/?format=json&api_key=free&bin={b}") or {})

    if not api1 and not api2:
        return send_response("error", {}, {"message": "BIN not found"})

    return send_response("success", {
        "bin":      b,
        "time":     get_time_now(),
        "binlist":  api1,
        "bincodes": api2
    }, {"user": user["name"]})
