"""
@api /inrupees
@method GET
@param number
@usage /inrupees?key=YOUR_API_KEY&number=1234567
"""
from flask import Blueprint, request
from core import check_access, send_response

rupee_bp = Blueprint("rupee", __name__)

ONES=["","One","Two","Three","Four","Five","Six","Seven","Eight","Nine","Ten","Eleven","Twelve","Thirteen","Fourteen","Fifteen","Sixteen","Seventeen","Eighteen","Nineteen"]
TENS=["","","Twenty","Thirty","Forty","Fifty","Sixty","Seventy","Eighty","Ninety"]

def n2w(n):
    if n==0: return ""
    if n<20: return ONES[n]
    if n<100:return TENS[n//10]+(" "+ONES[n%10] if n%10 else "")
    return ONES[n//100]+" Hundred"+(" "+n2w(n%100) if n%100 else "")

def to_indian(n):
    if n==0: return "Zero Rupees Only"
    parts=[]
    crore=n//10000000; n%=10000000
    lakh =n//100000;   n%=100000
    thou =n//1000;     n%=1000
    hun  =n
    if crore: parts.append(n2w(crore)+" Crore")
    if lakh:  parts.append(n2w(lakh)+" Lakh")
    if thou:  parts.append(n2w(thou)+" Thousand")
    if hun:   parts.append(n2w(hun))
    return " ".join(parts)+" Rupees Only"

@rupee_bp.route("/inrupees")
def inrupees():
    key    = request.args.get("key","")
    number = request.args.get("number","")
    user, err = check_access(key)
    if err: return err
    if not number: return send_response("error",{},{"message":"number required"})
    try:
        n=int(float(number)); paise=round((float(number)-n)*100)
        words=to_indian(n)
        if paise: words=words.replace("Only",f"and {n2w(paise)} Paise Only")
        return send_response("success",{
            "number":float(number),"formatted":f"₹{n:,}","words":words,
            "crores":n//10000000,"lakhs":(n%10000000)//100000,"thousands":(n%100000)//1000
        },{"user":user["name"]})
    except: return send_response("error",{},{"message":"Invalid number"})
