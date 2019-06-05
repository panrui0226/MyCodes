# usr/bin/env python3
# -*- coding:utf-8 -*-


import json
from CMCTrader.CMCTraderMac import CMCTrader
from Strategies.StrategyDoubleMA import StrategyDoubleMA


if __name__ == '__main__':
    file = open('TradingConfig.cfg')
    cfg_file = json.load(file)
    trader = CMCTrader(cfg_file)
    trader.start_trading(StrategyDoubleMA)