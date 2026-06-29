"""
@api /num
@method GET
@param num
@usage /num?key=YOUR_API_KEY&num=PHONE_NUMBER
"""

from flask import Blueprint, request
from urllib.parse import quote
from core import check_access, clean_response, fetch_api, send_response, make_list, get_time_now

num_bp = Blueprint("num", __name__)


@num_bp.route("/num")
def num():
    key     = request.args.get("key", "")
    num_val = request.args.get("num", "")

    user, err = check_access(key)
    if err:
        return err

    if not num_val:
        return send_response("error", {}, {"message": "Phone number required"})

    n = quote(num_val)

    # ---------- 4 APIs (as requested) ----------
    api1 = clean_response(fetch_api(f"https://api.b77bf911.workers.dev/mobile?number={n}") or {})
    api2 = clean_response(fetch_api(f"https://calltracerinfoapi.vercel.app/api?number={n}") or {})
    api3 = clean_response(fetch_api(f"https://ft-osint-api.duckdns.org/api/numleak?key=freetill1&num={n}") or {})
    api4 = clean_response(fetch_api(f"https://anon-num-info.vercel.app/num?key=tnum1906&num={n}") or {})

    # ---------- Check ----------
    if not api1 and not api2 and not api3 and not api4:
        return send_response("error", {}, {"message": "No data found"})

    # ---------- Response ----------
    return send_response("success", {
        "input_number": num_val,
        "time": get_time_now(),
        "sameer_lookup": {
            "api_1": make_list(api1),
            "api_2": make_list(api2),
            "api_3": make_list(api3),
            "api_4": make_list(api4)
        }
    }, {"user": user["name"]})