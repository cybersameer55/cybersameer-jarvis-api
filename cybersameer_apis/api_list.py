"""
@api /api-list
@method GET
@usage /api-list?key=YOUR_API_KEY
"""

import os
import ast
import json
from flask import Blueprint, request, current_app, Response
from core import DEVELOPER, check_access
from datetime import datetime

api_list_bp = Blueprint("api_list", __name__)

# Routes listed here appear first (in this order).
# All other registered routes appear after, sorted alphabetically.
# This list does NOT control which APIs are active — that is fully automatic.
# If a route here no longer exists it is silently skipped.
PRIORITY = [
    # India / Lookup
    "/num", "/calltracer", "/truecaller", "/pakistan",
    "/aadhar", "/pan", "/gst", "/ifsc", "/imei", "/pincode",
    "/vehicle", "/vehicletype",
    "/upi", "/state", "/isd", "/inrupees",
    # Gaming
    "/freefire", "/bgmi", "/emotes",
    # Downloaders
    "/alldownloader", "/instadownload", "/ytdownloader", "/terabox",
    # Social Media
    "/instagram", "/tginfo", "/github", "/twitter", "/tiktok", "/youtubeinfo",
    # Network / Domain
    "/ipinfo", "/domaininfo", "/whois", "/ssl", "/email", "/bin",
    "/phonevalidate", "/country", "/dns", "/httpstatus",
    # Weather / Environment
    "/weather", "/airquality", "/sun", "/moon", "/earthquake",
    # Finance
    "/crypto", "/currency", "/currencies", "/stock",
    "/emi", "/interest", "/fd", "/sip", "/roi", "/profitloss",
    "/compoundinterest", "/gst_calc", "/percentage", "/discount",
    "/tax", "/vat", "/salary", "/savings", "/inflation", "/breakeven",
    # Info / Data
    "/spacex", "/wikipedia", "/dictionary", "/translate", "/news", "/nasa",
    "/devto", "/hackernews", "/reddit", "/gitrepo", "/gittrending",
    "/covid", "/holiday", "/history", "/astronaut", "/iss",
    "/npm", "/pypi", "/fakedata", "/flag", "/population", "/continent",
    # Utility
    "/base64", "/hash", "/uuid", "/password", "/passphrase", "/username",
    "/otp", "/luhn", "/bmi", "/tip", "/age", "/grade", "/fuel",
    "/electricity", "/speed", "/datediff", "/wordcount", "/wordfreq",
    "/jsoncheck", "/sentiment", "/langdetect",
    "/math", "/numberfact", "/fibonacci", "/prime",
    "/countdown", "/qr1", "/qr2", "/qr3", "/barcode",
    "/screenshot", "/texttools", "/shorturl", "/websitezip", "/tempmail", "/time",
    "/morse", "/binary", "/roman", "/palindrome", "/anagram", "/slug",
    "/nato", "/leet", "/numwords", "/caseconvert", "/rhyme", "/synonym",
    "/tempconv", "/unit", "/timezone", "/element", "/urban", "/emoji",
]

SKIP_ROUTES = {"/", "/home", "/index.html", "/api-list", "/documentation"}


def _scan_docstrings():
    """Scan all .py files in cybersameer_apis/ and extract @api/@param/@usage tags."""
    apis_dir = os.path.dirname(os.path.abspath(__file__))
    mapping = {}
    for fname in sorted(os.listdir(apis_dir)):
        if not fname.endswith(".py") or fname in ("__init__.py", "api_list.py"):
            continue
        try:
            with open(os.path.join(apis_dir, fname), encoding="utf-8") as f:
                source = f.read()
            tree = ast.parse(source)
            ds = ast.get_docstring(tree)
            if not ds:
                continue
            route = params = usage = ""
            for line in ds.splitlines():
                line = line.strip()
                if line.startswith("@api"):     route  = line.replace("@api", "").strip()
                elif line.startswith("@param"):  params = line.replace("@param", "").strip()
                elif line.startswith("@usage"):  usage  = line.replace("@usage", "").strip()
            if route:
                mapping[route] = {"params": params, "usage": usage}
        except Exception:
            pass
    return mapping


def _user_info(user, key):
    expiry = user.get("expiry", "unlimited")
    if expiry == "unlimited":
        return {
            "api_key": key, "name": user["name"], "status": user["status"],
            "expiry": "unlimited", "expiry_status": "Unlimited", "remaining_days": "infinite"
        }
    parts = expiry.split("-")
    exp   = datetime(int(parts[0]), int(parts[1]), int(parts[2]))
    diff  = (exp - datetime.now()).days
    label = "Expired" if diff < 0 else "Expiring Soon" if diff <= 3 else "Active"
    return {
        "api_key": key, "name": user["name"], "status": user["status"],
        "expiry": expiry, "expiry_status": label, "remaining_days": max(0, diff)
    }


@api_list_bp.route("/")
@api_list_bp.route("/api-list")
def api_list():
    key = request.args.get("key", "")
    user, err = check_access(key)
    if err:
        return err

    base_url = request.url_root.rstrip("/")
    doc_map  = _scan_docstrings()

    # Collect every live GET route from Flask's URL map
    all_routes = set()
    for rule in current_app.url_map.iter_rules():
        if "GET" in (rule.methods or []):
            route = str(rule)
            if route not in SKIP_ROUTES and not route.startswith("/static"):
                all_routes.add(route)

    # Priority first, then everything else alphabetically
    priority_routes = [r for r in PRIORITY if r in all_routes]
    remaining       = sorted(all_routes - set(priority_routes))
    ordered         = priority_routes + remaining

    # Build route -> full example URL
    api_dict = {}
    for route in ordered:
        info  = doc_map.get(route, {})
        usage = info.get("usage", "")
        if usage:
            usage = usage.replace("YOUR_API_KEY", key)
            query = usage.split("?", 1)[1] if "?" in usage else f"key={key}"
            full_url = f"{base_url}{route}?{query}"
        else:
            full_url = f"{base_url}{route}?key={key}"
        api_dict[route] = full_url

    result = {
        "status": "success",
        "data": {
            "message": "J.A.R.V.I.S API — Auto-discovered. Add/remove files in cybersameer_apis/ to update.",
            "total_apis": len(api_dict),
            "api_list": api_dict,
        },
        "developer": DEVELOPER,
        "user_info": _user_info(user, key),
    }

    # Use json.dumps (not jsonify) so priority insertion order is preserved
    return Response(
        json.dumps(result, ensure_ascii=False, indent=2),
        mimetype="application/json"
    )
