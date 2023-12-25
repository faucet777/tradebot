import hashlib
from operator import itemgetter
#import websockets
import requests
import hmac
import time
TIME_IN_FORCE = 'GTC'  # Good till cancelled
# TIME_IN_FORCE = 'IOC'  # Immediate or cancel
# TIME_IN_FORCE = 'FOK'  # Fill or kill

api_url = "https://api.binance.com/api/v3/order/test"
API_KEY = ""
API_SECRET = ""

# Parameters for the buy order
symbol = "BTCUSDT"  # the symbol for the market you want to trade
side = "BUY"  # buy or sell order
type = "LIMIT"  # order type (limit, market, stop-loss, etc.) LIMIT_MAKER are LIMIT orders that will be rejected if they would immediately match and trade as a taker.
quantity = 0.001  # the amount of the asset you want to buy
price = 10000.0  # the price at which you want to buy

# Create the headers for the API request
headers = {
    "X-MBX-APIKEY": API_KEY
}

# Create the data for the API request
data = {
    "symbol": symbol,
    "side": side,
    "type": type,
    "quantity": quantity,
    "price": price,

}

def order_params(params=None):
    data = dict(filter(lambda el: el[1] is not None, params.items()))
    data["timestamp"] = int(time.time() * 1000)
    data["timeInForce"] = TIME_IN_FORCE
    paramlist = []
    for key, value in data.items():
        paramlist.append((key, str(value)))
    # sort parameters by key
    paramlist.sort(key=itemgetter(0))
    return paramlist

def generate_signature(params) -> str:
    ordered_params = order_params(params)
    query_string = '&'.join([f"{d[0]}={d[1]}" for d in ordered_params])
    print(query_string)
    m = hmac.new(API_SECRET.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256)
    ordered_params.append(("signature",m.hexdigest()))
    print(ordered_params)
    return ordered_params


# Send the API request and store the response

# Print the response from the API
#print(response.json())

if __name__ == '__main__':
    payload = dict(generate_signature(data))
    print(payload)
    response = requests.post(api_url, headers=headers, params=payload, timeout=30)
    print(response.json())


