"""
@api /gst_calc
@method GET
@param amount, rate, action
@usage /gst_calc?key=YOUR_API_KEY&amount=1000&rate=18&action=add
"""
from flask import Blueprint, request
from core import check_access, send_response

tax_bp = Blueprint("tax", __name__)

@tax_bp.route("/gst_calc")
def gst_calc():
    key    = request.args.get("key","")
    amount = request.args.get("amount","")
    rate   = request.args.get("rate","18")
    action = request.args.get("action","add").lower()
    user, err = check_access(key)
    if err: return err
    if not amount: return send_response("error",{},{"message":"amount required"})
    try:
        a=float(amount); r=float(rate)/100
        if action=="add":
            gst=a*r; total=a+gst; base=a
        else:
            base=a/(1+r); gst=a-base; total=a
        gst_rates = {"CGST":round(gst/2,2),"SGST":round(gst/2,2),"IGST":round(gst,2)}
        return send_response("success",{
            "base_amount":round(base,2),"gst_rate_percent":float(rate),"gst_amount":round(gst,2),
            "total_amount":round(total,2),"breakdown":gst_rates
        },{"user":user["name"]})
    except: return send_response("error",{},{"message":"Invalid numbers"})
