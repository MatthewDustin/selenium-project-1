from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC

def printallbusinfo(tbody):
    tbody = tbody.find_elements(By.TAG_NAME, "td")
    for row in tbody:
        print(row.text)

driver = webdriver.Firefox()
driver.maximize_window()
driver.get("https://www.holtonmountainrentals.com/view-all-properties")
wait = WebDriverWait(driver, 10)

import time

links = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "td a::attr(href)")))
for url in links:
    yield scrapy.Request(url, callback=RentalSpider.holtonItem)
    return
#elem = wait.until(EC.element_to_be_clickable((By.XPATH, "(//li[@class='wixui-anchor-menu__item'])[2]/a")))
#wait.until(EC.element_to_be_selected(driver.find_elements(By.CSS_SELECTOR, "circle")[1]))
#driver.find_elements(By.CSS_SELECTOR, "circle")[1].click()

#scroll down a little more
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

frame = wait.until(EC.element_to_be_clickable((By.TAG_NAME, "iframe")))

driver.execute_script("arguments[0].scrollIntoView(false);", frame)
driver.switch_to.frame(frame)

wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "toggleText"))).click()


elem = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='B24']/div[@class='vehicle icon-asset']")))
driver.execute_script("arguments[0].scrollIntoView(true);", elem)
elem.click()

busInfo = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".asset-info-eta table tbody")))
printallbusinfo(busInfo)
assert "No results found." not in driver.page_source
driver.close()