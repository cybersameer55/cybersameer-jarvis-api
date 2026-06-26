"""
@api /webinfo
@method GET
@param domain
@usage /webinfo?key=YOUR_API_KEY&domain=google.com&type=A
"""

from flask import Blueprint, request
from core import check_access, clean_response, fetch_api, send_response, make_list

webinfo_bp = Blueprint("webinfo", __name__)


@webinfo_bp.route("/webinfo")
def webinfo():
    key    = request.args.get("key", "")
    domain = request.args.get("domain", "")
    dtype  = request.args.get("type", "A").upper()

    user, err = check_access(key)
    if err:
        return err

    if not domain:
        return send_response("error", {}, {"message": "Domain required"})

    # 🔥 API 1 (DNS with TYPE support - your requested one)
    api1 = clean_response(fetch_api(
        f"https://dns.google/resolve?name={domain}&type={dtype}"
    ) or {})

    # 🌐 API 2
    api2 = clean_response(fetch_api(
        f"https://dns.google/resolve?name={domain}"
    ) or {})

    # 🌐 API 3
    api3 = clean_response(fetch_api(
        f"https://rdap.org/domain/{domain}"
    ) or {})

    # 🌐 API 4
    api4 = clean_response(fetch_api(
        f"https://urlscan.io/api/v1/search/?q=domain:{domain}"
    ) or {})

    # 🌐 API 5
    api5 = clean_response(fetch_api(
        f"https://app.netlas.io/api/domains/?q={domain}"
    ) or {})

    # 🌐 API 6
    api6 = clean_response(fetch_api(
        f"https://api.microlink.io/?url=https://{domain}"
    ) or {})

    # 🌐 API 7 (VirusTotal)
    api7 = clean_response(fetch_api(
        f"https://www.virustotal.com/api/v3/domains/{domain}",
        headers={"x-apikey": "YOUR_VIRUSTOTAL_API_KEY"}
    ) or {})

    if not api1 and not api2 and not api3 and not api4 and not api5 and not api6 and not api7:
        return send_response("error", {}, {"message": "No data found"})

    return send_response("success", {
        "input_domain": domain,
        "type": dtype,

        "sameer_lookup": {
            "results_1": make_list(api1),
            "results_2": make_list(api2),
            "results_3": make_list(api3),
            "results_4": make_list(api4),
            "results_5": make_list(api5),
            "results_6": make_list(api6),
            "results_7": make_list(api7)
        }
    }, {
        "user": user["name"]
    })