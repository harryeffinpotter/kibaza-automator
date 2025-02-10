from selenium.webdriver.common.by import By

def find_visible_one(driver, name_to_search):
    # find elements by name and return the first one of them that is visble
    all_elements = driver.find_elements(By.NAME, name_to_search)
    element = None
    for element in all_elements:
        if element.is_displayed():
            return element, True
    return element, False