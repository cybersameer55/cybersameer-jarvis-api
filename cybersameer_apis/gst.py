"""
@api /gst
@method GET
@param query
@usage /gst?key=YOUR_API_KEY&query=GSTIN_OR_NAME_OR_PAN
"""

import re
from flask import Blueprint, request
from urllib.parse import quote
from core import check_access, clean_response, fetch_api, send_response, get_time_now

gst_bp = Blueprint("gst", __name__)


@gst_bp.route("/gst")
def gst():
    key   = request.args.get("key", "")
    query = request.args.get("query", "")

    user, err = check_access(key)
    if err:
        return err

    if not query:
        return send_response("error", {}, {"message": "Query required"})

    qtype = "name"
    if re.match(r"^\d{2}[A-Z]{5}\d{4}[A-Z][1-9A-Z]{1}Z[0-9A-Z]{1}$", query.upper()):
        qtype = "gstin"
    elif re.match(r"^[A-Z]{5}\d{4}[A-Z]{1}$", query.upper()):
        qtype = "pan"

    q = quote(query)
    billing = gstin_adv = gstin_basic = name_api = pan_api = {}

    if qtype == "gstin":
        billing     = clean_response(fetch_api(f"https://anon-gst-info.vercel.app/advanced/billing?key=temp114&financial_year=2025-26&gstin={q}") or {})
        gstin_adv   = clean_response(fetch_api(f"https://anon-gst-info.vercel.app/advanced/gstin?key=temp114&gstin={q}") or {})
        gstin_basic = clean_response(fetch_api(f"https://anon-gst-info.vercel.app/gstin?gstin={q}&key=anon404") or {})
    elif qtype == "name":
        name_api = clean_response(fetch_api(f"https://anon-gst-info.vercel.app/advanced/name?key=temp114&name={q}") or {})
    elif qtype == "pan":
        pan_api  = clean_response(fetch_api(f"https://anon-gst-info.vercel.app/pan?pan={q}&key=anon404") or {})

    if not billing and not name_api and not gstin_adv and not gstin_basic and not pan_api:
        return send_response("error", {}, {"message": "No data found"})

    return send_response("success", {
        "input": query,
        "type":  qtype,
        "time":  get_time_now(),
        "sameer_lookup": {
            "gstin_data":   {"advanced": gstin_adv, "basic": gstin_basic},
            "billing_info": billing,
            "name_search":  name_api,
            "pan_to_gstin": pan_api
        }
    }, {"user": user["name"]})
