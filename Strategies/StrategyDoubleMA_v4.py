# usr/bin/env python3
# -*- coding:utf-8 -*-

from ArrayManager.ArrayManager import TickArrayManager
from OandaClient.OandaClient import Oanda
import pandas as pd


class StrategyDoubleMA(object):
    def __init__(self, use_oanda_data=False):
        self.tam = TickArrayManager(frequency=60, size=100)
        # 策略参数
        self.adj_factor = 0.999
        self.units = 200
        self.stop_loss_point = 1
        self.take_profit_point = 0.7
        self.bound_factor = 1.96
        # 策略变量
        self.posLong = 0
        self.posShort = 0
        self.transaction = 0
        self.on_trading_list = []
        self.upper_list = []
        self.lower_list = []
        # 历史数据初始化
        if use_oanda_data:
            try:
                practice = Oanda("c21945e45c3573a926278f59a3522ffd-2d71c89fb810289c58a4827a9eb21156",
                                "https://api-fxpractice.oanda.com/v3/",
                                "https://stream-fxpractice.oanda.com/v3/")
                candles = practice.getOandaCandles(instrument="XAU_USD", granularity="M1", count=100)
                self.tam.high = list(candles['high'].astype(float))
                self.tam.low = list(candles['low'].astype(float))
                self.tam.close = list(candles['close'].astype(float))
                print('Onada Data Has Been Acquired Successfully!')
            except Exception as e:
                print('Onada Data Acquired Failed! %s' % e)
        else:
            pass

    def return_signal(self, ask, bid):
        signal = [0, 0]
        tam = self.tam
        tam.update_bar(ask, bid)

        if len(tam.close) > 50:
            # 参数计算
            sigma = list(pd.Series(tam.close).rolling(50).std())
            avg_price = list(pd.Series(tam.close).rolling(50).mean())

            upper_bound = float(avg_price[-1]) + float(sigma[-1]) * self.bound_factor
            lower_bound = float(avg_price[-1]) - float(sigma[-1]) * self.bound_factor

            self.upper_list.append(upper_bound)
            self.lower_list.append(lower_bound)

            if len(self.upper_list) == len(self.lower_list) and len(self.upper_list) >= 2:
                # 开仓
                if self.posLong == 0 and self.posShort == 0:
                    if tam.close[-2] > self.upper_list[-2] and tam.close[-1] < self.upper_list[-1]:
                        signal = [-1, self.units]
                        self.posShort = 1
                        self.transaction = tam.last_price
                        self.on_trading_list.append(self.transaction)
                    elif tam.close[-2] < self.lower_list[-2] and tam.close[-1] > self.lower_list[-1]:
                        signal = [1, self.units]
                        self.posLong = 1
                        self.transaction = tam.last_price
                        self.on_trading_list.append(self.transaction)
                # 多头监控
                elif self.posLong == 1 and self.posShort == 0:
                    max_value = max(self.on_trading_list)
                    if max_value - tam.last_price > self.take_profit_point:
                        signal = [-1, self.units]
                        self.posLong = 0
                        self.on_trading_list = []
                    elif self.transaction - tam.last_price >= self.stop_loss_point:
                        signal = [-1, self.units]
                        self.posLong = 0
                        self.on_trading_list = []
                # 空头监控
                elif self.posShort == 1 and self.posLong == 0:
                    min_value = min(self.on_trading_list)
                    if tam.last_price - min_value > self.take_profit_point:
                        signal = [1, self.units]
                        self.posShort = 0
                        self.on_trading_list = []
                    elif tam.last_price - self.transaction >= self.stop_loss_point:
                        signal = [1, self.units]
                        self.posShort = 0
                        self.on_trading_list = []

        return signal
