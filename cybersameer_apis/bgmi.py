"""
@api /bgmi
@method GET
@param uid
@usage /bgmi?key=YOUR_API_KEY&uid=YOUR_BGMI_UID
"""

from flask import Blueprint, request
from core import check_access, clean_response, fetch_api, send_response, get_time_now

bgmi_bp = Blueprint("bgmi", __name__)


@bgmi_bp.route("/bgmi")
def bgmi():
    key = request.args.get("key", "")
    uid = request.args.get("uid", "")

    user, err = check_access(key)
    if err:
        return err

    if not uid:
        return send_response("error", {}, {"message": "BGMI UID required"})

    api1 = clean_response(fetch_api(f"https://bgmi-api.vercel.app/bgmi?uid={uid}") or {})
    api2 = clean_response(fetch_api(f"https://pubg-api.vercel.app/uid?uid={uid}") or {})

    if not api1 and not api2:
        return send_response("error", {}, {"message": "No data found for this UID"})

    return send_response("success", {
        "uid":    uid,
        "time":   get_time_now(),
        "bgmi_1": api1,
        "bgmi_2": api2
    }, {"user": user["name"]})
