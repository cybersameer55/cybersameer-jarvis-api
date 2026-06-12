"""
@api /crypto
@method GET
@param coin
@usage /crypto?key=YOUR_API_KEY&coin=bitcoin|BTC
"""

from flask import Blueprint, request
from core import check_access, clean_response, fetch_api, send_response

crypto_bp = Blueprint("crypto", __name__)


@crypto_bp.route("/crypto")
def crypto():
    key  = request.args.get("key", "")
    coin = request.args.get("coin", "btc").lower()

    user, err = check_access(key)
    if err:
        return err

    coin_map = {
        "btc": {"id": "bitcoin",  "symbol": "BTCUSDT"},
        "eth": {"id": "ethereum", "symbol": "ETHUSDT"}
    }
    coin_data = coin_map.get(coin, coin_map["btc"])
    id_    = coin_data["id"]
    symbol = coin_data["symbol"]
    upper  = coin.upper()

    coingecko_price = clean_response(fetch_api(f"https://api.coingecko.com/api/v3/simple/price?ids={id_}&vs_currencies=usd,inr") or {})
    coingecko_full  = clean_response(fetch_api(f"https://api.coingecko.com/api/v3/coins/{id_}") or {})
    binance_price   = clean_response(fetch_api(f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}") or {})
    binance_24hr    = clean_response(fetch_api(f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}") or {})
    cryptocompare   = clean_response(fetch_api(f"https://min-api.cryptocompare.com/data/price?fsym={upper}&tsyms=USD,INR") or {})
    coinbase_spot   = clean_response(fetch_api(f"https://api.coinbase.com/v2/prices/{upper}-USD/spot") or {})
    coinbase_buy    = clean_response(fetch_api(f"https://api.coinbase.com/v2/prices/{upper}-USD/buy") or {})
    kraken          = clean_response(fetch_api("https://api.kraken.com/0/public/Ticker?pair=XBTUSD") or {})
    okx             = clean_response(fetch_api(f"https://www.okx.com/api/v5/market/ticker?instId={upper}-USDT") or {})
    blockchain      = clean_response(fetch_api("https://blockchain.info/ticker") or {})

    if not coingecko_price and not binance_price and not cryptocompare:
        return send_response("error", {}, {"message": "No data found"})

    return send_response("success", {
        "coin": upper,
        "summary": {
            "coingecko":    coingecko_price.get(id_) if coingecko_price else None,
            "cryptocompare": cryptocompare
        },
        "markets": {
            "binance_price": binance_price,
            "binance_24hr":  binance_24hr,
            "coinbase_spot": coinbase_spot,
            "coinbase_buy":  coinbase_buy,
            "kraken":        kraken,
            "okx":           okx,
            "blockchain":    blockchain
        },
        "details": {
            "coingecko_full": coingecko_full
        }
    }, {"user": user["name"]})
