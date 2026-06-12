"""
@api /otp
@method GET
@param length, type
@usage /otp?key=YOUR_API_KEY&length=6&type=numeric
"""
from flask import Blueprint, request
from core import check_access, send_response
import random, string

otp_gen_bp = Blueprint("otp_gen", __name__)

@otp_gen_bp.route("/otp")
def otp_gen():
    key    = request.args.get("key","")
    length = int(request.args.get("length",6))
    otype  = request.args.get("type","numeric").lower()
    user, err = check_access(key)
    if err: return err
    if length < 4 or length > 12: length = 6
    if otype == "alpha":       chars = string.ascii_uppercase
    elif otype == "alphanumeric": chars = string.ascii_uppercase + string.digits
    else:                      chars = string.digits
    otp = "".join(random.choices(chars, k=length))
    return send_response("success",{"otp":otp,"length":length,"type":otype},{"user":user["name"]})
