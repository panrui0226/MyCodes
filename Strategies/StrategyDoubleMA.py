from ArrayManager.ArrayManager import TickArrayManager


class StrategyDoubleMA(object):
    def __init__(self):
        self.tam = TickArrayManager(frequency=60, size=20)
        # 策略参数
        self.adj_factor = 0.999
        self.units = 200
        # 策略变量
        self.posLong = 0
        self.posShort = 0

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
            diff0_cross = ma_5[-5] - ma_11[-5]
            diff1_cross = ma_5[-4] - ma_11[-4]
            diff2_cross = ma_5[-3] - ma_11[-3]
            diff3_cross = ma_5[-2] - ma_11[-2]
            diff4_cross = ma_5[-1] - ma_11[-1]

            # golden_cross = diff2_cross < 0 < diff3_cross
            # death_cross = diff3_cross < 0 < diff2_cross

            if self.posLong == 1:
                # if death_cross:
                #     signal = [-1, self.units]
                #     self.posLong = 0
                if tam.last_price() <= ma_11[-1] * self.adj_factor:
                    signal = [-1, self.units]
                    self.posLong = 0

            elif self.posShort == 1:
                # if golden_cross:
                #     signal = [1, self.units]
                #     self.posShort = 0
                if tam.last_price() >= ma_11[-1] * (1/self.adj_factor):
                    signal = [1, self.units]
                    self.posShort = 0

            elif self.posLong == 0 and self.posShort == 0:
                long = diff4_cross > diff3_cross > diff2_cross > diff1_cross > 0 > diff0_cross
                short = diff4_cross < diff3_cross < diff2_cross < diff1_cross < 0 < diff0_cross
                long_filter = ma_5[-1] > ma_5[-2] > ma_5[-3] > ma_5[-4] and ma_11[-1] >= ma_11[-2]
                short_filter = ma_5[-1] < ma_5[-2] < ma_5[-3] < ma_5[-4] and ma_11[-1] <= ma_11[-2]

                if long and long_filter:
                    signal = [1, self.units]
                    self.posLong = 1

                elif short and short_filter:
                    signal = [-1, self.units]
                    self.posShort = 1

            else:
                print('Unexpected error, please interrupt the program immediately.')

        else:
            pass

        return signal
