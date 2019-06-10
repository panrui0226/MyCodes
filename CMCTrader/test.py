from CMCTrader.CMCTraderMac import CMCTrader
import json
from OandaClient.OandaClient import Oanda
import pandas as pd
import numpy as np

trader = CMCTrader(json.load(open('Trader.cfg')))
trader.open()
ask, bid = trader.get_ask_bid()
print(ask, bid)

# practice = Oanda("c21945e45c3573a926278f59a3522ffd-2d71c89fb810289c58a4827a9eb21156",
#         "https://api-fxpractice.oanda.com/v3/",
#         "https://stream-fxpractice.oanda.com/v3/")
# candles = practice.getOandaCandles(instrument="XAU_USD", granularity="S5",count=50)
# ID = practice.getOandaAccount()[0]["id"]
# a = practice.getOandaAccountInstruments(ID)
# pd.set_option('display.max_row', None)
# pd.set_option('display.max_column', None)


