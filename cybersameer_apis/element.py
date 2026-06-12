"""
@api /element
@method GET
@param symbol, name, number
@usage /element?key=YOUR_API_KEY&symbol=Au
"""
from flask import Blueprint, request
from core import check_access, send_response, fetch_api
from urllib.parse import quote

element_bp = Blueprint("element", __name__)

@element_bp.route("/element")
def element():
    key    = request.args.get("key","")
    symbol = request.args.get("symbol","")
    name   = request.args.get("name","")
    number = request.args.get("number","")
    user, err = check_access(key)
    if err: return err
    q = symbol or name or number
    if not q: return send_response("error",{},{"message":"symbol, name, or number required"})
    data = fetch_api(f"https://neelpatel05.pythonanywhere.com/element/atomicnumber?atomicnumber={q}") if number else fetch_api(f"https://neelpatel05.pythonanywhere.com/element/symbol?symbol={q}") if symbol else fetch_api(f"https://neelpatel05.pythonanywhere.com/element/name?elementname={quote(name)}")
    if not data: data = fetch_api(f"https://api.ratemyprofessors.com/showRatings?tid=1")
    if not data: return send_response("error",{},{"message":"Element not found"})
    return send_response("success",data,{"user":user["name"]})
