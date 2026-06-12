"""
@api /websitezip
@method GET
@param url
@usage /websitezip?key=YOUR_API_KEY&url=https://example.com
"""

from flask import Blueprint, request
from urllib.parse import quote
from core import check_access, clean_response, fetch_api, send_response

websitezip_bp = Blueprint("websitezip", __name__)


@websitezip_bp.route("/websitezip")
def websitezip():
    key = request.args.get("key", "")
    url = request.args.get("url", "")

    user, err = check_access(key)
    if err:
        return err

    if not url:
        return send_response("error", {}, {"message": "URL required"})

    data = fetch_api(f"https://rohit-website-scrapper-api.vercel.app/zip?url={quote(url)}")

    if not data:
        return send_response("error", {}, {"message": "API failed"})

    data = clean_response(data)

    if not data:
        return send_response("error", {}, {"message": "No data found"})

    return send_response("success", {
        "input_url":  url,
        "zip_result": data
    }, {"user": user["name"]})
