"""
@api /pan
@method GET
@param pan
@usage /pan?key=YOUR_API_KEY&pan=AAYFK4129N
"""

import re
from flask import Blueprint, request
from urllib.parse import quote
from core import check_access, clean_response, fetch_api, send_response, get_time_now

pan_bp = Blueprint("pan", __name__)


@pan_bp.route("/pan")
def pan():
    key     = request.args.get("key", "")
    pan_val = request.args.get("pan", "").upper()

    user, err = check_access(key)
    if err:
        return err

    if not pan_val:
        return send_response("error", {}, {"message": "PAN required"})

    if not re.match(r"^[A-Z]{5}\d{4}[A-Z]{1}$", pan_val):
        return send_response("error", {}, {"message": "Invalid PAN format"})

    api = fetch_api(f"https://anon-gst-info.vercel.app/advanced/pan?key=temp114&pan={quote(pan_val)}")
    api = clean_response(api)

    if not api:
        return send_response("error", {}, {"message": "No data found"})

    return send_response("success", {
        "input_pan": pan_val,
        "time":      get_time_now(),
        "result":    api
    }, {"user": user["name"]})
