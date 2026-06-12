"""
@api /pakistan
@method GET
@param num
@usage /pakistan?key=YOUR_API_KEY&num=923XXXXXXXXX
"""

from flask import Blueprint, request
from urllib.parse import quote
from core import check_access, clean_response, fetch_api, send_response, get_time_now

pakistan_bp = Blueprint("pakistan", __name__)


@pakistan_bp.route("/pakistan")
def pakistan():
    key     = request.args.get("key", "")
    num_val = request.args.get("num", "")

    user, err = check_access(key)
    if err:
        return err

    if not num_val:
        return send_response("error", {}, {"message": "Phone number required"})

    n          = quote(num_val)
    num_api1   = clean_response(fetch_api(f"https://rohit-pakistan-num-info-api.vercel.app/api/lookup?query={n}") or {})
    num_api2   = clean_response(fetch_api(f"https://anon-pak-info.vercel.app/num?key=temp1004&q={n}") or {})
    cnic_api   = clean_response(fetch_api(f"https://anon-pak-info.vercel.app/cnic?key=temp1004&q={n}") or {})
    police_api = clean_response(fetch_api(f"https://anon-pak-info.vercel.app/police?key=temp1004&num={n}") or {})

    if not num_api1 and not num_api2 and not cnic_api and not police_api:
        return send_response("error", {}, {"message": "No data found"})

    return send_response("success", {
        "input_number": num_val,
        "time":         get_time_now(),
        "sameer_lookup": {
            "pakistan_num": {
                "results_1": num_api1,
                "results_2": num_api2
            },
            "pakistan_cnic":   cnic_api,
            "pakistan_police": police_api
        }
    }, {"user": user["name"]})
