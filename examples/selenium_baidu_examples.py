from selenium import webdriver
import time


driver = webdriver.Chrome('/Applications/chromedriver')

# get方法，打开指定网址
url = 'http://www.baidu.com'
driver.get(url)

# 界面元素的定位
# 查找到搜索输入栏网页元素，返回一个表示该元素的WebElement对象
element_input = driver.find_element_by_id(id_='kw')

# 输入字符
element_input.send_keys('python')

# 查找搜索按钮网页元素
element_submit = driver.find_element_by_id(id_='su')
# 点击该元素
element_submit.click()
time.sleep(10)

# 最后，driver.quit让浏览器和驱动程序一起退出，不然会有好几个实例一起运行
driver.quit()
