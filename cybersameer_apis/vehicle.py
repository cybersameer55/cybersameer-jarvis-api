"""
@api /vehicle
@method GET
@param rc
@usage /vehicle?key=YOUR_API_KEY&rc=MH12AB1234
"""

from flask import Blueprint, request
from core import check_access, clean_response, fetch_api, send_response

vehicle_bp = Blueprint("vehicle", __name__)


@vehicle_bp.route("/vehicle")
def vehicle():
    key = request.args.get("key", "")
    rc  = request.args.get("rc", "")

    user, err = check_access(key)
    if err:
        return err

    if not rc:
        return send_response("error", {}, {"message": "RC required"})

    # Existing APIs
    api1 = clean_response(fetch_api(f"https://reseller-host.vercel.app/api/rc?number={rc}") or {})
    api2 = clean_response(fetch_api(f"https://api.b77bf911.workers.dev/vehicle?registration={rc}") or {})
    api3 = clean_response(fetch_api(f"https://vvvin-ng.vercel.app/lookup?rc={rc}") or {})
    api4 = clean_response(fetch_api(f"https://vehicle-infoo.vercel.app/?rc_number={rc}") or {})

    # 🆕 New APIs
    api5 = clean_response(fetch_api(f"https://ft-osint-api.duckdns.org/api/vehicle?key=freetill1&vehicle={rc}") or {})
    api6 = clean_response(fetch_api(f"https://ft-osint-api.duckdns.org/api/veh2num?key=freetill1&vehicle={rc}") or {})
    api7 = clean_response(fetch_api(f"https://ft-osint-api.duckdns.org/api/challan?key=freetill1&vehicle={rc}") or {})
    api8 = clean_response(fetch_api(f"https://rc-x.paskhinpf9.workers.dev/?vehicle={rc}") or {})
    api9 = clean_response(fetch_api(f"https://parivahan-x.paskhinpf9.workers.dev/?vehicle={rc}") or {})

    sources = {k: v for k, v in {
        "reseller_host":    api1,
        "worker_api":       api2,
        "vvvin_api":        api3,
        "vehicle_info":     api4,
        "ft_vehicle":       api5,
        "ft_veh2num":       api6,
        "ft_challan":       api7,
        "rc_x":             api8,
        "parivahan_x":      api9
    }.items() if v}

    if not sources:
        return send_response("error", {}, {"message": "No data found"})

    return send_response("success", {
        "rc_number":     rc,
        "total_sources": len(sources),
        "sources":       sources
    }, {"user": user["name"]})