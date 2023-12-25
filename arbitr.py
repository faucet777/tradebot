import asyncio
import json
# import datetime
import aiohttp
# import websockets
from aiohttp import WSMessage

okex_data = {"op": "subscribe", "args": [{"channel": "tickers", "instId": 'BTC-USDT', }, ]}
url_binance = 'wss://stream.binance.com:9443/stream?streams=btcusdt@miniTicker'
url_okx = 'wss://ws.okex.com:8443/ws/v5/public'


async def handler(msg, stream):
    print('handler >>>>>>msg>>', msg,stream)
    try:
        value = float(msg)
        return [value, stream]
    except:
        return [str(msg), stream]


async def bin_ws(session: aiohttp.ClientSession, q: asyncio.Queue, url=url_binance):
    async with session.ws_connect(url) as ws:
        async for msg in ws:
            try:
                close_price = json.loads(msg.data)['data']['c']
                value = await handler(close_price, 'BINWS')
                q.put_nowait(value)
                print('BINANSE WS q puted size>>', q.qsize(), value)
            except:
                print('BINANSE WS ERR>>>', close_price)
                continue


async def okex_ws(session: aiohttp.ClientSession, q: asyncio.Queue, data: dict = okex_data, url: str = url_okx):
    async with session.ws_connect(url) as ws:
        await ws.send_json(data)
        # response = ws.receive(timeout=2)
        print('RESPONSE_OKX>>>')
        async for msg in ws:
            try:
                last = json.loads(msg.data)
                last = last['data'][0]['last']
                value = await handler(last, 'OKXWS')
                q.put_nowait(value)
                print('OKX WS q puted size>>', q.qsize(), value)
            except Exception as e:
                print('OKX_EXEPTION>>', e, 'msg okx ws>>>', msg)
                continue

            await asyncio.sleep(1)


async def calc(q: asyncio.Queue):
    while True:
        await asyncio.sleep(1)
        print('CALC')
        try:
            a = q.get_nowait()
            # print('a>',a)
            b = q.get_nowait()
            # print('b>', b)

            if a[1] != b[1]:
                dif = float(a[0]) - float(b[0])
                print('calc dif>>>', dif)
                if dif > 100 or dif < -100:
                    print('DEAL!!!DEAL!!!DEAL!!!')
                # return dif
            else:
                print('calc same streams>>a=',a[1],'  b=',b[1])
        except Exception as e:
            print('calc Ex>>', e)
            continue
            # return [a,b]







async def main():
    qu = asyncio.Queue()
    aiosession = aiohttp.ClientSession()
    tasks = [bin_ws(aiosession, qu), okex_ws(aiosession, qu), calc(qu)]
    await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == '__main__':
    asyncio.run(main())
