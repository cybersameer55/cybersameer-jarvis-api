"""
@api /tginfo
@method GET
@param iduser
@usage /tginfo?key=YOUR_API_KEY&iduser=USER_ID_OR_USERNAME
"""

from flask import Blueprint, request
from urllib.parse import quote
from core import check_access, clean_response, fetch_api, send_response, get_time_now

tginfo_bp = Blueprint("tginfo", __name__)


def format_tg(data):
    if not data:
        return {}
    return {
        "id":          data.get("id") or data.get("user_id", ""),
        "username":    data.get("username", ""),
        "name":        data.get("name") or data.get("first_name", ""),
        "phone":       data.get("phone", ""),
        "bio":         data.get("bio", ""),
        "profile_pic": data.get("profile_pic", ""),
        "extra":       data
    }


@tginfo_bp.route("/tginfo")
def tginfo():
    key    = request.args.get("key", "")
    iduser = request.args.get("iduser", "")

    user, err = check_access(key)
    if err:
        return err

    if not iduser:
        return send_response("error", {}, {"message": "iduser required"})

    is_id = iduser.isdigit()
    u     = quote(iduser)

    api1 = api2 = api3 = api4 = {}

    if is_id:
        api1 = clean_response(fetch_api(f"https://api.b77bf911.workers.dev/telegram?user={u}") or {})
        api2 = clean_response(fetch_api(f"https://cyber-osint-tg-num.vercel.app/api/tginfo?key=Trail5&id={u}") or {})
    else:
        api3 = clean_response(fetch_api(f"https://anon-tg-info.vercel.app/telegram?key=temp104&username={u}") or {})

    # 🆕 NEW API (works for both id and username)
    api4 = clean_response(fetch_api(f"https://telegram-info-plum.vercel.app/api/search?q={u}") or {})

    data1 = format_tg(api1)
    data2 = format_tg(api2)
    data3 = format_tg(api3)
    data4 = format_tg(api4)

    if not data1 and not data2 and not data3 and not data4:
        return send_response("error", {}, {"message": "No data found"})

    return send_response("success", {
        "input": iduser,
        "type":  "id" if is_id else "username",
        "time":  get_time_now(),
        "sameer_lookup": {
            "results_1": data1,
            "results_2": data2,
            "results_3": data3,
            "results_4": data4
        }
    }, {"user": user["name"]})