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

    n    = quote(num_val)

    api1 = clean_response(fetch_api(f"https://cyber-osint-num-infos.vercel.app/api/numinfo?key=Anonymous&num={n}") or {})
    api2 = clean_response(fetch_api(f"https://api.b77bf911.workers.dev/mobile?number={n}") or {})
    api3 = clean_response(fetch_api(f"https://anon-num-info.vercel.app/name?key=temp114&num={n}") or {})
    api4 = clean_response(fetch_api(f"https://anon-num-info.vercel.app/num?key=temp094&num={n}") or {})
    api5 = clean_response(fetch_api(f"https://techvishalboss.com/api/v1/lookup.php?key=TVB_FULL_52F4672E&service=number&number={n}") or {})

    # ✅ NEW API ADDED
    api6 = clean_response(fetch_api(
        f"https://cyber-osint-num-infos.vercel.app/api/numinfo?key=Anupkumar-h4ck-₹₹-ig=anon_xploit&num={n}"
    ) or {})

    if not api1 and not api2 and not api3 and not api4 and not api5 and not api6:
        return send_response("error", {}, {"message": "No data found"})

    return send_response("success", {
        "input_number": num_val,
        "time": get_time_now(),
        "sameer_lookup": {
            "results_1": make_list(api3),
            "results_2": make_list(api1),
            "results_3": make_list(api2),
            "results_4": make_list(api4),
            "results_5": make_list(api5),
            "results_6": make_list(api6)
        }
    }, {"user": user["name"]})