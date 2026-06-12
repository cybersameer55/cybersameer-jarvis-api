"""
@api /countdown
@method GET
@param date (YYYY-MM-DD), label (optional)
@usage /countdown?key=YOUR_API_KEY&date=2025-12-31&label=New+Year
"""

from datetime import datetime, date
from flask import Blueprint, request
from core import check_access, send_response, get_time_now

countdown_bp = Blueprint("countdown", __name__)


@countdown_bp.route("/countdown")
def countdown():
    key   = request.args.get("key", "")
    tdate = request.args.get("date", "")
    label = request.args.get("label", "Event")

    user, err = check_access(key)
    if err:
        return err

    if not tdate:
        return send_response("error", {}, {"message": "date required (YYYY-MM-DD)"})

    try:
        target = datetime.strptime(tdate, "%Y-%m-%d").date()
        today  = date.today()
        diff   = (target - today).days

        hours   = abs(diff) * 24
        minutes = abs(diff) * 24 * 60
        seconds = abs(diff) * 24 * 60 * 60
        weeks   = abs(diff) // 7

        if diff > 0:
            status = "upcoming"
            msg    = f"{diff} days remaining"
        elif diff == 0:
            status = "today"
            msg    = "It's today!"
        else:
            status = "passed"
            msg    = f"{abs(diff)} days ago"

    except Exception:
        return send_response("error", {}, {"message": "Invalid date format. Use YYYY-MM-DD"})

    return send_response("success", {
        "label":         label,
        "target_date":   tdate,
        "today":         str(today),
        "status":        status,
        "message":       msg,
        "days":          diff,
        "weeks":         weeks,
        "hours":         hours,
        "minutes":       minutes,
        "seconds":       seconds,
        "day_of_week":   target.strftime("%A"),
        "time":          get_time_now()
    }, {"user": user["name"]})
