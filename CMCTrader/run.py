# usr/bin/env python3
# -*- coding:utf-8 -*-


import json
from CMCTrader.CMCTraderMac import CMCTrader
from Strategies.StrategyDoubleMA import StrategyDoubleMA
from Strategies.StrategyDoubleMA_v4 import StrategyDoubleMA


if __name__ == '__main__':
    file = open('Trader.cfg')
    cfg_file = json.load(file)
    trader = CMCTrader(cfg_file)
    strategy = StrategyDoubleMA(use_oanda_data=True)
    trader.start_trading(strategy)