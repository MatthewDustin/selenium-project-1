import re
from selenium import webdriver
from selenium.common import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
import time
import json
#wipe rental_leases.jsonl

already_visited = []
with open("rental_leases.jsonl", "r") as f:
    elems = f.readlines()
    for elem in elems:
        elem = json.loads(elem)
        url = str(elem["url"])
        url = url.replace("properties", "property")
        name = url.split("property/")[1].split("/")[0].strip()
        already_visited.append(name)

driver = webdriver.Firefox()
driver.implicitly_wait(3)
wait = WebDriverWait(driver, 3)

loopDelay = 3  # seconds


def find_elements_default(by, value, default, lambda_func=None):
    try:
        elements = driver.find_elements(by=by, value=value)
        return lambda_func(elements) if lambda_func else elements
    except NoSuchElementException:
        return default
    except StaleElementReferenceException: #clever solution
        elements = driver.find_elements(by=by, value=value)
        return lambda_func(elements) if lambda_func else elements


def find_element_default(by, value, default, lambda_func=None):
    try:
        element = driver.find_element(by=by, value=value)
        return lambda_func(element) if lambda_func else element
    except NoSuchElementException:
        return default


driver.maximize_window()
driver.get("https://www.holtonmountainrentals.com/view-all-properties")

links = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "td > a")))
links = [link.get_attribute("href") for link in links]
temp = []
for link in links:
    name = link.split("properties/")[1].split("/")[0].strip()
    if name not in already_visited:
        temp.append(link)

links = set(temp)

for url in links:
    print(url)
    driver.get(url)

    features = find_elements_default(By.CSS_SELECTOR, ".property-features-list ul li", [],
                                     lambda_func=lambda elems: [elem.text.lower() for elem in elems])
    features = " ".join(features)

    # this is so 'washer' doesn't match to 'dishwasher'
    features.replace("dishwasher", "")

    description = find_element_default(By.CSS_SELECTOR, ".property-description", "",
                                       lambda_func=lambda elem: elem.text.lower())

    bedrooms = find_element_default(By.CLASS_NAME, "bed-item", 1, lambda_func=lambda elem: int(elem.text.split()[1]))
    bathrooms = find_element_default(By.CLASS_NAME, "bath-item", 1, lambda_func=lambda elem: int(elem.text.split()[1]))

    full_description = description + " " + features
    patio = "patio" in features
    busStop = "appalcart" in full_description or "bus stop" in full_description
    airConditioning = "air conditioning" in full_description or "a/c" in full_description
    washer = "None"
    if "washer" in features:
        washer = "In-home"
    elif "on-site laundry" in description or "on site laundry" in description or "on-site coin operated laundry" in description:
        washer = "On-site"

    pricePerBedroom = driver.find_element(By.CSS_SELECTOR, ".pe_price").text.split()[0][1:]
    totalPrice = int(bedrooms) * int(pricePerBedroom)

    rentalRates = driver.find_elements(By.CSS_SELECTOR, ".rates-table td:has(.tenant-number)")
    totalPriceMaxCapacity = totalPrice
    counter = 1
    for temp in rentalRates:
        if "$" in temp.text:
            tempNum = int(re.sub(r'[^0-9]', '', temp.text))
            if tempNum < 100:
                continue
            tempRent = tempNum * counter
            if tempRent < totalPriceMaxCapacity:
                totalPriceMaxCapacity = tempRent
            counter += 1
    address = driver.find_element(By.ID, "bbd_map-single-canvas").get_attribute("data-address")
    name = driver.find_element(By.CSS_SELECTOR, ".entry-title").text.split("$")[0].strip()
    with open("rental_leases.jsonl", "a") as f:
        # print(f'"name": "{name}", "address": "{address}", "bedrooms": {bedrooms}, "bathrooms": {bathrooms}, "busStop": {busStop}, "patio": {patio}, "airConditioning": {airConditioning}, "washer": "{washer}", "pricePerBedroom": {pricePerBedroom}, "totalPrice": {totalPrice}, "totalPriceMaxCapacity": {totalPriceMaxCapacity}')
        data = {
            "url": url,
            "name": name,
            "address": address,
            "bedrooms": bedrooms,
            "bathrooms": bathrooms,
            "busStop": busStop,
            "patio": patio,
            "airConditioning": airConditioning,
            "washer": washer,
            "pricePerBedroom": pricePerBedroom,
            "totalPrice": totalPrice,
            "discountedPrice": totalPriceMaxCapacity
        }
        f.write(json.dumps(data) + "\n")

    time.sleep(loopDelay)

assert "No results found." not in driver.page_source

driver.get("https://offcampushousing.appstate.edu/housing")
links = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".property-title a")))
links = [link.get_attribute("href") for link in links]
temp = []
for link in links:
    name = link.split("property/")[1].split("/")[0].strip()
    if name not in already_visited:
        temp.append(link)

links = set(temp)
for url in links:
    print(url)
    driver.get(url)

    driver.execute_script("arguments[0].scrollIntoView(true);", find_element_default(By.CSS_SELECTOR, ".floor-plan-container", None))
    try:
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".fake_link"))).click()
    except:
        pass
    features = find_elements_default(By.CSS_SELECTOR, ".amenities-container li", [],
                                     lambda_func=lambda elems: [elem.text.lower() for elem in elems])
    features = " ".join(features)
    description = find_element_default(By.CSS_SELECTOR, "#apartmentDescriptionSection p.word-wrap", "",
                                       lambda_func=lambda elem: elem.text.lower())

    bedrooms = find_elements_default(By.CLASS_NAME, "beds-bath-link", [1],
                                     lambda_func=lambda elems: [elem.text.lower() for elem in elems])
    print(bedrooms)
    for i in range(len(bedrooms)):
        if "studio" in bedrooms[i]:
            bedrooms[i] = 1
        elif type(bedrooms[i]) is str:
            bedrooms[i] = int(re.sub(r'[^0-9]', '', bedrooms[i]))
    bathrooms = find_elements_default(By.XPATH, "//td[@data-qaid='baths']", [1],
                                      lambda_func=lambda elems: [float(elem.text.split()[0]) for elem in elems])
    try:
        prices = find_elements_default(By.XPATH, "//td[@data-qaid='price']", [0],
                                       lambda_func=lambda elems: [int(re.sub(r'[^0-9]', '', elem.text.split('$')[1].split()[0])) for elem
                                                                  in elems])
    except Exception:
        continue
    full_description = description + " " + features
    patio = "patio" in features
    busStop = "appalcart" in full_description or "bus stop" in full_description
    airConditioning = "air conditioning" in full_description or "a/c" in full_description
    washer = "None"
    if "washer" in features:
        washer = "In-home"
    elif "on-site laundry" in description or "on site laundry" in description or "on-site coin operated laundry" in description:
        washer = "On-site"

    address = find_element_default(By.CSS_SELECTOR, "p.address", "None", lambda_func=lambda elem: elem.text.strip())
    name = driver.find_element(By.CSS_SELECTOR, "h1.property-name").text.strip()
    units = zip(bedrooms, bathrooms, prices)
    for bedroom, bathroom, price in units:
        #print(f'{{"name": "{name}", "address": "{address}", "bedrooms": {bedroom}, "bathrooms": {bathroom}, "price": {price}}}')
        with open("rental_leases.jsonl", "a") as f:
            data = {
                "url": url,
                "name": name,
                "address": address,
                "bedrooms": bedroom,
                "bathrooms": bathroom,
                "busStop": busStop,
                "patio": patio,
                "airConditioning": airConditioning,
                "washer": washer,
                "pricePerBedroom": price,
                "totalPrice": price * bedroom,
                "discountedPrice": price * bedroom
            }
            f.write(json.dumps(data) + "\n")

    time.sleep(loopDelay)

driver.close()

with open("rental_leases.jsonl", "r") as f:
    lines = f.readlines()
    unique_lines = {json.loads(line) for line in lines}
    unique_lines = sorted(unique_lines, key=(
        lambda x: ("In-home" in x["washer"], "On-site" in x["washer"], x["airConditioning"], x["patio"], x["busStop"],
                   -1 * int(x["pricePerBedroom"]))), reverse=True)

    for line in unique_lines:
        print(
            f'${line["pricePerBedroom"]} {line["name"]} - {line["bedrooms"]} bed, {line["bathrooms"]} bath - Amenities: Washer: {line["washer"]}, Air Conditioning: {line["airConditioning"]}, Patio: {line["patio"]}, Bus Stop: {line["busStop"]}')
