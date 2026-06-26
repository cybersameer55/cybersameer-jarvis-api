"""
@api /dns
@method GET
@param domain, type
@usage /dns?key=YOUR_API_KEY&domain=google.com&type=A
"""
from flask import Blueprint, request
from core import check_access, send_response, fetch_api

dns_bp = Blueprint("dns", __name__)

@dns_bp.route("/dns")
def dns():
    key    = request.args.get("key","")
    domain = request.args.get("domain","")
    dtype  = request.args.get("type","A").upper()
    user, err = check_access(key)
    if err: return err
    if not domain: return send_response("error",{},{"message":"domain required"})
    data = fetch_api(f"https://dns.google/resolve?name={domain}&type={dtype}")
    if not data: return send_response("error",{},{"message":"DNS lookup failed"})
    answers = data.get("Answer",[])
    records = [{"name":a.get("name",""),"type":a.get("type"),"ttl":a.get("TTL"),"data":a.get("data","")} for a in answers]
    return send_response("success",{"domain":domain,"type":dtype,"records":records,"count":len(records)},{"user":user["name"]})
