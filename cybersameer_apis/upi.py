"""
@api /upi
@method GET
@param upi_id
@usage /upi?key=YOUR_API_KEY&upi_id=example@paytm
"""
import re
from flask import Blueprint, request
from core import check_access, send_response

upi_bp = Blueprint("upi", __name__)

UPI_PROVIDERS = {
    "paytm":"Paytm","ybl":"PhonePe","ibl":"PhonePe","axl":"PhonePe","okicici":"Google Pay",
    "okhdfcbank":"Google Pay","okaxis":"Google Pay","oksbi":"Google Pay","upi":"BHIM UPI",
    "icici":"ICICI Bank","hdfcbank":"HDFC Bank","sbi":"SBI","axisbank":"Axis Bank",
    "kotak":"Kotak Bank","indus":"IndusInd Bank","apl":"Amazon Pay","rapl":"Amazon Pay",
    "freecharge":"FreeCharge","mbk":"Mobikwik","timecosmos":"Airtel Money","yapl":"Yes Bank"
}

@upi_bp.route("/upi")
def upi():
    key    = request.args.get("key","")
    upi_id = request.args.get("upi_id","").strip().lower()
    user, err = check_access(key)
    if err: return err
    if not upi_id: return send_response("error",{},{"message":"upi_id required"})
    pattern = r"^[a-zA-Z0-9.\-_+]+@[a-zA-Z0-9]+$"
    valid   = bool(re.match(pattern, upi_id))
    parts   = upi_id.split("@") if "@" in upi_id else ["",""]
    handle  = parts[1] if len(parts)>1 else ""
    provider= next((v for k,v in UPI_PROVIDERS.items() if k in handle),"Unknown")
    return send_response("success",{
        "upi_id":upi_id,"is_valid_format":valid,
        "username":parts[0],"handle":handle,
        "provider":provider,
        "note":"Format validation only. Actual UPI verification requires bank API."
    },{"user":user["name"]})
