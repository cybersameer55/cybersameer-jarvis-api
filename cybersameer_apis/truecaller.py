"""
@api /truecaller
@method GET
@param q
@usage /truecaller?key=YOUR_API_KEY&q=PHONE_NUMBER
"""

from flask import Blueprint, request
from urllib.parse import quote
from core import check_access, clean_response, fetch_api, send_response

truecaller_bp = Blueprint("truecaller", __name__)


@truecaller_bp.route("/truecaller")
def truecaller():
    key = request.args.get("key", "")
    q   = request.args.get("q", "")

    user, err = check_access(key)
    if err:
        return err

    if not q:
        return send_response("error", {}, {"message": "Phone number required"})

    data = fetch_api(f"https://ansh-apis.is-dev.org/api/truecaller?key=ansh&q={quote(q)}")

    if not data:
        return send_response("error", {}, {"message": "API failed"})

    data = clean_response(data)

    if not data:
        return send_response("error", {}, {"message": "No data found"})

    return send_response("success", data, {
        "user":         user["name"],
        "input_number": q
    })
