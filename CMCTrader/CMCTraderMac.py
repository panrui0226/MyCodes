# usr/bin/env python3
# -*- coding:utf-8 -*-


import json
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
import time
import logging
from Strategies.StrategyDoubleMA import StrategyDoubleMA
from Strategies.StrategyWaveCrest import StrategyWaveCrest


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# url = 'https://platform.cmcmarkets.com/#/login?b=CMC-CFD&r=AU'
# username = 'panrui0226@163.com'
# password = '1a8guJ58'
#
# driver = webdriver.Chrome('/Applications/chromedriver')
#
# driver.get(url)
# driver.fullscreen_window()
#
# waiter = WebDriverWait(driver, 60)
#
# try:
#     waiter.until(lambda driver: driver.find_element_by_id('username'))
#     element_username = driver.find_element_by_id('username')
#     element_username.send_keys(username)
#     element_password = driver.find_element_by_id(id_='password')
#     element_password.send_keys(password+'\n')
# except TimeoutError:
#     pass
#
# try:
#     waiter.until(lambda driver: driver.find_element_by_class_name('column account'))
# except:
#     pass

# cfg_file = open('Trader.cfg')
# setting = json.load(cfg_file)


# def open_browser(browser: str="Chrome"):
#     if browser == "Chrome":
#         webdriver_handle = webdriver.Chrome("/Applications/chromedriver")
#         return webdriver_handle
#     else:
#         print('WebDriver not exist')
#
#
# def open_url(d, url):
#     d.get(url)
#     d.fullscreen_window()


# if __name__ == '__main__':
#     d = webdriver.Chrome('/Applications/chromedriver')
#     url = "https://platform.cmcmarkets.com/#/login?b=CMC-CFD&r=AU"
#     d.get(url)
#     d.fullscreen_window()
#     waiter = WebDriverWait(d, 20)
#
#     waiter.until(lambda d: d.find_element_by_id('username'))
#     ele_username = d.find_element_by_id('username')
#     ele_password = d.find_element_by_id('password')
#     ele_username.clear()
#     ele_password.clear()
#     ele_username.send_keys('panrui0226@163.com')
#     ele_password.send_keys('1a8guJ58\n')
#     time.sleep(15)
#
#
#     try:
#         ele_remind_later = d.find_element_by_xpath("//button[@class='button accept rich-in-platform-message-container__"
#                                                    "button link-new-secondary']")
#         ele_remind_later.click()
#     except NoSuchElementException:
#         print('element not found')


# while True:
#     if d.current_url == "https://platform.cmcmarkets.com/#/app?b=CMC-CFD&r=AU":
#         try:
#             waiter.until(lambda x: x.find_element_by_link_text("稍后提醒"))
#             ele_remind_later = d.find_element_by_link_text("稍后提醒").click()
#             break
#         except TimeoutError:
#             print(TimeoutError)

class CMCTrader(object):
    def __init__(self, cfg):
        self.cfg = cfg
        self.login_status = False
        self.original_url = 'https://platform.cmcmarkets.com/#/login?b=CMC-CFD&r=AU'
        self.driver = webdriver.Chrome('/Applications/chromedriver')
        self.waiter = WebDriverWait(self.driver, 60)
        self.strategy = None

    # ------------------------------------------------------------------------------------------------------------------
    #
    def close_sub_windows(self):
        driver = self.driver
        close_list = driver.find_elements_by_xpath("//div[@class='header-item action-buttons']//"
                                                  "button[@class='header-item__button close-button' and @title='关闭']")
        for c in close_list:
            try:
                c.click()
            except Exception as e:
                logger.info('A sub window that failed to close automatically has been detected. '
                            'Please close it manually')

    # ------------------------------------------------------------------------------------------------------------------
    #
    def open_trade_window(self, instrument):
        driver = self.driver
        waiter = self.waiter

        xpath_search = "//nav[@class='header-row header-row-3 navigation-bar']//li[@title = '打开快速搜索进入产品']"
        waiter.until(lambda driver: driver.find_element_by_xpath(xpath_search))
        ele_search = driver.find_element_by_xpath(xpath_search)
        ele_search.click()

        xpath_input = "//input[@class = 'search-input-text']"
        waiter.until(lambda driver: driver.find_element_by_xpath(xpath_input))
        ele_input = driver.find_element_by_xpath(xpath_input)
        ele_input.clear()
        ele_input.send_keys(instrument)

        xpath_result = "//ul[@class = 'results']//li[@class = 'search-result-item--odd currently-selected-by-keypress']"
        waiter.until(lambda driver: driver.find_element_by_xpath(xpath_result))
        ele_result = driver.find_element_by_xpath(xpath_result)
        ele_result.click()

    # ------------------------------------------------------------------------------------------------------------------
    #
    def login(self):
        driver = self.driver
        waiter = self.waiter

        waiter.until(lambda driver: driver.find_element_by_id('username'))
        ele_username = driver.find_element_by_id('username')
        ele_password = driver.find_element_by_id('password')
        ele_username.send_keys(self.cfg['username'])
        ele_password.send_keys(self.cfg['password'] + '\n')
        # time.sleep(15)

        xpath_remind_later = "//button[@class='button accept rich-in-platform-message-container__button " \
                             "link-new-secondary']"
        waiter.until(lambda driver: driver.find_element_by_xpath(xpath_remind_later))
        ele_remind_later = driver.find_element_by_xpath(xpath_remind_later)
        ele_remind_later.click()

        try:
            ele_close = driver.find_element_by_xpath("//button[@class ='link-new-secondary "
                                                     "cookie-banner__button']")
            ele_close.click()
        except Exception as e:
            pass

        logger.info('User %s Logged in Successfully!' % self.cfg['username'])

    # ------------------------------------------------------------------------------------------------------------------
    #
    def open(self):
        driver = self.driver
        driver.get(self.original_url)
        driver.fullscreen_window()
        self.login()
        self.close_sub_windows()
        count = 0
        while count < 2:
            self.open_trade_window(self.cfg['instrument'])
            count += 1

    # ------------------------------------------------------------------------------------------------------------------
    #
    def get_ask_bid(self):
        driver = self.driver
        waiter = self.waiter

        xpath_ask = "//div[@class = 'price-box buy']//span[@class = 'price']//span[@class = 'main']"
        xpath_ask_decimals = "//div[@class = 'price-box buy']//span[@class = 'price']//sub"
        xpath_bid = "//div[@class = 'price-box sell']//span[@class = 'price']//span[@class = 'main']"
        xpath_bid_decimals = "//div[@class = 'price-box sell']//span[@class = 'price']//sub"

        waiter.until(lambda driver: driver.find_element_by_xpath(xpath_ask) and driver.find_element_by_xpath(xpath_bid))
        ele_ask = driver.find_element_by_xpath(xpath_ask)
        ele_ask_decimals = driver.find_element_by_xpath(xpath_ask_decimals)
        ele_bid = driver.find_element_by_xpath(xpath_bid)
        ele_bid_decimals = driver.find_element_by_xpath(xpath_bid_decimals)

        ask_str = str(ele_ask.text) + str(ele_ask_decimals.text)
        bid_str = str(ele_bid.text) + str(ele_bid_decimals.text)

        try:
            ask_str = ask_str.replace(',', '')
            bid_str = bid_str.replace(',', '')
        except:
            pass

        ask = float(ask_str)
        bid = float(bid_str)

        return ask, bid

    # ------------------------------------------------------------------------------------------------------------------
    #
    def fill_quantity(self):
        driver = self.driver
        xpath_quantity = "//div[@class='form-ctrl quantity']//div[@name='quantity']"
        ele_quantity = driver.find_elements_by_xpath(xpath_quantity)

        for quantity in ele_quantity:
            quantity.clear()
            quantity.send_keys(self.cfg['amount'] + '\n')

    # ------------------------------------------------------------------------------------------------------------------
    #
    def trade_template_01(self, strategy):
        driver = self.driver
        self.strategy = strategy
        logger.info('Trading Strategy %s Has Been Loaded Successfully!' % str(strategy))
        counter_1 = 0
        counter_2 = 1

        ele_buy_button = None
        ele_sell_button = None

        while True:
            ask_price = self.get_ask_bid()[0]
            bid_price = self.get_ask_bid()[1]
            signal = self.strategy.return_signal(ask_price, bid_price)[0]

            # 只检查一次下单按钮，一旦通过，不再检查
            while counter_1 == 0:
                try:
                    ele_buy_button = driver.find_element_by_xpath("//div[@class='next-gen-order-ticket-buttons']//"
                                                                      "button[contains(text(),'下达市场买单')]")
                    ele_sell_button = driver.find_element_by_xpath("//div[@class='next-gen-order-ticket-buttons']//"
                                                                      "button[contains(text(),'下达市场卖单')]")
                    logger.info('Buy and Sell Button Found!')
                    logger.info('Trading Strategy Has Been Activated at %s!' % time.asctime())
                    start_time = time.time()
                    counter_1 += 1
                    self.fill_quantity()
                    break

                except Exception as e:
                    logger.warning('Buy and Sell Button NOT Found!')
                    time.sleep(5)
                    pass

            if signal == 1:
                print('Get Signal 1')
                try:
                    ele_buy_button.click()
                    print('Buy at %s' % ask_price)

                    waiter = self.waiter
                    xpath_new_order = "//div[@class='next-gen-order-ticket-buttons']//button[contains(text(),'新定单')]"
                    waiter.until(lambda driver: driver.find_element_by_xpath(xpath_new_order))
                    ele_new_order = driver.find_element_by_xpath(xpath_new_order)
                    ele_new_order.click()

                    self.fill_quantity()

                except Exception as e:
                    print('Unexpected error: %s. Stop The Program Right Now!' % e)

            elif signal == -1:
                print('Get Signal -1')
                try:
                    ele_sell_button.click()
                    print('Sell at %s' % bid_price)

                    waiter = self.waiter
                    xpath_new_order = "//div[@class='next-gen-order-ticket-buttons']//button[contains(text(),'新定单')]"
                    waiter.until(lambda driver: driver.find_element_by_xpath(xpath_new_order))
                    ele_new_order = driver.find_element_by_xpath(xpath_new_order)
                    ele_new_order.click()

                    self.fill_quantity()

                except Exception as e:
                    print('Unexpected error: %s. Stop The Program Right Now!' % e)

            if counter_2 % 60 == 0:
                end_time = time.time()
                cost = end_time - start_time
                logger.info('Strategy Has Been Running for %s Seconds' % round(cost))

            counter_2 += 1
            time.sleep(0.9)

    # ------------------------------------------------------------------------------------------------------------------
    #
    def trade_template_02(self, strategy):
        driver = self.driver
        waiter = self.waiter
        logger.info('Trading Strategy %s Has Been Loaded Successfully!' % str(strategy))
        counter_1 = 0

        ele_buy_button = None
        ele_sell_button = None

        xpath_buy_button = "//div[@class='next-gen-order-ticket-buttons']//button[contains(text(),'下达市场买单')]"
        xpath_sell_button = "//div[@class='next-gen-order-ticket-buttons']//button[contains(text(),'下达市场卖单')]"
        xpath_amount = "//div[@class='form-ctrl quantity']//div[@class='price-input active-input']"
        xpath_new_order = "//div[@class='next-gen-order-ticket-buttons']//button[contains(text(),'新定单')]"

        while True:
            # 首次检查窗口
            while counter_1 == 0:
                try:
                    ele_buy_button = driver.find_element_by_xpath(xpath_buy_button)
                    ele_sell_button = driver.find_element_by_xpath(xpath_sell_button)
                    logger.info('Buy and Sell Button Found!')
                    logger.info('Trading Strategy Has Been Activated at %s!' % time.asctime())
                    start_time = time.time()
                    counter_1 += 1
                    self.fill_quantity()
                    break

                except Exception as e:
                    logger.warning('Buy and Sell Button NOT Found!')
                    time.sleep(5)
                    pass

            ask = self.get_ask_bid()[0]
            bid = self.get_ask_bid()[1]
            signal = strategy.return_signal(ask=ask, bid=bid)

            if signal[0] == 1:
                logger.info("Get Signal 1")
                try:
                    ele_amount = driver.find_elements_by_xpath(xpath_amount)
                    ele_amount[0].clear()
                    ele_amount[0].send_keys(str(signal[1]) + '\n')
                    ele_amount[1].clear()
                    ele_amount[1].send_keys(str(signal[1]) + '\n')

                    ele_buy_button.click()
                    waiter.until(lambda driver: driver.find_element_by_xpath(xpath_new_order))
                    ele_new_order = driver.find_element_by_xpath(xpath_new_order)
                    ele_new_order.click()
                except Exception as e:
                    logger.warning('Unexpected error: %s. Stop The Program Right Now!' % e)

            elif signal[0] == -1:
                logger.info("Get Signal -1")
                try:
                    ele_amount = driver.find_elements_by_xpath(xpath_amount)
                    ele_amount[0].clear()
                    ele_amount[0].send_keys(str(signal[1]) + '\n')
                    ele_amount[1].clear()
                    ele_amount[1].send_keys(str(signal[1]) + '\n')

                    ele_sell_button.click()
                    waiter.until(lambda driver: driver.find_element_by_xpath(xpath_new_order))
                    ele_new_order = driver.find_element_by_xpath(xpath_new_order)
                    ele_new_order.click()
                except Exception as e:
                    logger.warning('Unexpected error: %s. Stop The Program Right Now!' % e)

            # 交易中检查窗口
            try:
                ele_buy_button = driver.find_element_by_xpath(xpath_buy_button)
                ele_sell_button = driver.find_element_by_xpath(xpath_sell_button)
            except Exception as e:
                logger.warning("Button Not Found! The Program Is Still Running! Check The Windows Immediately!")
                pass

            time.sleep(0.9)

    # ------------------------------------------------------------------------------------------------------------------
    #
    def start_trading(self, strategy):
        self.open()
        self.trade_template_02(strategy=strategy)

    # ------------------------------------------------------------------------------------------------------------------

