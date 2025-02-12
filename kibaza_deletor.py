#!/usr/bin/env python3
import csv
import time
import undetected_chromedriver as uc
from selenium.webdriver.support.select import Select
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys  # Add this import
from datetime import datetime
import argparse
import sys

from selenium import webdriver
from selenium.webdriver.chrome.service import Service

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
    driver.get("https://www.kibaza.de/archemedes")
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
# Add this above SUBCATEGORY_MAP in your code
CATEGORY_MAP = {
    "Bekleidung": "1",
    "Schuhe": "13",
    "Outdoorbekleidung": "25",
    "Spiel & Spaß": "3",
    "Sport": "27",
    "Bücher": "14",
    "Rucksäcke & Taschen": "6",
    "Essen und Trinken": "26",
    "Babyausstattung": "7",
    "Fahrradsitze & Anhänger": "23",
    "Schule & Lernen": "28",
    "Auto Kindersitze": "24",
    "Kinderfahrzeuge & Zubehör": "22",
    "Kinderwagen & Buggies": "4",
    "Für die Mama": "8",
    "Kinderzimmer": "5",
    "Saisonal": "2",
    "Sonstiges": "9"
}

SUBCATEGORY_CONTAINER_MAP = {
    "1": "js-subcategory-container-1",
    "13": "js-subcategory-container-13",
    "25": "js-subcategory-container-25",
    "3": "js-subcategory-container-3",
    "27": "js-subcategory-container-27",
    "14": "js-subcategory-container-14",
    "6": "js-subcategory-container-6",
    "26": "js-subcategory-container-26",
    "7": "js-subcategory-container-7",
    "23": "js-subcategory-container-23",
    "28": "js-subcategory-container-28",
    "24": "js-subcategory-container-24",
    "22": "js-subcategory-container-22",
    "4": "js-subcategory-container-4",
    "8": "js-subcategory-container-8",
    "5": "js-subcategory-container-5",
    "2": "js-subcategory-container-2",
    "9": "js-subcategory-container-9"
}

SUBCATEGORY_MAP = {
    "Bekleidung": {
        "Paket": "186",
        "Oberteile": "1",
        "Hosen": "2",
        "Kleider & Röcke": "11",
        "Schlafanzüge": "4",
        "Socken": "6",
        "Strumpfhosen": "152",
        "Unterwäsche & Bodies": "5",
        "Badebekleidung & Schwimmhilfen": "9",
        "Accessoires": "10",
        "Sonstiges": "22"
    },
    "Schuhe": {
        "Warme Schuhe": "118",
        "Sandalen & FlipFlops": "119",
        "Badeschuhe": "120",
        "Gummistiefel": "121",
        "Turnschuhe": "122",
        "Ballerinas": "124",
        "Halbschuhe & Stiefel (ungefüttert)": "125",
        "Hausschuhe": "138",
        "Crocs": "139",
        "Baby- & Krabbelschuhe": "143",
        "Sonstiges": "7"
    },
    "Outdoorbekleidung": {
        "Leichte Jacken & Westen": "112",
        "Winterjacken": "113",
        "Schneeanzüge": "114",
        "Regen / Matschkleidung": "115",
        "Overalls / Wagenanzüge": "116",
        "Schals & Tücher": "144",
        "Mützen & Kappen": "8",
        "Handschuhe": "31",
        "Sonstiges": "3"
    },
    "Spiel & Spaß": {
        "Baby": "23",
        "Puppen & Zubehör": "18",
        "Actionfigur/Spielfigur": "151",
        "Kuscheltiere": "67",
        "Lego, Duplo & Co.": "13",
        "Playmobil": "14",
        "Fahrzeuge & Zubehör": "12",
        "Werkzeug": "104",
        "Instrumente": "102",
        "Für Draussen": "101",
        "Tiere": "100",
        "Puzzle": "16",
        "Würfelspiele": "149",
        "Spiele": "29",
        "Spielküche & Kaufladen": "27",
        "Schwimmhilfen": "183",
        "Badespielzeug": "30",
        "CDs, DVDs & Toniefiguren": "21",
        "Smart Watches": "182",
        "Spielekonsolen": "19",
        "Malen & Basteln": "28",
        "Schmuck": "26",
        "Sonstiges": "20"
    },
    "Sport": {
        "Reiten": "162",
        "Fussball": "163",
        "Radsport": "164",
        "Inlineskaten": "165",
        "Eishockey": "166",
        "Eislaufen": "167",
        "Ski & Langlauf": "168",
        "Ballett": "171",
        "Wandern & Trekking": "172",
        "Laufen": "173",
        "Boxen": "178",
        "Schläger & Bälle": "169",
        "Sonstiges": "170"
    },
    "Bücher": {
        "Babybücher (0-2 Jahre)": "74",
        "Bücher für Kleinkinder (2-3 Jahre)": "75",
        "Bücher für Kleinkinder (ab 3 Jahre)": "76",
        "Bücher für Kleinkinder (ab 4 Jahre)": "77",
        "Erstleser (6-8 Jahre)": "78",
        "Leseprofis (9-12 Jahre)": "79",
        "Jugendbücher": "80",
        "Sachbücher für Kinder": "81",
        "Mal- und Bastelbücher": "83",
        "Kochbücher für Kinder": "82",
        "Schwangerschaftsbücher": "84",
        "Elternratgeber": "85",
        "Weihnachts- & Adventsbücher": "147",
        "Osterbücher": "148",
        "Romane für Erwachsene": "179",
        "Sonstiges": "180"
    },
    "Rucksäcke & Taschen": {
        "Schultaschen & -tüten": "129",
        "Rucksäcke": "130",
        "Umhängetaschen": "131",
        "Handtaschen": "132",
        "Geldbörsen": "133",
        "Turnbeutel": "137",
        "Sonstiges": "47"
    },
    "Essen und Trinken": {
        "Trinkflaschen und Becher": "153",
        "Brotzeitdosen": "154",
        "Kindergeschirr und -besteck": "155",
        "Sonstiges": "156"
    },
    "Babyausstattung": {
        "Schnuller, Fläschchen & Co.": "89",
        "Alles rund um´s Stillen": "99",
        "Füttern": "32",
        "Babydecken & Bettwäsche": "90",
        "Babybetten & Wiegen": "95",
        "Spieluhren & Mobiles": "96",
        "Schlafsäcke": "97",
        "Wippen": "91",
        "Sicherheit": "92",
        "Wickeltaschen": "94",
        "Wickeln & Töpfchen": "36",
        "Hochstühle": "98",
        "Tragehilfe": "43",
        "Babyschalen": "34",
        "Badewannen & Sitze": "111",
        "Fußsäcke": "103",
        "Laufgitter": "33",
        "Sonstiges": "41"
    },
    "Fahrradsitze & Anhänger": {
        "Fahrradsitze": "107",
        "Anhänger": "108",
        "Sonstiges": "109"
    },
    "Schule & Lernen": {
        "Lernhilfen": "175",
        "Schulbücher": "177",
        "Schulzubehör": "176",
        "Sonstiges": "174"
    },
    "Auto Kindersitze": {
        "Kindersitze": "110",
        "Zubehör": "181"
    },
    "Kinderfahrzeuge & Zubehör": {
        "Fahrradhelme": "140",
        "Fahrräder": "134",
        "Dreiräder": "135",
        "Bobbycar": "136",
        "Roller": "141",
        "Laufrad": "142",
        "Sonstiges": "37"
    },
    "Kinderwagen & Buggies": {
        "Kinderwagen & Buggies": "86",
        "Zubehör": "87"
    },
    "Für die Mama": {
        "Umstandshosen": "126",
        "Kleider": "127",
        "Oberteile": "128",
        "Umstandsjacken": "145",
        "Umstandsunterwäsche": "146",
        "Sonstiges": "48"
    },
    "Kinderzimmer": {
        "Deko": "40",
        "Textilien": "39",
        "Ordnungshelfer": "184",
        "Möbel": "38",
        "Sonstiges": "66"
    },
    "Saisonal": {
        "Kostüme": "45",
        "Ostern": "24",
        "Weihnachten": "25",
        "Herbst": "106",
        "Kindergeburtstag": "185"
    },
    "Sonstiges": {}
}

SIZE_MAP = {
    "XS": "größe[1]",
    "S": "größe[2]",
    "M": "größe[3]",
    "L": "größe[4]",
    "XL": "größe[5]",
    "XXL": "größe[6]",
    "20 Zoll": "größe[134]",
    "24 Zoll": "größe[141]"
}

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By


def select_subcategory(driver, category_id, subcategory_value):
    """
    Select the subcategory for the given category.
    If the subcategory element is not found and no subcategory_value is provided,
    the function assumes no subcategory is required and returns True.
    """
    try:
        # Build a CSS selector for the subcategory container
        container_selector = f"div.js-subcategory-container-{category_id}"
        # Wait for the container element to appear (even if it's hidden, we rely on its existence)
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, container_selector))
            )
        except Exception:
            if not subcategory_value:
                print(f"No subcategory needed for category {category_id}")
                return True
            else:
                raise Exception(f"Subcategory container '{container_selector}' not found for required subcategory value '{subcategory_value}'")
        
        # If no subcategory value is provided, skip selection.
        if not subcategory_value:
            print("No subcategory value provided; skipping subcategory selection.")
            return True
        
        import json
        # Build CSS selector for the <select> element inside the container (unchanged)
        select_selector = f'select.js-subcategory-{category_id}[name="subcategory[]"]'
        
        # Use json.dumps to safely embed the selector and subcategory value.
        selector_js = json.dumps(select_selector)
        value_js = json.dumps(subcategory_value)
        
        js_script = f"""
            const select = document.querySelector({selector_js});
            if (select) {{
                select.value = {value_js};
                select.dispatchEvent(new Event('change', {{ bubbles: true }}));
            }} else {{
                throw "Subcategory element not found for selector: " + {selector_js};
            }}
        """
        driver.execute_script(js_script)
        # Verify the value was set
        current_value = driver.execute_script(f"return document.querySelector('{select_selector}').value")
        if current_value != subcategory_value:
            raise Exception(f"Failed to set subcategory: expected {subcategory_value}, got {current_value}")
        print(f"Subcategory set to {current_value} successfully")
        return True
    except Exception as e:
        print("Subcategory selection error:", e)
        return False
    
def post_item(driver, item_data):
    driver.get("https://www.kibaza.de/product_add.php")
    time.sleep(1.5)
    close_modal(driver)
    time.sleep(1.5)
    
    try:
        # Validate required fields
        required_fields = ['title', 'category', 'subcategory', 'price']
        for field in required_fields:
            if field not in item_data:
                print(f"Missing required field: {field}")
                return

        # Fill basic fields
        driver.find_element(*NAME_SELECTOR).send_keys(item_data["title"])
        driver.find_element(*DESCRIPTION_SELECTOR).send_keys(item_data.get("description", ""))
        driver.find_element(*PRICE_SELECTOR).send_keys(str(item_data["price"]))

        # Handle category selection
        try:
            category_name = item_data["category"]
            category_value = CATEGORY_MAP.get(category_name)
            if not category_value:
                print(f"Invalid category: {category_name}. Valid options: {', '.join(CATEGORY_MAP.keys())}")
                return
                
            category_select = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(CATEGORY_SELECTOR)
            )
            Select(category_select).select_by_value(category_value)
            time.sleep(1)  # Allow DOM update
            
        except Exception as e:
            print(f"Category selection failed: {str(e)}")
            return

        # Handle subcategory selection
        try:
            # Directly target the select element using category value
            select_selector = f'select.js-subcategory-{category_value}[name="subcategory[]"]'
            print(f"Looking for subcategory selector: {select_selector}")  # DEBUG

            # Wait for select element to be present
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, select_selector))
            )
            print("Found subcategory select element")  # DEBUG

            # Get subcategory value from mapping
            subcategory_name = item_data["subcategory"]
            print(f"Raw subcategory from CSV: {subcategory_name}")  # DEBUG
            subcategory_value = SUBCATEGORY_MAP[category_name].get(subcategory_name)

            if not subcategory_value:
                print(f"Invalid subcategory: {subcategory_name}. Valid options: {list(SUBCATEGORY_MAP[category_name].keys())}")
                return

            if not select_subcategory(driver, category_value, subcategory_value):
                print("Error setting subcategory.")
                return False

            # New verification: Check the select's value directly
            current_value = driver.execute_script(f"return document.querySelector('{select_selector}').value")
            print(f"Current subcategory value: {current_value}   (expected: {subcategory_value})")
            
            if current_value != subcategory_value:
                raise Exception(f"Value mismatch. Expected {subcategory_value}, got {current_value}")

            print("Subcategory value set successfully")

        except Exception as e:
            print(f"Subcategory selection failed at step: {str(e)}")
            # Additional debug: Check current value
            current_value = driver.execute_script(f"return document.querySelector('{select_selector}').value")
            print(f"Current subcategory value after attempt: {current_value}")
            return
        # After subcategory selection and before form submission, upload image if provided
        import os
        image_filenames = item_data.get("images")
        if image_filenames:
            # image_path = os.path.join(os.getcwd(), image_filename)
            # print("Uploading image from:", image_path)
            # image_input = driver.find_element(By.NAME, "productImages[]")
            # image_input.send_keys(image_path)

            # Assuming 'images' is a string containing comma-separated filenames
            split_image_filenames = [filename.strip() for filename in image_filenames.split(',')]

            # Create a list of full file paths
            file_paths = [os.path.join(os.getcwd(), filename) for filename in split_image_filenames]

            # Join the file paths with newline characters
            multiple_file_paths = "\n".join(file_paths)

            print("Uploading image from:", multiple_file_paths)
            image_input_buttons = driver.find_elements(By.NAME, "productImages[]")
            multiple_images_button = image_input_buttons[3]
            multiple_images_button.send_keys(multiple_file_paths)

        try:
            CONDITION_SELECTOR = (By.NAME, "productCondition")

            if item_data.get("condition"):
                try:
                    condition_map = {
                        "new": "Neu",
                        "used": "Gebraucht",
                        "defect": "Defekt"
                    }
                    condition_text = condition_map.get(item_data["condition"].lower())
                    if not condition_text:
                        raise ValueError(f"Invalid condition: {item_data['condition']}")
                        
                    Select(driver.find_element(*CONDITION_SELECTOR)).select_by_visible_text(condition_text)
                except Exception as e:
                    print(f"Failed to set condition: {str(e)}")
                    return
            else:
                print("Warning: No condition specified, using default")
                Select(driver.find_element(*CONDITION_SELECTOR)).select_by_index(1)  # Default to first option
            # Handle dynamic fields
            if item_data.get("size"):
                Select(driver.find_element(*SIZE_SELECTOR)).select_by_visible_text(item_data["size"])
            # Conditional brand and gender handling
            if item_data.get("brand"):
                try:
                    brand_input = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located(BRAND_SELECTOR)
                    )
                    brand_input.clear()
                    brand_input.send_keys(item_data["brand"])
                    time.sleep(0.3)
                except:
                    print("Brand field not present for this category")
            if item_data.get("gender"):
                try:
                    gender_field = WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located(GENDER_SELECTOR)
                    )
                    gender_map = {
                        "Herren": "Männlich",
                        "Damen": "Weiblich",
                        "Unisex": "Unisex"
                    }
                    mapped_gender = gender_map.get(item_data["gender"])
                    if not mapped_gender:
                        raise ValueError(f"Invalid gender: {item_data['gender']}")
                    Select(gender_field).select_by_visible_text(mapped_gender)
                except Exception as e:
                    print(f"Gender selection skipped: {str(e)}")
        except Exception as e:
            print(f"Error setting item details: {str(e)}")
       
        # Submit form
        try:
            # Wait for button to be clickable with longer timeout
            submit_btn = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable(SUBMIT_ITEM_BUTTON_SELECTOR)
            )
            
            # Scroll to center of viewport
            driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", 
                submit_btn
            )
            time.sleep(0.8)  # Allow smooth scroll to complete
            
            print("Attempting form submission...")
            
            # Try normal click first
            try:
                submit_btn.click()
            except Exception as click_error:
                print(f"Standard click failed: {str(click_error)}, using JS fallback")
                driver.execute_script("arguments[0].click();", submit_btn)
            
            # Wait for product ID in URL
            WebDriverWait(driver, 30).until(
                lambda d: "justCreatedProductId=" in d.current_url
            )
            product_id = driver.current_url.split("justCreatedProductId=")[1].split("&")[0]
            print(f"Item successfully created! Product ID: {product_id}")
            
        except Exception as e:
            # Check if we actually succeeded despite error
            if "justCreatedProductId=" in driver.current_url:
                product_id = driver.current_url.split("justCreatedProductId=")[1].split("&")[0]
                print(f"Success detected retroactively! Product ID: {product_id}")
            else:
                print(f"True failure: {str(e)}")
                # Capture screenshot and page source for debugging
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                driver.save_screenshot(f"submit_error_{timestamp}.png")
                with open(f"page_source_{timestamp}.html", "w") as f:
                    f.write(driver.page_source)
                print(f"Saved debug files: submit_error_{timestamp}.png and page_source_{timestamp}.html")
                return
    except Exception as e:
        print(f"Error posting item: {str(e)}")
        raise


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

def delete_all_items(driver):
        driver.get("https://www.kibaza.de/product_list.php?status=1")
        time.sleep(1.5)
        close_modal(driver)
        time.sleep(1.5)
        
        button_found = True
        while button_found:
            try:
                delete_button = driver.find_element(By.CSS_SELECTOR, "button.btn.btn-danger.btn-sm")
                delete_button.click() 
                confirm_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Ja, löschen')]")
                driver.execute_script("arguments[0].click();", confirm_button)
                time.sleep(1.5) # pause before next deletion

            except Exception as e:
                print("No more items to delete.")
                return




#     # Wait for button to be clickable with longer timeout
#             submit_btn = WebDriverWait(driver, 15).until(
#                 EC.element_to_be_clickable(SUBMIT_ITEM_BUTTON_SELECTOR)
#             )
            
#             # Scroll to center of viewport
#             driver.execute_script(
#                 "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", 
#                 submit_btn
#             )
#             time.sleep(0.8)  # Allow smooth scroll to complete
            
#             print("Attempting form submission...")
            
#             # Try normal click first
#             try:
#                 submit_btn.click()
# input_element = driver.find_element(By.CLASS_NAME, "gLFyf")
# input_element.send_keys("test Suche" + Keys.ENTER)


def main():
    # Replace these credentials with your actual values.
    email = "william.swartwood86@gmail.com"
    seller_number = "V28296"
    
    # Set up Selenium WebDriver using Chrome.
    # chrome_options = uc.ChromeOptions()
    # chrome_options.binary_location = "/usr/bin/chromium"
    # chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument("--disable-dev-shm-usage")
    # chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
    
    # driver = uc.Chrome(
    #     options=chrome_options,
    #     version_main=133
    # )

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
        login(driver, email, seller_number)
        time.sleep(0.5)  # Post-modal dismissal
        
        # delete all items
        delete_all_items(driver)

        time.sleep(2)
    except Exception as e:
        print("An error occurred:", e)
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
