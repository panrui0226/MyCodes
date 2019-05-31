# usr/bin/env python3
# -*- coding:utf-8 -*-

import numpy as np
import talib


class TickArrayManager(object):
    def __init__(self, high, low, close, frequency: int = 10, size: int = 10):
        self.high = high
        self.low = low
        self.close = close
        self.frequency = frequency
        self.size = size
        self.tick_data = []

    def update_bar(self,  bid, ask):
        mid = (bid + ask)/2.0

        if len(self.tick_data) < self.frequency:
            self.tick_data.append(mid)
        else:
            self.high.append(max(self.tick_data))
            self.low.append(min(self.tick_data))
            self.close.append(self.tick_data[-1])
            self.tick_data = []

        if len(self.close) > self.size:
            self.high = self.high[len(self.high) - self.size:]
            self.low = self.low[len(self.low) - self.size:]
            self.close = self.close[len(self.close) - self.size:]
        else:
            pass

    def high(self):
        return self.high()

    def low(self):
        return self.low()

    def close(self):
        return self.close()

    def atr(self, n: int, array=True):
        result = talib.ATR(np.array(self.high), np.array(self.low), np.array(self.close), n)
        if array:
            return result
        else:
            return result[-1]

    def sma(self, n, array=False):
        result = talib.SMA(self.close, n)
        if array:
            return result
        else:
            return result[-1]

    def std(self, n, array=False):
        result = talib.STDDEV(self.close, n)
        if array:
            return result
        else:
            return result[-1]

    def cci(self, n, array=False):
        result = talib.CCI(self.high, self.low, self.close, n)
        if array:
            return result
        else:
            return result[-1]

    def rsi(self, n, array=True):
        result = talib.RSI(self.close, n)
        if array:
            return result
        else:
            return result[-1]

    def macd(self, fast_period, slow_period, signal_period, array=False):
        macd, signal, hist = talib.MACD(
            self.close, fast_period, slow_period, signal_period
        )
        if array:
            return macd, signal, hist
        else:
            return macd[-1], signal[-1], hist[-1]

    def adx(self, n, array=False):
        result = talib.ADX(self.high, self.low, self.close, n)
        if array:
            return result
        else:
            return result[-1]

    def boll(self, n, dev, array=False):
        mid = self.sma(n, array)
        std = self.std(n, array)
        up = mid + std * dev
        down = mid - std * dev
        return up, down

    def keltner(self, n, dev, array=False):
        mid = self.sma(n, array)
        atr = self.atr(n, array)
        up = mid + atr * dev
        down = mid - atr * dev
        return up, down

    def donchian(self, n, array=False):
        up = talib.MAX(self.high, n)
        down = talib.MIN(self.low, n)
        if array:
            return up, down
        else:
            return up[-1], down[-1]
