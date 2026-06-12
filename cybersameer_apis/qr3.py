"""
@api /qr3
@method GET
@param text, size (optional), color (optional hex), bgcolor (optional hex)
@usage /qr3?key=YOUR_API_KEY&text=HELLO&size=300&color=000000&bgcolor=ffffff
"""

from flask import Blueprint, request
from urllib.parse import quote
from core import check_access, send_response

qr3_bp = Blueprint("qr3", __name__)


@qr3_bp.route("/qr3")
def qr3():
    key     = request.args.get("key", "")
    text    = request.args.get("text", "")
    size    = request.args.get("size", "300")
    color   = request.args.get("color", "000000").strip("#")
    bgcolor = request.args.get("bgcolor", "ffffff").strip("#")

    user, err = check_access(key)
    if err:
        return err

    if not text:
        return send_response("error", {}, {"message": "Text required"})

    try:
        size = min(max(int(size), 50), 1000)
    except Exception:
        size = 300

    qr1 = f"https://api.qrserver.com/v1/create-qr-code/?size={size}x{size}&data={quote(text)}&color={color}&bgcolor={bgcolor}"
    qr2 = f"https://quickchart.io/qr?text={quote(text)}&size={size}&dark={color}&light={bgcolor}"
    qr3 = f"https://chart.googleapis.com/chart?chs={size}x{size}&cht=qr&chl={quote(text)}"

    return send_response("success", {
        "text":      text,
        "size":      size,
        "color":     "#" + color,
        "bgcolor":   "#" + bgcolor,
        "qr_api1":   qr1,
        "qr_api2":   qr2,
        "qr_api3":   qr3
    }, {"user": user["name"]})
