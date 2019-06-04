import pymysql
from datetime import datetime
import time
from DataHandler import DataHandler
from selenium import webdriver
import sys
import getpass


header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/"
                  "537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36",
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST',
    'Access-Control-Allow-Headers': 'content-type',
}

DATABASE_IP = "101.132.167.75"
DATABASE_ACCOUNT = 'data'
DATABASE_PWD = "SrHGPtjFPuj587F6PXX5"
DATABASE_NAME = 'investing'


ERROR_CODE = -1
SQL_ERROR = -2
CRAWL_ERROR = -3
SUCCESS_CODE = 1
EMPTY_CODE = 0
TIMEOUT_CODE = -4
NOT_UPDATE_CODE = -5
CODE_404 = -404


class Crawler:
    def __init__(self, type='Chrome', db_ip=DATABASE_IP, db_user=DATABASE_ACCOUNT, db_pwd=DATABASE_PWD,
                 db_name=DATABASE_NAME, open_browser=False):
        self.browser_type = type
        self.db_ip = db_ip
        self.db_user = db_user
        self.db_pwd = db_pwd
        self.db_name = db_name
        self.db = None
        self.connected = False
        self.browsers = []
        user = getpass.getuser()
        if type == 'Chrome':
            if sys.platform == 'darwin' and user == 'sunhua':
                self.exe_path = '/Users/sunhua/desktop/chromedriver'
            elif sys.platform == 'win32':
                self.exe_path = 'win32/chromedriver.exe'
            elif sys.platform == 'darwin':
                self.exe_path = 'mac/chromedriver'
        elif type == 'Firefox':
            if sys.platform == 'darwin' and user == 'sunhua':
                self.exe_path = '/Users/sunhua/desktop/geckodriver'
            elif sys.platform == 'win32':
                self.exe_path = 'win32/geckodriver.exe'
            elif sys.platform == 'darwin':
                self.exe_path = 'mac/geckodriver'
        self.dat = DataHandler()
        if open_browser:
            self.open_browser()

    def open_browser(self):
        print('Note: Selenium is using driver attached to this project, not your own driver.')
        browser = None
        if self.browser_type == 'Chrome':
            chrome_opt = webdriver.ChromeOptions()
            prefs = {'profile.managed_default_content_settings.images': 2}
            chrome_opt.add_experimental_option('prefs', prefs)
            browser = webdriver.Chrome(
                executable_path=self.exe_path,
                chrome_options=chrome_opt
            )
        elif self.browser_type == 'Firefox':
            browser = webdriver.Firefox(executable_path=self.exe_path)
        if browser is not None:
            self.browsers.append(browser)
            self.opened = True
        else:
            print('Wrong browser_type!')
        return browser

    def store_data(self, ID, act, prev, forecast, time_stamp, name):
        now = datetime.now().strftime('%H:%M:%S.%f')
        try:
            self.connect_db()
            #name = 'abc'
            time_stamp = datetime.strptime(time_stamp, '%Y/%m/%d %H:%M:%S')
            time_stamp = time_stamp.strftime('%H:%M:%S.%f')
            cursor = self.db.cursor()
            value = (int(ID), time_stamp, now, act, prev, forecast, name)
            sql = "replace into daily values(%s,%s,%s,%s,%s,%s,%s);"
            #print(sql)
            cursor.execute(sql, value)
            self.db.commit()
            cursor.close()
            self.db.close()
            return SUCCESS_CODE
        except pymysql.err.MySQLError as e:
            print(e)
            return SQL_ERROR

    def connect_db(self):
        self.db = pymysql.connect(
            host=self.db_ip,
            user=self.db_user,
            passwd=self.db_pwd,
            db=self.db_name,
            charset='utf8'
        )
        #self.db.charset = 'utf8'
        #self.db.encoding = 'utf8'
        self.connected = True

    def returnHandler(self, code):
        code_dic = {
            ERROR_CODE: 'Not Specified error!',
            SQL_ERROR: 'Database Error!',
            CRAWL_ERROR: 'Crawler Error!',
            EMPTY_CODE: 'Not implement api!',
            SUCCESS_CODE: 'Finished at ' + str(datetime.now()),
            NOT_UPDATE_CODE: 'No new update today!',
            TIMEOUT_CODE: 'Time out!',
            CODE_404: '404 not found!',
        }
        print(code_dic[code])


if __name__ == '__main__':
    c = Crawler()
    # time.sleep(10)
    ID_list = ['11', '12', '13']
    c.store_data('11', '2M', '3M', '1M', '2019/05/15 13:30:00', 'EIATest11')
    c.store_data('12', '2M', '1M', '1M', '2019/05/15 13:30:00', 'EIATest11')
    code = c.store_data('13', '2M', '1M', '1M', '2019/05/15 13:30:00', 'EIATest11')
    c.returnHandler(code)
