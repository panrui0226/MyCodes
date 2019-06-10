from ArrayManager.ArrayManager import TickArrayManager
from OandaClient.OandaClient import Oanda


class StrategyDoubleMA(object):
    def __init__(self, use_oanda_data=False):
        self.tam = TickArrayManager(frequency=60, size=20)
        # 策略参数
        self.adj_factor = 0.999
        self.units = 200
        self.stop_loss_point = 0.15
        # 策略变量
        self.posLong = 0
        self.posShort = 0
        self.transaction = 0
        self.on_trading_list = []
        # 历史数据初始化
        if use_oanda_data:
            try:
                practice = Oanda("c21945e45c3573a926278f59a3522ffd-2d71c89fb810289c58a4827a9eb21156",
                                "https://api-fxpractice.oanda.com/v3/",
                                "https://stream-fxpractice.oanda.com/v3/")
                candles = practice.getOandaCandles(instrument="WTICO_USD", granularity="M1", count=20)
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
        tam.update_bar(ask=float(ask), bid=float(bid))

        ma_5 = []
        ma_11 = []

        if len(tam.close) > 11:
            ma_5 = tam.sma(5, array=True)
            ma_11 = tam.sma(11, array=True)

        # 检查数据完整性
        if len(ma_11) >= 5:
            print(ma_5[-1])
            print(ma_11[-1])

            diff2_cross = ma_5[-2] - ma_11[-2]
            diff1_cross = ma_5[-1] - ma_11[-1]

            diff_fast = ma_5[-1] - ma_5[-2]
            diff_slow = ma_11[-1] - ma_11[-2]

            golden_cross = diff2_cross < 0 < diff1_cross and diff_fast > 0 > diff_slow
            death_cross = diff1_cross < 0 < diff2_cross and diff_fast < 0 < diff_slow

            # 平多
            if self.posLong == 1 and self.posShort == 0:
                self.on_trading_list.append(tam.last_price)
                stop_loss = max(self.on_trading_list) - self.stop_loss_point
                if tam.last_price < stop_loss:
                    signal = [-1, self.units]
                    self.posLong = 0
                    self.on_trading_list = []
                elif tam.last_price() <= ma_11[-1] * self.adj_factor:
                    signal = [-1, self.units]
                    self.posLong = 0
                    self.on_trading_list = []
            # 平空
            elif self.posShort == 1 and self.posLong == 0:
                self.on_trading_list.append(tam.last_price)
                stop_loss = min(self.on_trading_list) + self.stop_loss_point
                if tam.last_price > stop_loss:
                    signal = [1, self.units]
                    self.posShort = 0
                    self.on_trading_list = []
                elif tam.last_price() >= ma_11[-1] * (1/self.adj_factor):
                    signal = [1, self.units]
                    self.posShort = 0
                    self.on_trading_list = []
            # 开仓
            elif self.posLong == 0 and self.posShort == 0:
                if golden_cross:
                    signal = [1, self.units]
                    self.posLong = 1
                    self.transaction = tam.last_price
                    self.on_trading_list.append(tam.last_price)
                elif death_cross:
                    signal = [-1, self.units]
                    self.posShort = 1
                    self.transaction = tam.last_price
                    self.on_trading_list.append(tam.last_price)
            # 不可能事件
            else:
                print('Unexpected Error! Please Interrupt The Program Immediately!')

        else:
            pass

        return signal
