# usr/bin/env python3
# -*- coding:utf-8 -*-
from ArrayManager.ArrayManager_v2 import TickArrayManager
from OandaClient.OandaClient import Oanda
import pandas as pd
import math

'''
这一版功能基本成型，但是没有将波动率的大小考虑进去
这一点是存在改进空间的地方
还有一点就是止盈止损的设置比较粗糙，这也是很重要的需要改进的一个点
'''


class StrategyJ10(object):
    def __init__(self, use_history_data=True):
        # 初始化数据管理器
        self.granularity = 'M1'
        self.tam = TickArrayManager(frequency=60, size=120)
        # 账户信息
        self.available_margin = 5000.0                  # 可用资金
        self.leverage = 200.0                           # 杠杆比率
        # 风险偏好参数
        self.take_profit_point = 1.2                      # 重置止损价格点数&最大回撤点数
        self.single_maximum_loss_ratio = 0.015          # 最大单次亏损比率
        self.sigma_factor = 1.96
        self.sigma_of_sigma_factor = 0
        self.max_open_lots = 200                        # 最大开仓量保险栓
        # 合约信息
        self.instrument = "黄金"
        self.code = "XAU_USD"
        self.least_change_unit = 0.01                   # 合约价格最小变动单位
        self.spread = 0.3                               # 买卖价差

        # 策略参数
        self.rolling = 50                               # 计算周期
        # 计数
        self.check_initial_data_count = 0
        self.check_close_half_count = 0
        # 策略变量
        self.posLong = 0
        self.posShort = 0
        self.contract_value = 0     # 合约价值
        self.transaction = 0
        self.stop_loss_price = 0
        self.single_maximum_loss_amount = self.available_margin * self.single_maximum_loss_ratio
        self.initial_margin = 0         # 初始保证金
        # 列表
        self.upper_list = []
        self.lower_list = []
        self.on_trading_list = []

        if use_history_data:
            practice = Oanda("c21945e45c3573a926278f59a3522ffd-2d71c89fb810289c58a4827a9eb21156",
                             "https://api-fxpractice.oanda.com/v3/",
                             "https://stream-fxpractice.oanda.com/v3/")
            try:
                candles = practice.getOandaCandles(instrument=self.code, granularity=self.granularity, count=120)
                self.tam.close_list = list(candles['close'].astype(float))
                self.tam.high_list = list(candles['high'].astype(float))
                self.tam.low_list = list(candles['low'].astype(float))
                # sigma = list(pd.Series(self.tam.close_list).rolling(self.rolling).std())
                print('History Data Has Been Acquired Successfully!')
            except Exception as e:
                print('History Data Acquired Failed: %s' % e)
                pass

        # 信息确认
        print("本次交易可动用资金：%s \n杠杆比率：1/%s \n单次交易最大亏损比率：%s \n交易品种：%s \n品种代码：%s" %
              (self.available_margin, self.leverage, self.single_maximum_loss_ratio, self.instrument, self.code))

    # ------------------------------------------------------------------------------------------------------------------
    #
    def return_signal(self, ask, bid):
        signal = [0, 0]
        tam = self.tam
        tam.update_tick(ask=ask, bid=bid)

        # 检验数据完整性，只检验一次
        while self.check_initial_data_count == 0:
            if len(tam.close_list) > self.rolling:
                print("Initialization Calculation Requirements Have Been Met! Start Monitoring Real-Time Quotes!")
                pass
            else:
                print("The Amount of Data Does not Meet The Initialization Calculation requirements! "
                      "Start Receiving Real-Time Data!")
                pass
            self.check_initial_data_count += 1

        try:
            sigma = list(pd.Series(tam.close_list).rolling(self.rolling).std())
            # sigma_of_sigma = list(pd.Series(sigma).rolling(self.rolling).std())
            mean = list(pd.Series(tam.close_list).rolling(self.rolling).mean())
            # mean_of_sigma = list(pd.Series(sigma).rolling(self.rolling).mean())

            upper_bound = mean[-1] + sigma[-1] * self.sigma_factor
            self.upper_list.append(upper_bound)
            lower_bound = mean[-1] - sigma[-1] * self.sigma_factor
            self.lower_list.append(lower_bound)

            # upper_sigma_of_sigma = mean_of_sigma[-1] + sigma_of_sigma[-1] * self.sigma_of_sigma_factor
            # lower_sigma_of_sigma = mean_of_sigma[-1] - sigma_of_sigma[-1] * self.sigma_of_sigma_factor

            list_list = [self.upper_list, self.lower_list]
            for lists in list_list:
                if len(lists) > 2:
                    lists = lists[len(lists)-2:]

            if len(self.upper_list) >= 2:
                buy = tam.close_list[-1] > self.lower_list[-1] and tam.close_list[-2] < self.lower_list[-2]
                short = tam.close_list[-1] < self.upper_list[-1] and tam.close_list[-2] > self.upper_list[-2]
            else:
                buy = False
                short = False
            # high_vol = sigma[-1] >= upper_sigma_of_sigma
            # mid_vol = lower_sigma_of_sigma < sigma[-1] < upper_sigma_of_sigma
            # low_vol = sigma[-1] <= lower_sigma_of_sigma

            # ----------------------------------------------------------------------------------------------------------
            # 多头监控
            if self.posLong > 0:
                self.on_trading_list.append(tam.last_price)
                # 触线止损，全平
                if tam.last_price < self.stop_loss_price:
                    signal = [-1, self.posLong]
                    self.posLong = 0
                    self.check_close_half_count = 0
                    self.on_trading_list = []
                    print("卖平 \n触发止损价格，全平: %s" % self.posLong)
                # 调整止损价
                elif tam.last_price - self.transaction >= self.take_profit_point:
                    self.stop_loss_price = max(self.on_trading_list) - self.take_profit_point
                    # print("止损价格调整为: %s" % self.stop_loss_price)
                # 价格回归，平半仓
                elif tam.last_price > mean[-1] and self.check_close_half_count == 0:
                    signal = [-1, math.ceil(self.posLong/2.0)]
                    self.posLong -= math.ceil(self.posLong/2.0)
                    self.check_close_half_count = 1
                    print("卖平 \n平半仓，剩余仓位: %s" % self.posLong)

            # 空头监控
            if self.posShort > 0:
                self.on_trading_list.append(tam.last_price)
                # 触线止损，全平
                if tam.last_price > self.stop_loss_price:
                    signal = [1, self.posShort]
                    self.posShort = 0
                    self.check_close_half_count = 0
                    self.on_trading_list = []
                    print("买平 \n触发止损价格，全平: %s" % self.posShort)
                # 调整止损价
                elif self.transaction - tam.last_price >= self.take_profit_point:
                    self.stop_loss_price = min(self.on_trading_list) + self.take_profit_point
                    # print("止损价格调整为: %s" % self.stop_loss_price)
                # 价格回归，平半仓
                elif tam.last_price < mean[-1] and self.check_close_half_count == 0:
                    signal = [1, math.ceil(self.posShort/2.0)]
                    self.posShort -= math.ceil(self.posShort/2.0)
                    self.check_close_half_count = 1
                    print("买平 \n平半仓，剩余仓位: %s" % self.posShort)

            # ----------------------------------------------------------------------------------------------------------
            # 开仓
            if self.posLong == 0 and self.posShort == 0:
                if buy:
                    self.stop_loss_price = min(tam.low_list[len(tam.low_list) - 5:])
                    try:
                        profit_loss_ratio = (mean[-1] - tam.last_price)/(tam.last_price - self.stop_loss_price)
                    # 如果tam.last_price - self.stop_loss_price = 0
                    except:
                        profit_loss_ratio = 100
                    if profit_loss_ratio >= 1:
                        stop_loss_point = tam.last_price - self.stop_loss_price
                        open_lots = math.floor(self.single_maximum_loss_amount / stop_loss_point)
                        if open_lots >= self.max_open_lots:
                            signal = [1, self.max_open_lots]
                            self.posLong += self.max_open_lots
                            self.transaction = tam.last_price
                            self.contract_value = self.posLong * self.transaction
                            self.initial_margin = self.contract_value / self.leverage
                            self.on_trading_list.append(self.transaction)
                            # 交易信息
                            print("买开 \n理论开仓: %s，实际开仓: %s \n成交价: %s，止损价: %s \n合约价值: %s \n预估保证金占用: "
                                  "%s \n预估盈亏比: %s" % (open_lots, self.max_open_lots, self.transaction,
                                                      self.stop_loss_price, self.contract_value, self.initial_margin,
                                                      profit_loss_ratio))
                        elif 0 < open_lots < self.max_open_lots:
                            signal = [1, open_lots]
                            self.posLong += open_lots
                            self.transaction = tam.last_price
                            self.contract_value = self.posLong * self.transaction
                            self.initial_margin = self.contract_value / self.leverage
                            self.on_trading_list.append(self.transaction)
                            # 交易信息
                            print("买开 \n理论开仓: %s，实际开仓: %s \n成交价: %s，止损价: %s \n合约价值: %s \n预估保证金占用: "
                                  "%s \n预估盈亏比: %s" % (open_lots, open_lots, self.transaction, self.stop_loss_price,
                                                      self.contract_value, self.initial_margin, profit_loss_ratio))

                elif short:
                    self.stop_loss_price = max(tam.high_list[len(tam.high_list)-5:])
                    try:
                        profit_loss_ratio = (tam.last_price - mean[-1])/(self.stop_loss_price - tam.last_price)
                    except:
                        # 如果self.stop_loss_price - tam.last_price = 0
                        profit_loss_ratio = 100
                    if profit_loss_ratio >= 1:
                        stop_loss_point = self.stop_loss_price - tam.last_price
                        open_lots = math.floor(self.single_maximum_loss_amount / stop_loss_point)
                        if open_lots > self.max_open_lots:
                            signal = [-1, self.max_open_lots]
                            self.posShort += self.max_open_lots
                            self.transaction = tam.last_price
                            self.contract_value = self.posShort * self.transaction
                            self.initial_margin = self.contract_value / self.leverage
                            self.on_trading_list.append(self.transaction)
                            # 交易信息
                            print("卖开 \n理论开仓: %s，实际开仓: %s \n成交价: %s，止损价: %s \n合约价值: %s \n预估保证金占用: "
                                  "%s \n预估盈亏比: %s" % (open_lots, self.max_open_lots, self.transaction,
                                                      self.stop_loss_price, self.contract_value, self.initial_margin,
                                                      profit_loss_ratio))
                        elif 0 < open_lots < self.max_open_lots:
                            signal = [-1, open_lots]
                            self.posShort += open_lots
                            self.transaction = tam.last_price
                            self.contract_value = self.posShort * self.transaction
                            self.initial_margin = self.contract_value / self.leverage
                            self.on_trading_list.append(self.transaction)
                            # 交易信息
                            print("买开 \n理论开仓: %s，实际开仓: %s \n成交价: %s，止损价: %s \n合约价值: %s \n预估保证金占用: "
                                  "%s \n预估盈亏比: %s" % (open_lots, open_lots, self.transaction, self.stop_loss_price,
                                                      self.contract_value, self.initial_margin, profit_loss_ratio))

        except Exception as e:
            print("Strategy Unexpected Error: %s" % e)

        return signal


