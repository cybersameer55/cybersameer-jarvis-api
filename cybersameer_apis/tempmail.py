"""
@api /tempmail
@method GET
@param action
@usage
  /tempmail?key=YOUR_API_KEY&action=generate
  /tempmail?key=YOUR_API_KEY&action=check&token=SID_TOKEN
"""

from flask import Blueprint, request
from urllib.parse import quote
from core import check_access, clean_response, fetch_api, send_response

tempmail_bp = Blueprint("tempmail", __name__)


@tempmail_bp.route("/tempmail")
def tempmail():
    key    = request.args.get("key", "")
    action = request.args.get("action", "")
    token  = request.args.get("token", "")

    user, err = check_access(key)
    if err:
        return err

    if not action:
        return send_response("error", {}, {"message": "Action required (generate/check)"})

    if action == "generate":
        data = fetch_api("https://api.guerrillamail.com/ajax.php?f=get_email_address")
        if not data:
            return send_response("error", {}, {"message": "Failed to generate email"})
        data = clean_response(data)
        return send_response("success", {
            "email":     data.get("email_addr") if data else None,
            "alias":     data.get("alias") if data else None,
            "token":     data.get("sid_token") if data else None,
            "timestamp": data.get("email_timestamp") if data else None
        }, {"user": user["name"]})

    elif action == "check":
        if not token:
            return send_response("error", {}, {"message": "Token required"})
        data = fetch_api(f"https://api.guerrillamail.com/ajax.php?f=check_email&seq=0&sid_token={quote(token)}")
        if not data:
            return send_response("error", {}, {"message": "Failed to fetch inbox"})
        data = clean_response(data)
        return send_response("success", {
            "email": data.get("email") if data else None,
            "count": data.get("count", 0) if data else 0,
            "mails": data.get("list", []) if data else []
        }, {"user": user["name"]})

    else:
        return send_response("error", {}, {"message": "Invalid action"})
