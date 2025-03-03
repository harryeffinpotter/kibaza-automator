#!/usr/bin/env python3
import csv
import time
import undetected_chromedriver as uc
from selenium.webdriver.support.select import Select
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys  
from datetime import datetime
import argparse
import sys
from dotenv import load_dotenv
import re

from selenium import webdriver
from selenium.webdriver.chrome.service import Service

load_dotenv()
EMAIL = os.getenv("EMAIL")
SELLER_NUMBER = os.getenv("SELLER_NUMBER")
EVENT_NAME = os.getenv("EVENT_NAME")

# Update these selectors if the actual page uses different attributes
LOGIN_BUTTON_SELECTOR = (By.ID, "login-button")  # Selector for login button on the login page
EMAIL_INPUT_SELECTOR = (By.NAME, "email")  # Selector for the email input field
SELLER_NUMBER_SELECTOR = (By.NAME, "userId")  # Selector for seller ID field.
SUBMIT_BUTTON_SELECTOR = (By.ID, "sendlogin")  # Selector for the login submit button

# Posting page selectors—adjust these to match the actual posting form fields.
TITLE_INPUT_SELECTOR = (By.NAME, "title")
DESCRIPTION_INPUT_SELECTOR = (By.NAME, "description")
PRICE_INPUT_SELECTOR = (By.NAME, "price")
IMAGE_INPUT_SELECTOR = (By.NAME, "image_upload")  # Should be a file input element (allows multiple if needed)
POST_SUBMIT_SELECTOR = (By.ID, "post-submit")     # Selector for the post submit button
# Add new selectors at the top

CATEGORY_SELECTOR = (By.NAME, "category")
SUBCATEGORY_SELECTOR = (By.CSS_SELECTOR, "[name='subcategory[]']")
NAME_SELECTOR = (By.NAME, "name")
DESCRIPTION_SELECTOR = (By.NAME, "description")
PRICE_SELECTOR = (By.NAME, "price")
SIZE_SELECTOR = (By.CSS_SELECTOR, "[name='size[]']")
GENDER_SELECTOR = (By.NAME, "gender")
BRAND_SELECTOR = (By.CSS_SELECTOR, "[name='brand[]']")
IMAGE_INPUT_SELECTOR = (By.CSS_SELECTOR, "input[name='productImages[]']")
SUBMIT_ITEM_BUTTON_SELECTOR = (By.CSS_SELECTOR, "input.js-submit[name='js-submit']")


def login(driver, email, seller_number):
    # Navigate to the login page.
    driver.get(f"https://www.kibaza.de/{EVENT_NAME}")
    driver.get("https://www.kibaza.de/login.php")
    # Wait until the email input is present and fill in the credentials.
    email_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(EMAIL_INPUT_SELECTOR)
    )
    seller_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(SELLER_NUMBER_SELECTOR)
    )
    email_input.send_keys(email)
    seller_input.send_keys(seller_number)
    
    # Click the submit button.
    submit_btn = driver.find_element(*SUBMIT_BUTTON_SELECTOR)
    submit_btn.click()

def close_modal(driver):
    try:
        # Dismiss modal using Bootstrap's native methods
        driver.execute_script("""
            // Get all Bootstrap modals
            const modals = Array.from(document.querySelectorAll('.modal'));
            
            // Hide each modal using Bootstrap's jQuery API
            modals.forEach(modal => {
                $(modal).modal('hide');
            });
            
            // Remove backdrop if present
            const backdrop = document.querySelector('.modal-backdrop');
            if (backdrop) backdrop.remove();
            
            // Reset body class
            document.body.classList.remove('modal-open');
        """)
        
        # Verify dismissal
        WebDriverWait(driver, 3).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, ".modal.fade.show"))
        )
        
    except Exception as e:
        print(f"Modal dismissal error: {str(e)}")


def validate_categories(csv_path):
    """Validate CSV categories against Kibaza's requirements"""
    valid = True
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Category validation
            if row['category'] not in CATEGORY_MAP:
                print(f"Invalid category: {row['category']} - Valid options: {list(CATEGORY_MAP.keys())}")
                valid = False
            # Subcategory validation
            elif row['category'] in SUBCATEGORY_MAP and row['subcategory']:
                if row['subcategory'] not in SUBCATEGORY_MAP[row['category']]:
                    print(f"Invalid subcategory: {row['subcategory']} for category {row['category']} - Valid options: {list(SUBCATEGORY_MAP[row['category']].keys())}")
                    valid = False
    return valid

def check_if_item_should_be_spared(delete_button, items_to_spare):
    # Find the closest parent td element
    row = delete_button.find_element(By.XPATH, "./ancestor::tr")
    product_id_cell = row.find_element(By.XPATH, "./preceding-sibling::tr[1]/td[2]")
    # Check if the td contains a product ID that's in our set
    text_to_search = product_id_cell.text
    match = re.search(r'ProduktId: #(\d+)', text_to_search)
    if match:
        product_id = match.group(1)
        if product_id in items_to_spare:
            return True, product_id # i made it this way so that it defaults to True and really only returns False if everything went well here
        else:
            return False, product_id
    return True, 0

def delete_all_items(driver, items_to_spare):
    driver.get("https://www.kibaza.de/product_list.php?status=1")
    time.sleep(1.5)
    close_modal(driver)
    time.sleep(1.5)

    try:
        while True: # repeat until break signal 
            time.sleep(1.5)
            delete_buttons = driver.find_elements(By.CSS_SELECTOR, "button.btn.btn-danger.btn-sm")
            deleted_something = False
            for delete_button in delete_buttons:
                spare_this, product_id = check_if_item_should_be_spared(delete_button, items_to_spare)
                if not spare_this:
                    delete_button.click() 
                    time.sleep(1.5)
                    # Wait for the modal to appear
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "modal-content")))                  
                    # Find the confirmation button within the same modal
                    modal = driver.find_element(By.XPATH, "//div[contains(@class, 'modal') and contains(@style, 'display: block')]")
                    confirm_button = modal.find_element(By.XPATH, ".//button[contains(text(), 'Ja, löschen')]")                   
                    # Click the confirmation button
                    confirm_button.click()
                    delete_product_id_from_csv(product_id)
                    print("Item deleted")
                    time.sleep(1.5) # pause before next deletion
                    deleted_something = True
                    break
            if not deleted_something:
                print("No more items to delete.")
                break


    except Exception as e:
        print("Error while deleting items.")
        return

def delete_product_id_from_csv(product_id):
    rows = []
    with open("items.csv", newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        fieldnames = reader.fieldnames
        for row in reader:
            if row['id'] in product_id:
                row['id'] = ""
            rows.append(row)

    # Write the updated data back to the CSV file
    with open("items.csv", 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def find_sold_items(driver):
    driver.get("https://www.kibaza.de/product_list.php?status=1")
    time.sleep(1.5)
    close_modal(driver)
    time.sleep(1.5)

    all_filter_dropdowns = driver.find_elements(By.CSS_SELECTOR, "select.form-control")
    select = Select(all_filter_dropdowns[2])
    options = select.options
    select.select_by_index(4)

    filter_button = driver.find_element(By.NAME, "filterbutton")
    filter_button.click()

    sold_ids = set()
    elements = driver.find_elements(By.XPATH, "//*[string-length(text()) > 0]")
    for element in elements:
        if "ProduktId:" in element.text:
            product_id = element.text.split("#")[1].strip()
            product_id_number = re.findall(r'^\d+', product_id)[0]
            sold_ids.add(product_id_number)

    print("IDs of sold items found:", sold_ids)
    return sold_ids
            
def mark_sold_items_in_csv(sold_ids):
    rows = []
    with open("items.csv", newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        fieldnames = reader.fieldnames
        for row in reader:
            if row['id'] in sold_ids:
                row['sold'] = "sold"
            rows.append(row)

    # Write the updated data back to the CSV file
    with open("items.csv", 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print("sold items marked in csv")

def find_favored_items(driver):
    driver.get("https://www.kibaza.de/product_list.php?status=1")
    time.sleep(1.5)
    close_modal(driver)
    time.sleep(1.5)

    all_filter_dropdowns = driver.find_elements(By.CSS_SELECTOR, "select.form-control")
    select = Select(all_filter_dropdowns[2])
    options = select.options
    select.select_by_index(3)

    filter_button = driver.find_element(By.NAME, "filterbutton")
    filter_button.click()
    time.sleep(1.5) 

    fav_ids = set()
    elements = driver.find_elements(By.XPATH, "//a[contains(@href, 'productId=')]")
    for element in elements:
        href = element.get_attribute("href")
        match = re.search(r'productId=(\d+)', href)
        if match:
            fav_ids.add(match.group(1))
    print("IDs of favorite items found:", fav_ids)
    return fav_ids





    


def main():
    delete_favorites = input("Delete favored items? (y/n): ").lower() == 'y'

    service = Service(executable_path = "chromedriver.exe")
    driver = webdriver.Chrome(service = service)

    parser = argparse.ArgumentParser()
    parser.add_argument("--validate", action="store_true", help="Validate CSV categories before submission")
    args = parser.parse_args()

    if args.validate:
        if not validate_categories("items.csv"):
            print("\nValidation failed - fix CSV errors before submission")
            sys.exit(1)
        else:
            print("All categories validated successfully!")
        sys.exit(0)

    try:
        login(driver, EMAIL, SELLER_NUMBER)
        time.sleep(0.5)  # Post-modal dismissal
        
        # find out which items were sold
        sold_ids = find_sold_items(driver)
        # mark sold items in csv
        mark_sold_items_in_csv(sold_ids)

        items_to_spare = []
        if delete_favorites:
            # delete all items
            delete_all_items(driver, items_to_spare)
        else:
            # find favored items
            # delete all items except favored ones
            fav_ids = find_favored_items(driver)
            delete_all_items(driver, fav_ids)


        time.sleep(2)
    except Exception as e:
        print("An error occurred:", e)
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
