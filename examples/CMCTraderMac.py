# usr/bin/env python3
# -*- coding:utf-8 -*-


import json
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
import time
import logging


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

# cfg_file = open('CMCConfig.cfg')
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
    def __init__(self):
        self.login_status = False
        self.original_url = 'https://platform.cmcmarkets.com/#/login?b=CMC-CFD&r=AU'
        self.driver = webdriver.Chrome('/Applications/chromedriver')

    def close_subwindows(self):
        driver = self.driver
        close_list = driver.find_elements_by_xpath("//div[@class='main fade']//"
                                                  "button[@class='header-item__button close-button' and @title='关闭']")
        for c in close_list:
            try:
                c.click()
            except Exception as e:
                pass

    def login(self, username: str, password: str):
        driver = self.driver
        driver.get(self.original_url)
        driver.fullscreen_window()
        waiter = WebDriverWait(driver, 60)

        waiter.until(lambda driver: driver.find_element_by_id('username'))
        ele_username = driver.find_element_by_id('username')
        ele_password = driver.find_element_by_id('password')
        ele_username.send_keys(username)
        ele_password.send_keys(password + '\n')
        time.sleep(15)

        xpath_remind_later = "//button[@class='button accept rich-in-platform-message-container__button link-new-secondary']"
        waiter.until(lambda driver: driver.find_element_by_xpath(xpath_remind_later))
        ele_remind_later = driver.find_element_by_xpath(xpath_remind_later)
        ele_remind_later.click()

        try:
            ele_close = driver.find_element_by_xpath("//button[ @class ='link-new-secondary "
                                                     "cookie-banner__button']")
            ele_close.click()
        except Exception as e:
            pass

        self.close_subwindows()


if __name__ == '__main__':
    trader = CMCTrader()
    trader.login(username='panrui0226@163.com', password='1a8guJ58')
