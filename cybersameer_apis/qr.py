"""
@api /qr
@method GET
@param text (required)
@param size (optional, default 300, min 50, max 1000)
@param color (optional hex, default 000000)
@param bgcolor (optional hex, default ffffff)
@param format (optional, default png, options: png, svg, jpg)
@usage /qr?key=YOUR_API_KEY&text=HELLO&size=300&color=000000&bgcolor=ffffff
"""

from flask import Blueprint, request
from urllib.parse import quote
from core import check_access, send_response

qr_bp = Blueprint("qr", __name__)

@qr_bp.route("/qr")
def qr():
    key     = request.args.get("key", "")
    text    = request.args.get("text", "")
    size    = request.args.get("size", "300")
    color   = request.args.get("color", "000000").strip("#")
    bgcolor = request.args.get("bgcolor", "ffffff").strip("#")
    fmt     = request.args.get("format", "png").lower()

    user, err = check_access(key)
    if err:
        return err

    if not text:
        return send_response("error", {}, {"message": "Text parameter required"})

    # Validate and clamp size
    try:
        size = min(max(int(size), 50), 1000)
    except:
        size = 300

    # Validate format
    if fmt not in ("png", "svg", "jpg", "jpeg"):
        fmt = "png"

    encoded = quote(text)

    # Build QR image URLs from multiple free generators
    qr_urls = {
        # 1. qrserver.com (supports size, color, bgcolor, format)
        "qrserver": (
            f"https://api.qrserver.com/v1/create-qr-code/"
            f"?size={size}x{size}&data={encoded}"
            f"&color={color}&bgcolor={bgcolor}&format={fmt}"
        ),
        # 2. quickchart.io (dark=color, light=bgcolor, size)
        "quickchart": (
            f"https://quickchart.io/qr"
            f"?text={encoded}&size={size}&dark={color}&light={bgcolor}"
        ),
        # 3. Google Charts (only size and data, no color)
        "google_charts": (
            f"https://chart.googleapis.com/chart"
            f"?chs={size}x{size}&cht=qr&chl={encoded}"
        ),
        # 4. GoQR.me (free, supports size and data)
        "goqr": (
            f"https://api.qr-code-generator.com/v1/create"
            f"?access-token=free&data={encoded}&size={size}x{size}"
            f"&color={color}&bgcolor={bgcolor}"
        ),
        # 5. QR Code Monkey (free, supports size, color, bgcolor)
        "qrcode_monkey": (
            f"https://api.qr-code-monkey.com/v1/qr"
            f"?data={encoded}&size={size}&color={color}&bgcolor={bgcolor}"
        )
    }

    # Remove any that might be empty or invalid (just in case)
    qr_urls = {k: v for k, v in qr_urls.items() if v}

    return send_response("success", {
        "text":      text,
        "size":      size,
        "color":     "#" + color,
        "bgcolor":   "#" + bgcolor,
        "format":    fmt,
        "qr_images": qr_urls
    }, {"user": user["name"]})