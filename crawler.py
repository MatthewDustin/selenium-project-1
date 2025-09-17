from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
def printallbusinfo(tbody):
    tbody = tbody.find_elements(By.TAG_NAME, "td")
    for row in tbody:
        print(row.text)
driver = webdriver.Firefox()
driver.get("https://www.appalcart.com/live-transit")
assert "ETA" in driver.title

driver.find_element(By.CLASS_NAME, "routeSelectAllLabel").click()
driver.find_element(By.ID, "B24").click()
busInfo = driver.find_element(By.CSS_SELECTOR, ".asset-info-eta table tbody")
printallbusinfo(busInfo)
assert "No results found." not in driver.page_source
driver.close()