"""
@api /urldecode
@method GET
@param text (url encoded string)
@usage /urldecode?key=YOUR_API_KEY&text=Hello%20World
"""
from urllib.parse import unquote
from flask import Blueprint, request
from core import check_access, send_response, get_time_now
url_decode_bp = Blueprint("url_decode", __name__)
@url_decode_bp.route("/urldecode")
def url_decode():
    key = request.args.get("key","")
    text = request.args.get("text","")
    user, err = check_access(key)
    if err: return err
    if not text:
        return send_response("error",{},{"message":"text required"})
    decoded=unquote(text)
    return send_response("success",{
        "encoded":text,"decoded":decoded,"time":get_time_now()
    },{"user":user["name"]})
