"""
@api /shorturl
@method GET
@param url
@usage /shorturl?key=YOUR_API_KEY&url=LONG_URL
"""

import requests as req
from flask import Blueprint, request
from urllib.parse import quote
from core import check_access, send_response

shorturl_bp = Blueprint("shorturl", __name__)


@shorturl_bp.route("/shorturl")
def shorturl():
    key = request.args.get("key", "")
    url = request.args.get("url", "")

    user, err = check_access(key)
    if err:
        return err

    if not url:
        return send_response("error", {}, {"message": "URL required"})

    try:
        short = req.get(f"https://tinyurl.com/api-create.php?url={quote(url)}", timeout=10).text.strip()
    except Exception:
        short = None

    if not short:
        return send_response("error", {}, {"message": "Failed to shorten URL"})

    return send_response("success", {
        "original_url": url,
        "short_url":    short
    }, {"user": user["name"]})
