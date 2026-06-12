"""
@api /currency
@method GET
@param from, to, amount
@usage /currency?key=YOUR_API_KEY&from=USD&to=INR&amount=1
"""

from flask import Blueprint, request
from urllib.parse import quote
from core import check_access, clean_response, fetch_api, send_response, get_time_now

currency_bp = Blueprint("currency", __name__)


@currency_bp.route("/currency")
def currency():
    key    = request.args.get("key", "")
    frm    = request.args.get("from", "USD").upper()
    to     = request.args.get("to", "INR").upper()
    amount = request.args.get("amount", "1")

    user, err = check_access(key)
    if err:
        return err

    api1 = clean_response(fetch_api(f"https://api.frankfurter.app/latest?from={frm}&to={to}") or {})
    api2 = clean_response(fetch_api(f"https://open.er-api.com/v6/latest/{frm}") or {})
    api3 = clean_response(fetch_api(f"https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/{frm.lower()}.json") or {})

    rate = None
    if api1 and "rates" in api1:
        rate = api1["rates"].get(to)
    elif api2 and "rates" in api2:
        rate = api2["rates"].get(to)

    converted = None
    if rate:
        try:
            converted = float(amount) * float(rate)
        except Exception:
            pass

    if not api1 and not api2:
        return send_response("error", {}, {"message": "No data found"})

    return send_response("success", {
        "from":          frm,
        "to":            to,
        "amount":        amount,
        "rate":          rate,
        "converted":     converted,
        "time":          get_time_now(),
        "frankfurter":   api1,
        "open_er":       api2,
        "fawaz_api":     api3
    }, {"user": user["name"]})
