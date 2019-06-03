from selenium import webdriver
import time


url = 'https://platform.cmcmarkets.com/#/login?b=CMC-CFD&r=AU'
driver = webdriver.Chrome('/Applications/chromedriver')

driver.get(url)

time.sleep(15)

element_username = driver.find_element_by_id(id_='username')
element_username.send_keys('panrui0226@163.com')

element_password = driver.find_element_by_id(id_='password')
element_password.send_keys('1a8guJ58')

element_submit = driver.find_element_by_class_name('link-new-primary')
element_submit.click()

time.sleep(15)

element_secondary = driver.find_element_by_class_name('button accept rich-in-platform-message-container__button link-new-secondary')
element_secondary.click()
