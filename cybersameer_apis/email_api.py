"""
@api /email
@method GET
@param mail
@usage /email?key=YOUR_API_KEY&mail=example@gmail.com
"""

import re
from flask import Blueprint, request
from urllib.parse import quote
from core import check_access, clean_response, fetch_api, send_response, make_list, get_time_now

email_bp = Blueprint("email_api", __name__)


@email_bp.route("/email")
def email():
    key  = request.args.get("key", "")
    mail = request.args.get("mail", "")

    user, err = check_access(key)
    if err:
        return err

    if not mail:
        return send_response("error", {}, {"message": "Email required"})

    if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", mail):
        return send_response("error", {}, {"message": "Invalid email format"})

    api1 = clean_response(fetch_api(f"https://rohitemailapi.vercel.app/info?mail={quote(mail)}") or {})
    api2 = clean_response(fetch_api(f"https://anon-email-info.vercel.app/email?key=tempe124&email={quote(mail)}") or {})

    if not api1 and not api2:
        return send_response("error", {}, {"message": "No data found"})

    return send_response("success", {
        "input_email": mail,
        "time": get_time_now(),
        "sameer_lookup": {
            "results_1": make_list(api1),
            "results_2": make_list(api2)
        }
    }, {"user": user["name"]})
