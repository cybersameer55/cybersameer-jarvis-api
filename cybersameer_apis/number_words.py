"""
@api /numwords
@method GET
@param number
@usage /numwords?key=YOUR_API_KEY&number=12345
"""
from flask import Blueprint, request
from core import check_access, send_response

number_words_bp = Blueprint("number_words", __name__)

ONES=["","One","Two","Three","Four","Five","Six","Seven","Eight","Nine","Ten",
      "Eleven","Twelve","Thirteen","Fourteen","Fifteen","Sixteen","Seventeen","Eighteen","Nineteen"]
TENS=["","","Twenty","Thirty","Forty","Fifty","Sixty","Seventy","Eighty","Ninety"]

def n2w(n):
    if n==0: return "Zero"
    if n<0:  return "Negative "+n2w(-n)
    if n<20: return ONES[n]
    if n<100:return TENS[n//10]+("" if n%10==0 else " "+ONES[n%10])
    if n<1000:return ONES[n//100]+" Hundred"+((" "+n2w(n%100)) if n%100 else "")
    if n<100000:return n2w(n//1000)+" Thousand"+((" "+n2w(n%1000)) if n%1000 else "")
    if n<10000000:return n2w(n//100000)+" Lakh"+((" "+n2w(n%100000)) if n%100000 else "")
    return n2w(n//10000000)+" Crore"+((" "+n2w(n%10000000)) if n%10000000 else "")

@number_words_bp.route("/numwords")
def numwords():
    key    = request.args.get("key","")
    number = request.args.get("number","")
    user, err = check_access(key)
    if err: return err
    if not number: return send_response("error",{},{"message":"number required"})
    try:
        n=int(number)
        return send_response("success",{"number":n,"words":n2w(abs(n)),"indian_format":f"Rs. {n:,}"},{"user":user["name"]})
    except: return send_response("error",{},{"message":"Invalid number"})
