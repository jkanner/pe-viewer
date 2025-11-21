from selenium import webdriver
import time

url = 'http://localhost:8500?buildcache=true'

options = webdriver.ChromeOptions()
options.add_argument('--headless')
browser = webdriver.Chrome(options=options)
page = browser.get(url)
time.sleep(60*30)  #-- Let it run for 30 minutes
browser.quit()
