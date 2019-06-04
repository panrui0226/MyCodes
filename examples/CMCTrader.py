from Crawler import Crawler
import time
from datetime import datetime
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from random import randint, random
from SignalGenerator4 import Classifier
from strategyDoubleMA import StrategyEIA
import numpy as np
import datetime as dt


class CMCTrader:
    def __init__(self, b_type='Chrome', username='blanksweet@163.com', pwd='Blank123'):
        if 'simas' in username:
            print('This is the real account. Please be cautious while trading. semiAuto mode is recommended.')
        self.controller = Crawler(type=b_type)
        self.browser = None
        self.username = username
        self.pwd = pwd
        self.strategy = None

    def quit(self):
        if self.browser is not None:
            self.browser.quit()
            self.browser = None

    def close_all_window(self):
        d = self.browser
        close_list = d.find_elements_by_xpath('//div[@class="feature feature-next-gen-order-ticket"]//'
                                              'button[@class="header-item__button close-button" and @title="关闭"]')
        for c in close_list:
            try:
                c.click()
            except WebDriverException:
                print('There are windows that can\'t be closed. Please close them all manually.')
                continue

    def open(self, i=0):
        if i > 5:
            print('Please check your Internet connection. Or maybe cmcmarkets has issued a process.')
        if self.browser is None:
            self.browser = self.controller.open_browser()
        d = self.browser
        try:
            d.get('https://platform.cmcmarkets.com/#/login?b=CMC-CFD&r=CN&l=zh')
        except TimeoutException:
            print('Timeout! Restart')
            self.quit()
            return self.open(i=i+1)
        # Input the account and pwd, check if loading has finished
        while 1:
            current = d.current_url
            if 'https://platform.cmcmarkets.com/#/login' in current:
                print('Loading Finished at', time.ctime())
                try:
                    name = d.find_element_by_id('username')
                    password = d.find_element_by_id('password')
                    name.send_keys(self.username)
                    password.send_keys(self.pwd)
                    time.sleep(0.5)
                    d.find_element_by_xpath('//input[@value="提交"]').click()
                    break
                except NoSuchElementException:
                    d.get('https://platform.cmcmarkets.com/#/login')
        # close the message panel
        flag = 1
        while 1:
            current = d.current_url
            if 'https://platform.cmcmarkets.com/#/app' in current:
                time.sleep(5)
                if flag:
                    start = time.time()
                    flag = 0
                try:
                    d.find_element_by_xpath(
                        '//button[@class="button accept rich-in-platform-'
                        'message-container__button link-new-secondary"]').click()
                except NoSuchElementException:
                    end = time.time()
                    if end - start > 5:
                        break
                    continue
                print('Login Finished at', time.ctime())
                break
        # close all other trading window
        # self.close_all_window()
        return 1

    @staticmethod
    def getsignal(strategy='EIA'):
        # start = time.time()
        # waiting_time = random() * 10
        c = Classifier()
        signal, close_time = c.give_signal(strategy)
        # time.sleep(random()*5)
        # signal = randint(0, 1)
        return signal, close_time

    @staticmethod
    def __output(d, id, signal):
        if id is None:
            suctext = d.find_element_by_xpath('//h6[@ng-bind="::labels.receiptAction"]').text
            protext = d.find_element_by_xpath('//p[@ng-bind="::productName"]').text
            price = d.find_element_by_xpath('//span[@ng-bind-html="::price"]').text
            quant = d.find_element_by_xpath('//span[@ng-bind="::quantity"]').text
        else:
            suctext = d.find_element_by_xpath('//div[@id="%s"]//'
                                              'h6[@ng-bind="::labels.receiptAction"]' % id).text
            protext = d.find_element_by_xpath('//div[@id="%s"]//'
                                              'p[@ng-bind="::productName"]' % id).text
            price = d.find_element_by_xpath('//div[@id="%s"]//span[@ng-bind-html="::price"]' % id).text
            quant = d.find_element_by_xpath('//div[@id="%s"]//span[@ng-bind="::quantity"]' % id).text
        print(suctext, protext)
        print('Your order is finished at', datetime.now())
        print('The product is', protext)
        if signal == 1:
            print('You buy', quant, 'of', protext, 'at', price)
        else:
            print('You sold', quant, 'of', protext, 'at', price)

    def __makeOrder(self, bidbutton, offerbutton, signal, id=None):
        # Submit the Order
        d = self.browser
        if signal == 1 or signal == '1':
            try:
                self.__safely_click(offerbutton)
                print('Offer at', datetime.now())
            except WebDriverException:
                print('You don\'t have enough money in your account.')
        else:
            self.__safely_click(bidbutton)
            print('Bid at', datetime.now())
        # Read trading log
        while 1:
            try:
                yield 0
                self.__output(d, id, signal)
                return 1
            except NoSuchElementException:
                continue

    @staticmethod
    def __dragWindow(d, id, i):
        action = ActionChains(d)
        tar_path = '//div[@id="%s"]/div/header/div[3]/div' % id
        target = d.find_element_by_xpath(tar_path)
        action.click_and_hold(target)
        offsetx = 300
        action.move_by_offset(-450 + i * offsetx, -300)
        action.click(target)
        action.perform()
        time.sleep(0.5)

    def setLossProfit(self, d, id, loss, profit, way):
        d.find_element_by_xpath('//div[@id="%s"]//div[@class="stopLoss"]' % id).click()
        d.find_element_by_xpath('//div[@id="%s"]//div[@class="takeProfit"]' % id).click()
        if way == 'point':
            # Stop Loss Setting
            loss_type = d.find_element_by_xpath('//div[@id="%s"]//div[@class="stopLoss"]//'
                                                'label[@cmc-bind="model.labels.stopLossAmountLabel"]' % id).text
            if '点' not in loss_type:
                # click to switch
                d.find_element_by_xpath('//*[@id="%s"]//*[@button="stopLossAmountLabelButton"]/a' % id).click()
            d.find_element_by_xpath('//div[@id="%s"]//div[@name="stopLossPoints"]' % id).click()
            d.find_element_by_xpath('//div[@id="%s"]//div[@name="stopLossPoints"]' % id).send_keys(loss)
            # Take Profit Setting
            profit_type = d.find_element_by_xpath('//div[@id="%s"]//div[@class="takeProfit"]//'
                                                  'label[@cmc-bind="model.labels.takeProfitAmountLabel"]' % id).text
            if '点' not in profit_type:
                # click to switch
                d.find_element_by_xpath('//*[@id="%s"]//*[@button="takeProfitAmountLabelButton"]/a' % id).click()
            d.find_element_by_xpath('//div[@id="%s"]//div[@name="takeProfitPoints"]' % id).click()
            d.find_element_by_xpath('//div[@id="%s"]//div[@name="takeProfitPoints"]' % id).send_keys(profit)
        return 1

    def __getWindow(self, product_name, prev, approach='sell', num=100, i=0, loss=5, profit=10, way='point'):
        d = self.browser
        d.find_element_by_xpath('//li[@title="打开快速搜索进入产品"]').click()
        search = d.find_elements_by_xpath('//input[@class="search-input-text"]')
        search[0].send_keys(product_name)
        time.sleep(1)
        while 1:
            try:
                d.find_element_by_xpath('//li[@data-id="search-result-0"]').click()
                break
            except NoSuchElementException:
                continue
        time.sleep(1)
        actual = d.find_elements_by_xpath('//div[@class="feature feature-next-gen-order-ticket"]')
        new = [window for window in actual if window not in prev]
        window = new[0]
        id = window.get_attribute('id')
        if approach == 'sell':
            xpath = '//div[@id="%s"]//div[@class="price-box sell"]' % id
            window.find_element_by_xpath(xpath).click()
        elif approach == 'buy':
            xpath = '//div[@id="%s"]//div[@class="price-box buy"]' % id
            window.find_element_by_xpath(xpath).click()
        id = window.get_attribute('id')
        # Input the text
        textpath = '//div[@id="%s"]//div[@contenteditable="true" and @name="quantity"]' % id
        textfield = window.find_element_by_xpath(textpath)
        textfield.send_keys(num)
        textfield.send_keys(Keys.ENTER)
        bid_path = '//div[@id="%s"]//button[@cmc-next-gen-order-ticket-submit-button-tooltip]' % id
        btn = d.find_element_by_xpath(bid_path)
        # drag the window
        self.__dragWindow(d, id, i)
        # set stop loss
        self.setLossProfit(d, id, loss, profit, way)
        return window, btn

    @staticmethod
    def __check_type(product_name, num, loss, profit):
        count = 0
        if type(product_name) == list:
            count += 1
        if type(num) == list:
            count += 1
        if type(loss) == list:
            count += 1
        if type(profit) == list:
            count += 1
        if count == 4:
            return True, count
        else:
            return False, count

    def __get_price(self, id):
        d = self.browser
        while 1:
            bid_price = d.find_element_by_xpath('//div[@id="%s"]//span[@class="price" '
                                                'and @cmc-bind-with-sub="model.bidPrice"]' % id).text
            ask_price = d.find_element_by_xpath('//div[@id="%s"]//span[@class="price" '
                                                'and @cmc-bind-with-sub="model.offerPrice"]' % id).text
            yield bid_price, ask_price

    def close_position(self, signal, close_list, close_windows, trade_time, close_time):
        start = time.time()
        d = self.browser
        avail_money = self.get_available()
        count = 0
        finished_i = []
        # awaiting close position signal and close
        error = 0
        while 1:
            for i in range(0, trade_time):
                if i in finished_i:
                    continue
                end = time.time()
                navail_money = self.get_available()
                if navail_money - avail_money > 0.5 * avail_money:
                    print('Order has been closed by system.')
                    count += 1
                    error = 1
                    break
                if end - start > close_time:
                    print('Time is up. Closing position.')
                    self.__safely_click(close_list[i])
                    count += 1
                    finished_i.append(i)
                    money = d.find_element_by_css_selector('.account-summary-item.available').text
                    money = money.split('\n')[1]
                    avail_money = money
                else:
                    continue
            if count == trade_time:
                break
        # output the order log
        o_count = 0
        o_i = []
        if error:
            return 0
        while 1:
            for i in range(0, trade_time):
                if i in o_i:
                    continue
                id = close_windows[i].get_attribute('id')
                try:
                    self.__output(d, id, (signal + 1) % 2)
                    o_count += 1
                    o_i.append(i)
                except NoSuchElementException:
                    continue
            if o_count == trade_time:
                break
        return 1

    def get_available(self):
        d = self.browser
        avail_money = d.find_element_by_css_selector('.account-summary-item.available').text.split('\n')[1]
        avail_money = float(avail_money.replace('$', '').replace(',', ''))
        return avail_money

    @staticmethod
    def __safely_click(button):
        while 1:
            status = button.get_attribute('class')
            if 'disabled' in status:
                continue
            else:
                break
        button.click()

    def voling(self, bidwindow, offerwindow, bidbutton, offerbutton, duration=30, vol_init_num=500):
        print('Duration is', duration*60, 'seconds')
        id = bidwindow.get_attribute('id')
        pricer = self.__get_price(id)
        start = time.time()
        flag = 0
        d = self.browser
        # dat = pd.read_csv('WTI.csv')
        # s = dat.loc[:, ['datetime', 'high', 'low']].to_dict()
        # i = 0
        avail = self.get_available()
        while 1:
            end = time.time()
            if end - start > duration * 60:
                print('Time is up')
                if flag != 0:
                    # empty the position
                    print('Begin empty the position')
                    if flag == -1:
                        avail = self.get_available()
                        if avail == '$0.00':
                            print('Order has been closed by system.')
                        else:
                            self.__safely_click(bidbutton)
                            id = bidwindow.get_attribute('id')
                            while 1:
                                try:
                                    self.__output(d, id, 0)
                                    break
                                except NoSuchElementException:
                                    continue
                    elif flag == 1:
                        avail = self.get_available()
                        if avail == '$0.00':
                            print('Order has been closed by system.')
                        else:
                            self.__safely_click(offerbutton)
                            id = offerwindow.get_attribute('id')
                            while 1:
                                try:
                                    self.__output(d, id, 1)
                                    break
                                except NoSuchElementException:
                                    continue
                break
            time.sleep(0.45)
            bid, ask = next(pricer)
            # time.sleep(5)
            # bid, ask = s['high']
            signal, num = self.strategy.return_signal(bid, ask)
            if signal == 0:
                continue
            elif signal < 0:
                print('Get Signal', signal)
                c_avail = self.get_available()
                if abs(c_avail - avail) > 0.4 * avail:
                    print('Order has been closed by system.')
                    avail = c_avail
                    continue
                id = bidwindow.get_attribute('id')
                textpath = '//div[@id="%s"]//div[@contenteditable="true" and @name="quantity"]' % id
                textfield = bidwindow.find_element_by_xpath(textpath)
                textfield.send_keys(num)
                textfield.send_keys(Keys.ENTER)
                self.__safely_click(bidbutton)
                while 1:
                    try:
                        self.__output(d, id, 0)
                        break
                    except NoSuchElementException:
                        continue
                # flag = 0
                # bidbutton.click()
                self.init_window(bidwindow, 1000, 20, 30)
                # Awaiting the button be available
                # while 1:
                #     status = bidbutton.get_attribute('class')
                #     if 'disabled' in status:
                #         continue
                #     else:
                #         break
            elif signal > 0:
                if flag == 0:
                    flag = -1
                elif flag == 1:
                    avail = self.get_available()
                    if avail == '$0.00':
                        print('Order has been closed by system.')
                        flag = 0
                        continue
                id = offerwindow.get_attribute('id')
                textpath = '//div[@id="%s"]//div[@contenteditable="true" and @name="quantity"]' % id
                textfield = offerwindow.find_element_by_xpath(textpath)
                textfield.send_keys(num)
                textfield.send_keys(Keys.ENTER)
                self.__safely_click(offerbutton)
                while 1:
                    try:
                        self.__output(d, id, 1)
                        break
                    except NoSuchElementException:
                        continue
                self.init_window(offerwindow, 1000, 7, 30)

    def init_window(self, window, num, loss, profit, enable_loss=True, enable_profit=False):
        d = self.browser
        id = window.get_attribute('id')
        button = window.find_element_by_xpath(
            '//div[@id="%s"]//button[@cmc-show="model.layout.showSubmitButton" and '
            '@cmc-next-gen-order-ticket-submit-button-tooltip]' % id)
        self.__safely_click(button)
        time.sleep(0.5)
        # Input the text
        textpath = '//div[@id="%s"]//div[@contenteditable="true" and @name="quantity"]' % id
        textfield = window.find_element_by_xpath(textpath)
        textfield.send_keys(num)
        textfield.send_keys(Keys.ENTER)
        # self.setLossProfit(d, id, loss, profit, way='point')

    def trading(self, mode='semiAuto', strategy='EIA', trade_time=1, product_name="黄金", num=100,
                expect_time=datetime.now() + dt.timedelta(hours=-2, minutes=30), loss=5, profit=10, enable_close=False,
                enable_vol=False, vol_init_num=1000, vol_strategy=StrategyEIA):
        d = self.browser
        print('Trading begin, mode is', mode)
        if mode == 'semiAuto':
            # find the current windows and close all of them
            print('Please make sure there are only two window of offer/bid. '
                                                  'Otherwise may cause a great loss')
            print('You have 1 minute to set your information.')
            time.sleep(30)
            slist = d.find_elements_by_xpath('//div[@class="feature feature-next-gen-order-ticket"]')
            if len(slist) > 2:
                print('You have activated other trading window, '
                      'please close those you don\'t want and leave only 2 windows.')
                time.sleep(30)
            print('Trading begin at', datetime.now())
            while 1:
                # find submit order buttons
                bwindow = d.find_elements_by_xpath('//div[@class="feature feature-next-gen-order-ticket"]')
                bidbutton = None
                offerbutton = None
                bid_window = []
                offer_window = []
                for b in bwindow:
                    id = b.get_attribute('id')
                    button = b.find_element_by_xpath(
                        '//div[@id="%s"]//button[@cmc-show="model.layout.showSubmitButton" and '
                        '@cmc-next-gen-order-ticket-submit-button-tooltip]' % id)
                    if button.text == '下达市场卖单':
                        bidbutton = button
                        bid_window.append(b)
                    elif button.text == '下达市场买单':
                        offerbutton = button
                        offer_window.append(b)
                if bidbutton is None or offerbutton is None:
                    print('Button Not Found, Please Make sure you have correctly set the window.')
                    time.sleep(10)
                else:
                    break
            print('All is set at', datetime.now(), '. Awaiting signal.')
            signal, close_time = self.getsignal(strategy)
            print('Signal', str(signal), 'accquired at', datetime.now(), '. Close position time is', close_time)
            order = self.__makeOrder(bidbutton, offerbutton, signal)
            while 1:
                try:
                    ret = next(order)
                    if ret == 1:
                        break
                except StopIteration:
                    break
            if enable_close:
                print('Begin close position.')
                if signal == 1:
                    close_list = [bidbutton]
                    close_windows = bid_window[:]
                else:
                    close_list = [offerbutton]
                    close_windows = offer_window[:]
                print('begin close')
                self.close_position(signal, close_list, close_windows, trade_time, close_time)
                print('Finished close position at', datetime.now())
                btn = close_list[0]
                while 1:
                    status = btn.get_attribute('class')
                    if 'disabled' in status:
                        continue
                    else:
                        break
            if enable_vol:
                self.init_window(offer_window[0], vol_init_num, 7, 30)
                self.init_window(bid_window[0], vol_init_num, 7, 30)
                result = self.read_history_data(expect_time)
                close = []
                high = []
                low = []
                for r in result:
                    high.append(float(r[0]))
                    low.append(float(r[1]))
                    close.append(float(r[2]))
                print('Load history finished at', datetime.now())
                self.strategy = vol_strategy(high, low, close)
                print(self.strategy.closePrice)
                print('Begin voling at', datetime.now())
                self.voling(bid_window[0], offer_window[0], bidbutton, offerbutton, 30)
        elif mode == 'Auto':
            # Auto Trading
            print('Please confirm that you have input the correct product name. '
                  'Otherwise the trader may trade the wrong product.')
            time.sleep(10)
            self.close_all_window()
            d.find_element_by_css_selector('.cookie-banner__button').click()
            try:
                d.find_element_by_xpath('//h2[@title="市场分析"]/../..//button[@title="关闭"]').click()
            except NoSuchElementException:
                pass
            print('Please assure you have input the precise product name.')
            bid_window = []
            offer_window = []
            prev = d.find_elements_by_xpath('//div[@class="feature feature-next-gen-order-ticket"]')
            bid_list = []
            offer_list = []
            # Add designated product trading window and store the buttons
            flag, count = self.__check_type(product_name, num, loss, profit)
            if trade_time == 1 and flag is False and count == 0:
                for i in range(0, trade_time):
                    window, btn = self.__getWindow(product_name, prev, approach='sell', num=num, i=2 * i, loss=loss,
                                                 profit=profit)
                    bid_window.append(window)
                    bid_list.append(btn)
                    prev = d.find_elements_by_xpath('//div[@class="feature feature-next-gen-order-ticket"]')
                    time.sleep(1)
                    window, btn = self.__getWindow(product_name, prev, approach='buy', num=num, i=2 * i + 1,
                                                 loss=loss, profit=profit)
                    offer_window.append(window)
                    offer_list.append(btn)
                    prev = d.find_elements_by_xpath('//div[@class="feature feature-next-gen-order-ticket"]')
            elif trade_time > 1 and flag is True:
                for i in range(0, trade_time):
                    window, btn = self.__getWindow(product_name[i], prev, approach='sell', num=num[i], i=2 * i,
                                                 loss=loss[i], profit=profit[i])
                    bid_window.append(window)
                    bid_list.append(btn)
                    prev = d.find_elements_by_xpath('//div[@class="feature feature-next-gen-order-ticket"]')
                    time.sleep(1)
                    window, btn = self.__getWindow(product_name[i], prev, approach='buy', num=num[i], i=2 * i + 1,
                                                 loss=loss[i], profit=profit[i])
                    offer_window.append(window)
                    offer_list.append(btn)
                    prev = d.find_elements_by_xpath('//div[@class="feature feature-next-gen-order-ticket"]')
            else:
                print('Please correct your input. if you want make more than one order, a list of product name, '
                      'num, loss and profit should be included.')
                return -1
            # Awaiting Signal
            print('All is set at', datetime.now(), '. Awaiting signal.')
            signal, close_time = self.getsignal(strategy)
            print('Signal', str(signal), 'accquired at', datetime.now())
            # Click the Button
            button_list = []
            for i in range(0, len(bid_list)):
                bidbutton = bid_list[i]
                offerbutton = offer_list[i]
                if signal == 1:
                    id = offer_window[i].get_attribute('id')
                else:
                    id = bid_window[i].get_attribute('id')
                button = self.__makeOrder(bidbutton, offerbutton, signal, id)
                next(button)
                button_list.append(button)
            # get the returned information
            for button in button_list:
                while 1:
                    try:
                        ret = next(button)
                        if ret == 1:
                            break
                    except StopIteration:
                        break
            # close position
            if enable_close:
                print('Begin close position.')
                if signal == 1:
                    close_list = bid_list[:]
                    close_windows = bid_window[:]
                else:
                    close_list = offer_list[:]
                    close_windows = offer_window[:]
                self.close_position(signal, close_list, close_windows, trade_time, close_time)
                print('Finished close position at', datetime.now())
        elif mode == 'recording':
            pass

    def EIATrading(self, awaiting_time=datetime.now()):
        year = awaiting_time.year
        month = awaiting_time.month
        day = awaiting_time.day
        wait_time = datetime(year=year, month=month, day=day, hour=22, minute=30)
        now = datetime.now()
        delta = now - wait_time
        delta = now - awaiting_time
        if delta.days >= 0 and delta.seconds > 600:
            print('Awaiting', awaiting_time, ', sleep', delta.seconds - 600, 'seconds')
            time.sleep(delta.seconds - 600)
        elif delta.days < 0:
            print('Error time. Please check the arg awaiting_time.')
            return
        self.open()
        # t.browser.quit()
        self.trading('semiAuto', enable_close=True, enable_vol=False, vol_strategy=StrategyEIA, vol_init_num=1000)
        return

    def PMITrading(self, awaiting_time=datetime.now()):
        year = awaiting_time.year
        month = awaiting_time.month
        day = awaiting_time.day
        wait_time = datetime(year=year, month=month, day=day, hour=22, minute=30)
        now = datetime.now()
        delta = now - wait_time
        delta = now - awaiting_time
        if delta.days >= 0 and delta.seconds > 600:
            print('Awaiting', awaiting_time, ', sleep', delta.seconds - 600, 'seconds')
            time.sleep(delta.seconds - 600)
        elif delta.days < 0:
            print('Error time. Please check the arg awaiting_time.')
            return
        self.open()
        # t.browser.quit()
        self.trading('semiAuto', strategy='PMI_GR', enable_close=True)
        self.trading('semiAuto', strategy='PMI_EU', enable_close=True)
        return

    def collecting_price(self, product_name="西得克萨斯原油", awaiting_time=datetime.now()):
        c_time = datetime.now()
        delta = awaiting_time - c_time
        if delta.days >= 0 and delta.seconds > 60:
            print('Awaiting', awaiting_time, '.Sleep', delta.seconds - 60, 'seconds')
            time.sleep(delta.seconds - 60)
        self.open()
        d = self.browser
        self.close_all_window()
        d.find_element_by_css_selector('.cookie-banner__button').click()
        try:
            d.find_element_by_xpath('//h2[@title="市场分析"]/../..//button[@title="关闭"]').click()
        except NoSuchElementException:
            pass
        window, btn = self.__getWindow(product_name, [], approach='sell', num=1, i=0, loss=1, profit=2)
        id = window.get_attribute('id')
        pricer = self.__get_price(id)
        hist = []
        count = 0
        while 1:
            bid, ask = next(pricer)
            price = (float(bid) + float(ask)) / 2
            count += 1
            hist.append(price)
            if count == 5:
                close = float(price)
                low = float(np.min(hist))
                high = float(np.max(hist))
                v = (str(datetime.now()), high, low, close)
                code = self.controller.dat.store_data(v, table_name='WTI')
                self.controller.returnHandler(code)
                count = 0
                hist = []
            time.sleep(0.95)

    def read_history_data(self, expect_time):
        exp_t = expect_time.strftime('%Y-%m-%d %H:%M:%S.%f')
        sql = 'select high, low, close from investing.WTI where timestamp >= "%s";' % exp_t
        result = self.controller.dat.sql_executer(sql)
        return result


if __name__ == '__main__':
    # username='simaschu@outlook.com'          pwd='Aa201410'
    # t = CMCTrader(username='simaschu@outlook.com', pwd='Aa201410', b_type='Chrome')
    t = CMCTrader(username='sunhua@deepquant.com.cn', pwd='SUNHUAfd2015')
    # t.PMITrading()
    t.EIATrading()
    print('Trading Finished at', datetime.now())
    # t.collecting_price('西得克萨斯原油')
    # t.test()
