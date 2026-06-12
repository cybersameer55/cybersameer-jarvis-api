"""
@api /calltracer
@method GET
@param number
@usage /calltracer?key=YOUR_API_KEY&number=PHONE_NUMBER
"""

from flask import Blueprint, request
from urllib.parse import quote
from core import check_access, clean_response, fetch_api, send_response

calltracer_bp = Blueprint("calltracer", __name__)


@calltracer_bp.route("/calltracer")
def calltracer():
    key    = request.args.get("key", "")
    number = request.args.get("number", "")

    user, err = check_access(key)
    if err:
        return err

    if not number:
        return send_response("error", {}, {"message": "Phone number required"})

    data = fetch_api(f"https://calltracerinfoapi.vercel.app/api?number={quote(number)}")

    if not data:
        return send_response("error", {}, {"message": "API failed"})

    data = clean_response(data)

    if not data:
        return send_response("error", {}, {"message": "No data found"})

    return send_response("success", data, {
        "user": user["name"],
        "input_number": number
    })
