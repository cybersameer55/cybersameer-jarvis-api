"""
@api /qr2
@method GET
@param text
@usage /qr2?key=YOUR_API_KEY&text=HELLO
"""

from flask import Blueprint, request
from urllib.parse import quote
from core import check_access, send_response

qr2_bp = Blueprint("qr2", __name__)


@qr2_bp.route("/qr2")
def qr2():
    key  = request.args.get("key", "")
    text = request.args.get("text", "")

    user, err = check_access(key)
    if err:
        return err

    if not text:
        return send_response("error", {}, {"message": "Text required"})

    qr = f"https://quickchart.io/qr?text={quote(text)}"

    return send_response("success", {
        "text":     text,
        "qr_image": qr
    }, {"user": user["name"]})
