"""
@api /urlencode
@method GET
@param text
@usage /urlencode?key=YOUR_API_KEY&text=Hello World & More!
"""
from urllib.parse import quote, unquote
from flask import Blueprint, request
from core import check_access, send_response, get_time_now
url_encode_bp = Blueprint("url_encode", __name__)
@url_encode_bp.route("/urlencode")
def url_encode():
    key = request.args.get("key","")
    text = request.args.get("text","")
    user, err = check_access(key)
    if err: return err
    if not text:
        return send_response("error",{},{"message":"text required"})
    encoded=quote(text)
    return send_response("success",{
        "original":text,"url_encoded":encoded,"length_original":len(text),
        "length_encoded":len(encoded),"time":get_time_now()
    },{"user":user["name"]})
