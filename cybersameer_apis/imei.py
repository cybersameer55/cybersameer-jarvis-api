"""
@api /imei
@method GET
@param imei
@usage /imei?key=YOUR_API_KEY&imei=IMEI_NUMBER
"""

from flask import Blueprint, request
from urllib.parse import quote
from core import check_access, clean_response, fetch_api, send_response, get_time_now

imei_bp = Blueprint("imei", __name__)


def find_device(data):
    if not isinstance(data, dict):
        return ""
    for k in ["model", "device", "phone", "name", "product"]:
        if data.get(k):
            return data[k]
    for v in data.values():
        if isinstance(v, dict):
            res = find_device(v)
            if res:
                return res
    return ""


@imei_bp.route("/imei")
def imei():
    key      = request.args.get("key", "")
    imei_num = request.args.get("imei", "")

    user, err = check_access(key)
    if err:
        return err

    if not imei_num:
        return send_response("error", {}, {"message": "IMEI required"})

    api1 = clean_response(fetch_api(f"https://ng-imei-info.vercel.app/?imei_num={imei_num}") or {})
    api2 = clean_response(fetch_api(f"https://anon-phone-specs.vercel.app/imei?key=temp1104&imei={imei_num}") or {})
    api3 = clean_response(fetch_api(f"https://anon-phone-specs.vercel.app/imei?key=temp1104&imei={imei_num}&extra=true") or {})

    device = ""
    try:
        device = api2["response"]["data"][0]["specs"]["Phone Name"]
    except (KeyError, IndexError, TypeError):
        pass

    if not device:
        device = find_device(api1)
    if not device:
        device = find_device(api3)

    specs = {}
    try:
        specs = api2["response"]["data"][0]["specs"]
    except (KeyError, IndexError, TypeError):
        pass

    if not specs and device:
        specs = clean_response(fetch_api(f"https://anon-phone-specs.vercel.app/specs?key=temp1104&phone={quote(device)}") or {})

    if not api1 and not api2 and not api3:
        return send_response("error", {}, {"message": "No data found"})

    return send_response("success", {
        "input_imei": imei_num,
        "time":       get_time_now(),
        "sameer_lookup": {
            "results_1":   api1,
            "results_2":   api2,
            "results_3":   api3,
            "device_name": device,
            "device_specs": specs
        }
    }, {"user": user["name"]})
