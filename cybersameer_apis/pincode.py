"""
@api /pincode
@method GET
@param pin
@usage /pincode?key=YOUR_API_KEY&pin=110001
"""

from flask import Blueprint, request
from core import check_access, clean_response, fetch_api, send_response

pincode_bp = Blueprint("pincode", __name__)


@pincode_bp.route("/pincode")
def pincode():
    key = request.args.get("key", "")
    pin = request.args.get("pin", "")

    user, err = check_access(key)
    if err:
        return err

    if not pin:
        return send_response("error", {}, {"message": "Pincode required"})

    api_list = [
        f"https://api.postalpincode.in/pincode/{pin}",
        f"https://api.zippopotam.us/in/{pin}",
        f"http://api.zippopotam.us/IN/{pin}",
        f"https://api.bigdatacloud.net/data/reverse-geocode-client?localityLanguage=en&postalCode={pin}",
        f"https://nominatim.openstreetmap.org/search?postalcode={pin}&country=India&format=json",
        f"https://nominatim.openstreetmap.org/search?q={pin}%20India&format=json",
        f"http://www.postalpincode.in/api/pincode/{pin}",
        f"https://pincodesinfo.in/api/pincode/{pin}",
        f"https://api.sthan.io/AutoComplete/India/PinCode/{pin}",
        f"https://pincode-base-address.vercel.app/api/getBaseAddress/{pin}"
    ]

    results = {}
    for count, url in enumerate(api_list, 1):
        data  = fetch_api(url)
        clean = clean_response(data) if data else {}
        if not clean:
            clean = {"status": "failed", "message": "No data / blocked API"}
        results[f"result_{count}"] = clean

    return send_response("success", {
        "pincode":       pin,
        "total_results": len(results),
        "results":       results
    }, {"user": user["name"]})
