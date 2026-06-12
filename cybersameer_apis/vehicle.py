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

    api1 = clean_response(fetch_api(f"https://reseller-host.vercel.app/api/rc?number={rc}") or {})
    api2 = clean_response(fetch_api(f"https://api.b77bf911.workers.dev/vehicle?registration={rc}") or {})
    api3 = clean_response(fetch_api(f"https://vvvin-ng.vercel.app/lookup?rc={rc}") or {})
    api4 = clean_response(fetch_api(f"https://vehicle-infoo.vercel.app/?rc_number={rc}") or {})

    sources = {k: v for k, v in {
        "reseller_host": api1,
        "worker_api":    api2,
        "vvvin_api":     api3,
        "vehicle_info":  api4
    }.items() if v}

    if not sources:
        return send_response("error", {}, {"message": "No data found"})

    return send_response("success", {
        "rc_number":     rc,
        "total_sources": len(sources),
        "sources":       sources
    }, {"user": user["name"]})
