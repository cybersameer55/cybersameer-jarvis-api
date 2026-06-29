"""
@api /aadhar
@method GET
@param id
@usage /aadhar?key=YOUR_API_KEY&id=XXXXXXXXXXXX
"""

import re
from flask import Blueprint, request
from core import check_access, clean_response, fetch_api, send_response, get_time_now

aadhar_bp = Blueprint("aadhar", __name__)


@aadhar_bp.route("/aadhar")
def aadhar():
    key = request.args.get("key", "")
    id_ = request.args.get("id", "")

    user, err = check_access(key)
    if err:
        return err

    if not id_:
        return send_response("error", {}, {"message": "Aadhar number required"})

    if not re.match(r"^\d{12}$", id_):
        return send_response("error", {}, {"message": "Invalid Aadhar format"})

    # 🔁 API REPLACED with new key
    api = fetch_api(f"https://anon-num-info.vercel.app/aadhar?key=2060adr&id={id_}")
    api = clean_response(api)

    if not api:
        return send_response("error", {}, {"message": "No data found"})

    return send_response("success", {
        "input_aadhar": id_,
        "time": get_time_now(),
        "result": api
    }, {"user": user["name"]})