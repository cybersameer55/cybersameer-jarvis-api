"""
@api /emi
@method GET
@param principal, rate, tenure
@usage /emi?key=YOUR_API_KEY&principal=500000&rate=8.5&tenure=60
"""
from flask import Blueprint, request
from core import check_access, send_response

emi_bp = Blueprint("emi", __name__)

@emi_bp.route("/emi")
def emi():
    key       = request.args.get("key","")
    principal = request.args.get("principal","")
    rate      = request.args.get("rate","")
    tenure    = request.args.get("tenure","")
    user, err = check_access(key)
    if err: return err
    if not principal or not rate or not tenure:
        return send_response("error",{},{"message":"principal, rate (annual %), and tenure (months) required"})
    try:
        P = float(principal); r = float(rate)/12/100; n = int(tenure)
        if r == 0: emi_val = P/n
        else:      emi_val = P * r * (1+r)**n / ((1+r)**n - 1)
        total = emi_val * n
        interest = total - P
        return send_response("success",{
            "principal":P,"annual_rate_percent":float(rate),"tenure_months":n,
            "emi":round(emi_val,2),"total_payment":round(total,2),
            "total_interest":round(interest,2),"interest_percent":round(interest/P*100,2)
        },{"user":user["name"]})
    except: return send_response("error",{},{"message":"Invalid numbers"})
