# usr/bin/env python3
# -*- coding:utf-8 -*-

"""
This class is used to record ask and bid price data that transmit in real time.

Created on May 31, 2019
@author Rui.Pan
"""

import numpy as np
import talib as ta


class TickArrayManager(object):
    def __init__(self, frequency: int, size: int):
        self.frequency = frequency
        self.size = size
        self.ask = 0
        self.bid = 0
        self.mid = 0
        self.last_price = 0

        self.tick_list = []
        self.ask_list = []
        self.bid_list = []
        self.mid_list = []
        self.high_list = []
        self.low_list = []
        self.close_list = []

    def update_tick(self, ask, bid):
        self.ask = float(ask)
        self.bid = float(bid)
        self.mid = (ask + bid) / 2.0
        self.last_price = (ask + bid) / 2.0

        if len(self.tick_list) < self.frequency:
            self.tick_list.append(self.mid)
        elif len(self.tick_list) == self.frequency:
            self.ask_list.append(self.ask)
            self.bid_list.append(self.bid)
            self.mid_list.append(self.mid)
            self.high_list.append(max(self.mid_list))
            self.low_list.append(min(self.mid_list))
            self.close_list.append(self.mid_list[-1])
            self.tick_list = []
            self.tick_list.append(self.mid)
        else:
            print('Unexpected error: the length of tick list should not lager than frequency')

        all_lists = [self.ask_list, self.bid_list, self.mid_list, self.high_list, self.low_list, self.close_list]

        for single_list in all_lists:
            if len(single_list) > self.size:
                single_list = single_list[len(single_list) - self.size:]
            else:
                pass

    def sma(self, n, array=False):
        if array:
            return list(ta.SMA(np.array(self.close_list), n))
        else:
            return ta.SMA(np.array(self.close_list), n)[-1]
