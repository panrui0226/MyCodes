# usr/bin/env python3
# -*- coding:utf-8 -*-

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class BackTestConfig(object):
    def __init__(self, strategy, initial_cash, open_amount, data_path, date_column, close_column):
        self.strategy = strategy
        self.initial_cash = initial_cash
        self.open_amount = open_amount
        self.data_path = data_path
        self.date_column = date_column
        self.close_column = close_column


def run_back_test(cfg):
    back_test_data = pd.read_csv(cfg.data_path)
    back_test_data['datetime'] = pd.to_datetime(back_test_data[cfg.date_column])
    back_test_data['signal'] = np.nan
    back_test_data['capital'] = np.nan
    back_test_data['trading_info'] = 0
    back_test_data['P&L'] = 0

    for i in range(len(back_test_data)):
        ask = float(back_test_data.loc[i][cfg.close_column])
        bid = float(back_test_data.loc[i][cfg.close_column])
        signal = cfg.strategy.return_signal(ask=ask, bid=bid)[0]
        back_test_data.loc[i, ['signal']] = signal

    is_trading = False
    cash = cfg.initial_cash
    last_open = 0

    for i in range(len(back_test_data)):
        price = float(back_test_data.loc[i][cfg.close_column])
        signal = float(back_test_data.loc[i]['signal'])
        if not is_trading:
            if signal == 0.0:
                back_test_data.loc[i, ['capital']] = cash
            if signal == 1.0:
                contract_value = price * cfg.open_amount
                cash -= contract_value
                capital = cash + contract_value
                back_test_data.loc[i, ['capital']] = capital
                back_test_data.loc[i, ['trading_info']] = "Buy Open"
                last_open = i
                is_trading = True
            if signal == -1.0:
                contract_value = price * cfg.open_amount
                cash -= contract_value
                capital = cash + contract_value
                back_test_data.loc[i, ['capital']] = capital
                back_test_data.loc[i, ['trading_info']] = "Short Open"
                last_open = i
                is_trading = True
        elif is_trading:
            if signal == 0.0:
                contract_value = price * cfg.open_amount
                capital = cash + contract_value
                back_test_data.loc[i, ['capital']] = capital
            elif signal == -1.0 or signal == 1.0:
                contract_value = price * cfg.open_amount
                capital = cash + contract_value
                back_test_data.loc[i, ['capital']] = capital
                cash = capital
                is_trading = False
                if signal == 1.0:
                    back_test_data.loc[i, ['trading_info']] = "Cover Close"
                    back_test_data.loc[i, ['P&L']] = round(back_test_data.loc[i]['capital'] - back_test_data.loc[
                        last_open]['capital'], 3)
                elif signal == -1.0:
                    back_test_data.loc[i, ['trading_info']] = "Sell Close"
                    back_test_data.loc[i, ['P&L']] = round(back_test_data.loc[i]['capital'] - back_test_data.loc[
                        last_open]['capital'], 3)

    trading_info_df = back_test_data[back_test_data['trading_info'] != 0]
    trading_info_df = trading_info_df[['datetime', 'trading_info', 'P&L']]
    trading_info_df.reset_index(drop=True, inplace=True)

    back_test_data.set_index(['datetime'], drop=True, inplace=True)
    #
    back_test_data['capital'].plot()
    plt.show()
    #
    trading_info_df.to_csv(r'DataFiles\trading_info.csv')
