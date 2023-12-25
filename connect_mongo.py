# don't foget to run mongo server with 'mongod' comand from mongo directory
#
from datetime import datetime
import pymongo
import requests
from pymongo.collection import Collection

# from pymongo.database import Database

base_ep = 'https://api.binance.com'
curr_ep = '/api/v3/klines'
pair = 'BTCUSDT'
timeframe = '5m'
curr_client = pymongo.MongoClient('mongodb://localhost:27017/')
# curr_client.drop_database(curr_pair) #!!!!!DROP DATABASE
curr_database = curr_client[pair]
curr_collection = curr_database[timeframe]

def get_last_time(collection: Collection = curr_collection):
    try:
        ltime = collection.find_one(sort=[('open_time', pymongo.DESCENDING)])['ohlc'][5]
        # collection_item.aggregate([
        #                                 {'$sort': {'open_time': -1}},
        #                                 {'$limit':1}
        #                             ])
        return ltime
    except Exception as exc:
        print('empty collection, no last element found')
        print(exc)
        ltime = None
        return ltime
#print(f'last time is  {get_last_time()}')





def get_stock_data(params=None):  # get list of candles(dicts) from stock, not storing to db
    #print(params)
    if params is None:
        params = configure_params()
    reqcandles = requests.get(base_ep + curr_ep, params=params)
    stock_data = reqcandles.json()
    #print(stock_data)
    if stock_data:
        try:
            stock_dict_list = [{'open_time': time_ax,
                                'ohlc': ohlc} for (time_ax, ohlc) in
                               zip([stock_data[i][0] for i in range(len(stock_data))],  #OPTIMIZE for i, item in enumerate(sequence):
                                   [stock_data[i][1:] for i in range(len(stock_data))])]             # print("{} : {}".format(i, item)
            return stock_dict_list
        except Exception as e:
            print('nothing to upd')
            print(e)
            stock_dict_list = None
            return stock_dict_list

    else:
        print('not stockdata')


def update_stock_data(collection: Collection = curr_collection):  # puts new objects to db from list of candles(dicts) taken
    collection.insert_many(get_stock_data())              # from get_stock_data()##OPTIMIZE parameter "stock_data"=get_stock_data()
    print(collection.estimated_document_count())



def get_ohlc_arr(pair=pair, timeframe=timeframe,
                 limit=1800):  # gets list of dicts id,open_time,[ohlc] from existing db collection
    curr_client = pymongo.MongoClient('mongodb://localhost:27017/')  #OPTIMIZE HINT!!! one db connection is running above
    # curr_client.drop_database(curr_pair) #!!!!!DROP DATABASE
    curr_database = curr_client[pair]
    curr_collection = curr_database[timeframe]
    # curr_collection.insert_many(get_stock_data())
    # print(curr_collection.estimated_document_count())
    return list(curr_collection.find().limit(limit))


ohlcArr = get_ohlc_arr()
def normalize(ohlc_arr: list = ohlcArr): #normalize prices to percentage to use in svg later
    coords = []
    minmax = []
    for candle in ohlc_arr:
        [o, h, l, c] = [float(candle['ohlc'][p]) for p in range(4)]
        coords.append({
            'time': datetime.utcfromtimestamp(candle['open_time'] / 1000).strftime('%Y-%m-%d %H:%M:%S'),
            'ohlc': dict(o=o, h=h, l=l, c=c)
        })
        if not minmax:
            minmax = [l, h]
            continue
        elif l < minmax[0]:
            minmax[0] = l
            continue
        elif h > minmax[1]:
            minmax[1] = h

    minc = minmax[0]
    maxc = minmax[1]
    i = 0
    scale_perc = maxc * 100 / (maxc - minc)
    for coord in coords:  # 2 fors calculate persentage of each ohlc price relatively
        for price in coord['ohlc']:  # min and max price to convert to svg later
            coord['ohlc'][price] = ((maxc - coord['ohlc'][price]) / (maxc - minc)) * 100#((maxc - coord['ohlc'][price]) / (maxc - minc)) * 100  # (coord['ohlc'][price] / maxc) * 100- same above
        i += 1                            # but relatevely max price and zero
        coord['i'] = float(i/4)
    #print(coords)
    return scale_perc, coords


if __name__ == '__main__':
    update_stock_data()

    # print(get_ohlc_arr())
    #update_stock_data()
    #print(normalize())



    # print(curr_timeInterval.aggregate([
    #                                     {'$sort': {'open_time': 1}},
    #                                     {'$limit':100}
    #                                   ]))

# collectionBTCUSDT = databaseBTC['btc-usdt-5m']
# collectionBTCUSDT.insert_many(get_stock_data())
# for doc in collectionBTCUSDT.find({}):
#     print(doc)
# db. yourcollectionname. findOne({$query: {}, $orderby: {$natural : -1}})  last item in collection
