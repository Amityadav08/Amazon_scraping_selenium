from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import json

AMAZON_USERNAME = "your_email@example.com"
AMAZON_PASSWORD = "your_password"

CATEGORIES = [
    "https://www.amazon.in/gp/bestsellers/kitchen/ref=zg_bs_nav_kitchen_0",
    "https://www.amazon.in/gp/bestsellers/shoes/ref=zg_bs_nav_shoes_0",
    "https://www.amazon.in/gp/bestsellers/computers/ref=zg_bs_nav_computers_0",
    "https://www.amazon.in/gp/bestsellers/electronics/ref=zg_bs_nav_electronics_0",
]

def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    return driver

def amazon_login(driver):
    driver.get("https://www.amazon.in")
    try:
        driver.find_element(By.ID, "nav-link-accountList").click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "ap_email")))
        driver.find_element(By.ID, "ap_email").send_keys(AMAZON_USERNAME)
        driver.find_element(By.ID, "continue").click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "ap_password")))
        driver.find_element(By.ID, "ap_password").send_keys(AMAZON_PASSWORD)
        driver.find_element(By.ID, "signInSubmit").click()
    except Exception as e:
        driver.quit()

def scrape_category(driver, category_url):
    driver.get(category_url)
    time.sleep(2)
    category_name = driver.find_element(By.XPATH, "//span[@class='zg_selected']").text
    products = []
    for page in range(1, 4):
        try:
            product_elements = driver.find_elements(By.XPATH, "//div[@class='zg-grid-general-faceout']")
            for product in product_elements:
                try:
                    name = product.find_element(By.CSS_SELECTOR, ".p13n-sc-truncated").text
                    price = product.find_element(By.CSS_SELECTOR, ".p13n-sc-price").text
                    discount = product.find_element(By.CSS_SELECTOR, ".p13n-sc-discount").text if product.find_elements(By.CSS_SELECTOR, ".p13n-sc-discount") else "N/A"
                    rating = product.find_element(By.CSS_SELECTOR, ".a-icon-alt").text if product.find_elements(By.CSS_SELECTOR, ".a-icon-alt") else "N/A"
                    seller = "Amazon"
                    images = [img.get_attribute("src") for img in product.find_elements(By.CSS_SELECTOR, ".p13n-sc-product-image")]
                    if discount != "N/A" and int(discount.strip('%')) > 50:
                        products.append({
                            "Name": name,
                            "Price": price,
                            "Discount": discount,
                            "Rating": rating,
                            "Category": category_name,
                            "Sold By": seller,
                            "Images": images,
                        })
                except Exception as e:
                    continue
            next_button = driver.find_element(By.CSS_SELECTOR, "li.a-last a")
            driver.execute_script("arguments[0].click();", next_button)
            time.sleep(2)
        except Exception as e:
            break
    return products

def save_to_csv(data, filename):
    keys = data[0].keys()
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)

def save_to_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def main():
    driver = init_driver()
    try:
        amazon_login(driver)
        all_products = []
        for category_url in CATEGORIES:
            products = scrape_category(driver, category_url)
            all_products.extend(products)
        save_to_csv(all_products, "amazon_best_sellers.csv")
        save_to_json(all_products, "amazon_best_sellers.json")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
