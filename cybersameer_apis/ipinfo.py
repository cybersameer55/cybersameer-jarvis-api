"""
@api /ipinfo
@method GET
@param ip
@usage /ipinfo?key=YOUR_API_KEY&ip=8.8.8.8
"""

import time
import ipaddress
import requests as req
from flask import Blueprint, request
from core import check_access, clean_response, fetch_api, send_response, get_time_now

ipinfo_bp = Blueprint("ipinfo", __name__)


@ipinfo_bp.route("/ipinfo")
def ipinfo():
    key = request.args.get("key", "")
    ip  = request.args.get("ip", "")

    user, err = check_access(key)
    if err:
        return err

    if not ip:
        try:
            ip = req.get("https://api.ipify.org?format=json", timeout=5).json().get("ip", "")
        except Exception:
            pass

    if not ip:
        return send_response("error", {}, {"message": "IP required"})

    apis = [
        f"http://ip-api.com/json/{ip}",
        f"https://api.ipbase.com/v1/json/{ip}",
        f"https://freeipapi.com/api/json/{ip}",
        f"https://ipinfo.io/{ip}/json",
        f"https://ipapi.co/{ip}/json/",
        f"https://ipwho.is/{ip}",
        f"https://api.ip.sb/geoip/{ip}",
        f"https://api.ipapi.is/?q={ip}",
        f"https://api.hackertarget.com/geoip/?q={ip}",
        f"https://api.db-ip.com/v2/free/{ip}",
        f"https://ipwhois.app/json/{ip}",
        f"https://get.geojs.io/v1/ip/geo/{ip}.json",
        f"https://api.iplocation.net/?ip={ip}",
        f"https://api.seeip.org/geoip/{ip}",
        "https://ipinfo.io/json",
        "https://ipapi.co/json/",
        "https://ipwho.is/",
        "https://api.ip.sb/geoip/",
        "https://api.ipapi.is/?q=",
        f"http://ip-api.com/json/"
    ]

    results = {}
    for count, url in enumerate(apis, 1):
        data = fetch_api(url)
        results[f"result_{count}"] = clean_response(data) if data else {}

    is_private = False
    try:
        is_private = ipaddress.ip_address(ip).is_private
    except Exception:
        pass

    custom = {
        "ip":            ip,
        "version":       "IPv6" if ":" in ip else "IPv4",
        "is_private":    is_private,
        "timestamp":     int(time.time()),
        "server_time":   get_time_now(),
        "total_sources": len(apis)
    }

    return send_response("success", {
        "custom":  custom,
        "results": results
    }, {"user": user["name"]})
