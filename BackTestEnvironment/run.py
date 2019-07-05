# usr/bin/env python3
# -*- coding:utf-8 -*-
from BackTestEnvironment.BackTestMoudle import *
from Strategies.StrategyDoubleMA import StrategyDoubleMA

if __name__ == "__main__":
    strategy = StrategyDoubleMA()
    cfg = BackTestConfig(strategy=strategy, initial_cash=1000, open_amount=100,
                         data_path=r'DataFiles/back_test_data.csv', date_column='datetime', close_column='close')
    run_back_test(cfg)
