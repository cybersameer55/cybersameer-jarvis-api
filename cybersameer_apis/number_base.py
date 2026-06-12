"""
@api /numbase
@method GET
@param number, from_base (2/8/10/16), to_base (2/8/10/16)
@usage /numbase?key=YOUR_API_KEY&number=255&from_base=10&to_base=16
"""
from flask import Blueprint, request
from core import check_access, send_response, get_time_now
number_base_bp = Blueprint("number_base", __name__)
@number_base_bp.route("/numbase")
def number_base():
    key = request.args.get("key","")
    user, err = check_access(key)
    if err: return err
    num_str=request.args.get("number",""); from_b=int(request.args.get("from_base","10")); to_b=int(request.args.get("to_base","2"))
    if not num_str:
        return send_response("error",{},{"message":"number, from_base, to_base required"})
    if from_b not in [2,8,10,16] or to_b not in [2,8,10,16]:
        return send_response("error",{},{"message":"base must be 2, 8, 10, or 16"})
    try:
        decimal=int(num_str, from_b)
        converters={2:bin(decimal)[2:],8:oct(decimal)[2:],10:str(decimal),16:hex(decimal)[2:].upper()}
        return send_response("success",{
            "input":num_str,"from_base":from_b,"to_base":to_b,"result":converters[to_b],
            "all_bases":{"binary":converters[2],"octal":converters[8],"decimal":converters[10],"hexadecimal":converters[16]},
            "time":get_time_now()
        },{"user":user["name"]})
    except:
        return send_response("error",{},{"message":"Invalid number for given base"})
