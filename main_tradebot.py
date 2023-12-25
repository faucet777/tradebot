from operator import itemgetter
import requests
import hashlib
import hmac
import time
import asyncio
import calculator
from pymongo.database import Database
from constants import *
from db_connect import *
from stock_connect import *


def order_params(params=None):
    data = dict(filter(lambda el: el[1] is not None, params.items()))
    paramlist = []
    for key, value in data.items():
        paramlist.append((key, str(value)))
    # sort parameters by key
    paramlist.sort(key=itemgetter(0))
    return paramlist


def generate_signature(params) -> str:
    ordered_params = order_params(params)
    print(ordered_params)
    query_string = '&'.join([f"{d[0]}={d[1]}" for d in ordered_params])
    print(query_string)
    m = hmac.new(API_SECRET.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256)
    return m.hexdigest()



class paramsHelper():
    def __init__(self, params):
        self.api = params['api_ep']
        self.interval = params['interval']
        self.qntty = params['qntty']
        self.stock = params['stock']
        self.symbol = params['symbol']
        self.indicator = params['indicator']

        #self.collection = set_connection_collection()  может коллекцию в свойство закинуть, чтоб каждый раз не подключаться
    def set_connection_collection(self):
        curr_client = pymongo.MongoClient(DB_URL)
        curr_database = curr_client[self.symbol]
        curr_collection = curr_database[self.interval]
        #self.collection = set_connection_collection()

        return curr_collection

    # def update_db(self, collection:Collection, updates: list[dict]):  # puts new objects to db from list of candles(dicts) taken
    #   collection.insert_many(updates)  # from get_stock_data()##OPTIMIZE parameter "stock_data"=get_stock_data()
    #   print('databsase updated, current elements count:>>>>'+ str(collection.estimated_document_count()))

    def generate_params(self, action=None):
        def order_params(params=None):
            data = dict(filter(lambda el: el[1] is not None, params.items()))
            paramlist = []
            for key, value in data.items():
                paramlist.append((key, str(value)))
            # sort parameters by key
            paramlist.sort(key=itemgetter(0))
            return paramlist

        def generate_signature(params) -> str:
            ordered_params = order_params(params)
            #print(ordered_params)
            query_string = '&'.join([f"{d[0]}={d[1]}" for d in ordered_params])
            #print(query_string)
            m = hmac.new(API_SECRET.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256)
            return m.hexdigest()

        # params.update({'signature':generate_signature(params)})
        # response = requests.post(url, params=params, headers=headers)

        try:
            match action:
                case None:
                    return None
                case 'start trade session':
                    params = {
                        'symbol': self.symbol,
                        'interval': self.interval,
                    }
                    return params
                case 'connect_db':
                    params = {
                        'symbol': self.symbol,
                        'interval': self.interval,
                    }
                    return params
                case 'init_db':
                    #print('self api in init' + self.api)
                    params = {'api_ep': self.api,
                              'options': {
                                  'symbol': self.symbol,  # str(collection.full_name).split('.')[0]
                                  'interval': self.interval,
                                  'startTime': 1483209000000,  # 2017
                                  # надо проверить коллекцию на наличие элементов, потом грузить в время или начальное время 2015,,,2017maybe mongoindexes? calling function bad idea not pep8? fixed:put dict to this func
                                  'endTime': None,
                                  'limit': 1000,
                              }}
                    #print('params in init     \n ', params)
                    return params

                case 'upd_db':
                    #print('self api in upd' + self.api)
                    params = {'api_ep': self.api,
                              'options': {
                                  'symbol': self.symbol,  # str(collection.full_name).split('.')[0]
                                  'interval': self.interval,
                                  'startTime': get_last_time(self.set_connection_collection()),######вот тут параматры
                                  # надо проверить коллекцию на наличие элементов, потом грузить в время или начальное время 2015,,,2017maybe mongoindexes? calling function bad idea not pep8? fixed:put dict to this func
                                  'endTime': None,
                                  'limit': 1000,
                              }}
                    #print(type(params['api_ep']))
                    return params
                case 'buy_mrkt':
                    params = {
                        'quantity': self.qntty,
                        'side': 'BUY',
                        'symbol': self.symbol,
                        'timestamp': int(time.time() * 1000),
                        'type': 'MARKET',
                    }
                case 'sel_mrkt':
                    params = {
                        'quantity': self.qntty,
                        'side': 'SELL',
                        'symbol': self.symbol,
                        'timestamp': int(time.time() * 1000),
                        'type': 'MARKET',
                    }

        except:
            params = 'not valid parameters for this action'
            print('not valid parameters for this action')
            return params

# async def get_last_indicator_value(collection:Collection, indicator:str):
#     indicator_name = collection.name + indicator
#     indicator_value = collection.find_one(sort=[('open_time', pymongo.DESCENDING)])[indicator_name]
#     if indicator_value:


async def db_updater(params:dict=DEFAULT_PARAMS):
    session = paramsHelper(params)
    collection1 = session.set_connection_collection()
    while True:
        if collection1.estimated_document_count() != 0:
                # print(session.generate_params(action='upd_db'))
                update_params = session.generate_params(action='upd_db')
                updates_list = get_stock_data(update_params)
                collection1.insert_many(updates_list)
                print('database updated, current elements count:>>>>' + str(collection1.estimated_document_count()))
                await asyncio.sleep(5)

        else:
            init_params = session.generate_params(action='init_db')
            updates_list = get_stock_data(init_params)
            collection1.insert_many(updates_list)
            #print(updates_list)
            print('init passed')
            print('database initialised, current elements count:>>>>' + str(collection1.estimated_document_count()))

async def trader(params:dict=DEFAULT_PARAMS):
    session = paramsHelper(params)
    collection1 = session.set_connection_collection()
    rsi = get_last_indicator_value(collection1)

async def main():
    task_update = asyncio.create_task(db_updater())
    await asyncio.gather(task_update)

# async def trader(params:dict=DEFAULT_PARAMS):
if __name__ == '__main__':
    asyncio.run(main())

