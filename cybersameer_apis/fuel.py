"""
@api /fuel
@method GET
@param distance, mileage, price
@usage /fuel?key=YOUR_API_KEY&distance=500&mileage=15&price=105
"""
from flask import Blueprint, request
from core import check_access, send_response

fuel_bp = Blueprint("fuel", __name__)

@fuel_bp.route("/fuel")
def fuel():
    key      = request.args.get("key","")
    distance = request.args.get("distance","")
    mileage  = request.args.get("mileage","")
    price    = request.args.get("price","")
    user, err= check_access(key)
    if err: return err
    if not distance or not mileage or not price:
        return send_response("error",{},{"message":"distance (km), mileage (km/L), and price (per litre) required"})
    try:
        d=float(distance); m=float(mileage); p=float(price)
        litres = d/m; cost = litres*p
        return send_response("success",{
            "distance_km":d,"mileage_km_per_litre":m,"fuel_price_per_litre":p,
            "fuel_required_litres":round(litres,3),"total_cost":round(cost,2),
            "cost_per_km":round(p/m,2)
        },{"user":user["name"]})
    except: return send_response("error",{},{"message":"Invalid numbers"})
