import pandas as pd
import sys
import requests

import mplfinance as mpf

from PyQt5.QtWidgets import QMainWindow, QWidget, QApplication
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

base_ep = 'https://api.binance.com'
candles_ep = '/api/v3/klines'
param = {'symbol': 'BTCUSDT', 'interval': '5m', 'limit': 50}

reqcandles = requests.get(base_ep + candles_ep, params=param)
arraydata = reqcandles.json()
arraydata = pd.DataFrame(arraydata)


t=arraydata.iloc[:,0]
o=arraydata.iloc[:,1].astype(float)
h=arraydata.iloc[:,2].astype(float)
l=arraydata.iloc[:,3].astype(float)
c=arraydata.iloc[:,4].astype(float)
v=arraydata.iloc[:,5].astype(float)

d={'Open': o,'High': h,'Low': l,'Close': c,'Volume': v}
d1=pd.DataFrame(data=d)
d1.index = pd.to_datetime(t,unit='ms')
d1.index.name='Date'

class Canvas(FigureCanvas):
    def __init__(self,parent):
        fig, axlist =mpf.plot(d1,type='candle',returnfig=True)
        super().__init__(fig)
        self.setParent(parent)


class AppDemo(QWidget):
    def __init__(self):
        super().__init__()
        chart=Canvas(self)

if __name__ == '__main__':

    app=QApplication(sys.argv)
    demo=AppDemo()
    demo.show()
    sys.exit(app.exec_())




