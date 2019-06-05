# usr/bin/env python3
# -*- coding:utf-8 -*-
from ArrayManager import TickArrayManager


class StrategyWaveCrest:
    def __init__(self):
        self.tam = TickArrayManager(frequency=5, size=20)
        self.window = []
        # 参数
        self.units = 500
        self.stopLoss = 0.1
        self.takeProfit = 0.08
        # 变量
        self.posLong = 0
        self.posShort = 0
        self.transaction = 0

    def return_signal(self, bid, ask):
        signal = [0, 0]
        self.tam.update_bar(bid=bid, ask=ask)
        last_price = (bid + ask)/2.0

        if len(self.tam.close) > 10:
            ma5 = list(self.tam.sma(n=5, array=True))
            self.window = ma5[len(ma5)-5:]

            max_value = max(self.window)
            min_value = min(self.window)
            first_value = self.window[0]
            last_value = self.window[-1]

            long = first_value > min_value and last_value - min_value >= 0.02 and max_value == last_value
            short = first_value < max_value and max_value - last_value >= 0.02 and min_value == last_value

            # 平
            if self.posLong > 0:
                if last_price - self.transaction > self.takeProfit:
                    self.transaction = self.transaction + self.takeProfit
                elif self.transaction - last_price >= self.stopLoss:
                    signal = [-1, self.units]
                    self.posLong = 0
                    # 平仓条件出发后不执行开仓条件判断
                    long = False
                    short = False

            if self.posShort > 0:
                if self.transaction - last_price > self.takeProfit:
                    self.transaction = self.transaction - self.takeProfit
                elif last_price - self.transaction >= self.stopLoss:
                    signal = [1, self.units]
                    self.posShort = 0
                    # 平仓条件出发后不执行开仓条件判断
                    long = False
                    short = False

            # 开
            if self.posLong == 0 and self.posShort == 0:
                if long:
                    signal = [1, self.units]
                    self.transaction = last_price
                    self.posLong = 1
                elif short:
                    signal = [-1, self.units]
                    self.transaction = last_price
                    self.posShort = 1

        return signal
