"""
@api /freefire
@method GET
@param uid
@usage /freefire?key=YOUR_API_KEY&uid=5706927797
"""

from flask import Blueprint, request
from urllib.parse import quote
from core import check_access, clean_response, fetch_api, send_response, get_time_now

freefire_bp = Blueprint("freefire", __name__)


@freefire_bp.route("/freefire")
def freefire():
    key = request.args.get("key", "")
    uid = request.args.get("uid", "")

    user, err = check_access(key)
    if err:
        return err

    if not uid:
        return send_response("error", {}, {"message": "UID required"})

    api1 = clean_response(fetch_api(f"https://anku-ffapi-inky.vercel.app/ff?uid={quote(uid)}") or {})
    api2 = clean_response(fetch_api(f"https://mafuuuu-info-api.vercel.app/mafu-info?uid={quote(uid)}") or {})
    api3 = clean_response(fetch_api(f"https://anon-ff-info.vercel.app/info?key=76temp&uid={quote(uid)}") or {})

    if not api1 and not api2 and not api3:
        return send_response("error", {}, {"message": "No data found"})

    return send_response("success", {
        "uid": uid,
        "time": get_time_now(),
        "sameer_lookup": {
            "results_1": api1,
            "results_2": api2,
            "results_3": api3
        }
    }, {"user": user["name"]})