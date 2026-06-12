"""
@api /stock
@method GET
@param symbol
@usage /stock?key=YOUR_API_KEY&symbol=AAPL
"""
from flask import Blueprint, request
from core import check_access, send_response, fetch_api

stock_bp = Blueprint("stock", __name__)

@stock_bp.route("/stock")
def stock():
    key    = request.args.get("key","")
    symbol = request.args.get("symbol","AAPL").upper()
    user, err = check_access(key)
    if err: return err
    data = fetch_api(f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=5d", headers={"User-Agent":"Mozilla/5.0"})
    if not data: return send_response("error",{},{"message":"Failed to fetch stock data"})
    meta = (data.get("chart",{}).get("result") or [{}])[0].get("meta",{})
    if not meta: return send_response("error",{},{"message":"Symbol not found"})
    return send_response("success",{
        "symbol":meta.get("symbol",""),"name":meta.get("longName",""),
        "currency":meta.get("currency",""),"exchange":meta.get("exchangeName",""),
        "current_price":meta.get("regularMarketPrice"),
        "previous_close":meta.get("previousClose"),
        "52_week_high":meta.get("fiftyTwoWeekHigh"),
        "52_week_low":meta.get("fiftyTwoWeekLow"),
        "market_cap":meta.get("marketCap"),
        "timezone":meta.get("timezone","")
    },{"user":user["name"]})
