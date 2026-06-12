"""
@api /qr1
@method GET
@param text
@usage /qr1?key=YOUR_API_KEY&text=HELLO
"""

from flask import Blueprint, request
from urllib.parse import quote
from core import check_access, send_response

qr1_bp = Blueprint("qr1", __name__)


@qr1_bp.route("/qr1")
def qr1():
    key  = request.args.get("key", "")
    text = request.args.get("text", "")

    user, err = check_access(key)
    if err:
        return err

    if not text:
        return send_response("error", {}, {"message": "Text required"})

    qr = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={quote(text)}"

    return send_response("success", {
        "text":     text,
        "qr_image": qr
    }, {"user": user["name"]})
