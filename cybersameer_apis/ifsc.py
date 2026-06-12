"""
@api /ifsc
@method GET
@param code
@usage /ifsc?key=YOUR_API_KEY&code=SBIN0001234
"""

from flask import Blueprint, request
from urllib.parse import quote
from core import check_access, clean_response, fetch_api, send_response

ifsc_bp = Blueprint("ifsc", __name__)


@ifsc_bp.route("/ifsc")
def ifsc():
    key  = request.args.get("key", "")
    code = request.args.get("code", "")

    user, err = check_access(key)
    if err:
        return err

    if not code:
        return send_response("error", {}, {"message": "IFSC code required"})

    data = fetch_api(f"https://api.b77bf911.workers.dev/ifsc?code={quote(code)}")

    if not data:
        return send_response("error", {}, {"message": "API failed"})

    data = clean_response(data)

    if not data:
        return send_response("error", {}, {"message": "No data found"})

    return send_response("success", data, {
        "user":       user["name"],
        "input_ifsc": code
    })
