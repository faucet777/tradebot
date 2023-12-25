from flask import Flask, render_template
from connect_mongo import get_ohlc_arr, normalize
#ohlc = get_ohlc_arr()
svgcoords = normalize()
#base_ep = 'https://api.binance.com'
#curr_ep = '/api/v3/klines'
#pair = 'BTCUSDT'
#timeframe = '5m'
app = Flask(__name__)
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', svgcoords=svgcoords)

if __name__ == '__main__':
    app.run(debug=True)

