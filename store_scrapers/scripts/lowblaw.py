from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from aldi import click, excluded_keyword_in
from scrapy.selector import Selector
from selenium.webdriver.common.action_chains import ActionChains
from csv import writer
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
import logging, json, os, sys, time, random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service


logging.basicConfig(level=logging.INFO)
DRIVER_EXECUTABLE_PATH = "./utils/chromedriver"


def hover(driver, element):
    action = ActionChains(driver)
    action.move_to_element(to_element=element)
    action.perform()
    time.sleep(1)


def extract_product_id(url):
    last_slash_index = url[::-1].index("/")
    return url[-last_slash_index:]


def load_all(driver):
    while True:
        try:
            load_more = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//button[@class='primary-button primary-button--load-more-button']",
                    )
                )
            )
            click(load_more, driver)
        except:
            break


def get_subcategories(driver):
    driver.get("https://www.loblaws.ca/")
    WebDriverWait(driver, 120).until(
        EC.presence_of_element_located((By.XPATH, "//nav[@class='primary-nav']"))
    )

    page_response = Selector(text=driver.page_source)

    categories = page_response.xpath(
        "//li[@class='primary-nav__list__item primary-nav__list__item--with-children']"
    )
    subcategories_list = []
    for category in categories[2:]:  # remove/slice foods(groceries) and seasonal shops
        category_name = category.xpath("./button/span//text()").get()

        subcategories = category.xpath("./ul/li")
        for subcategory in subcategories:
            subcategory_name = subcategory.xpath("./a/span//text()").get()
            subcategory_url = subcategory.xpath("./a/@href").get()
            if not subcategory_url.startswith("http"):
                subcategory_url = f"https://www.loblaws.ca{subcategory_url}"

    # groceries category and subcategory shows well in full window
    driver.maximize_window()

    groceries = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[@data-code='xp-455-food-departments']")
        )
    )
    hover(driver, groceries)
    category_elements = driver.find_elements(
        by=By.XPATH,
        value="//button[@data-code='xp-455-food-departments']/parent::li/ul/li",
    )
    for category_elem in category_elements:
        hover(driver, category_elem)
        category = category_elem.find_element(by=By.XPATH, value="./a/span").text
        subcategory_elements = driver.find_elements(
            by=By.XPATH,
            value="//ul[@data-code='xp-455-food-departments']//li[@class='primary-nav__list__item']",
        )
        for subcategory_elem in subcategory_elements:
            subcategory = subcategory_elem.find_element(
                by=By.XPATH, value="./a/span"
            ).text
            subcategory_url = subcategory_elem.find_element(
                by=By.XPATH, value="./a"
            ).get_attribute("href")

            subcategories_list.append(
                {
                    "category": category_name,
                    "subcategory": subcategory_name,
                    "subcategory_url": subcategory_url,
                }
            )

    return subcategories_list[::-1]  # start extraction from groceriies


def extract_products(driver, category, subcategory, subcategory_url, csv_writer):
    driver.get(subcategory_url)
    try:
        WebDriverWait(driver, 100).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//li[@class='product-tile-group__list__item']")
            )
        )
    except:
        logging.critical(f"{category}: {subcategory} not loaded\nURL: {subategory_url}")
    load_all(driver)

    product_response = Selector(text=driver.page_source)
    products = product_response.xpath("//li[@class='product-tile-group__list__item']")

    for product in products:

        brand = product.xpath(
            ".//span[@class='product-name__item product-name__item--brand']//text()"
        ).get()
        name = product.xpath(
            ".//span[@class='product-name__item product-name__item--name']//text()"
        ).get()
        price = " ".join(
            product.xpath(".//div[@class='selling-price-list__item']//text()").getall()
        )
        product_url = product.xpath(
            ".//a[@class='product-tile__details__info__name__link']/@href"
        ).get()
        if not product_url.startswith("http"):
            product_url = f"https://www.loblaws.ca{product_url}"
        product_id = extract_product_id(product_url)

        csv_writer.writerow(
            (name, brand, category, subcategory, product_url, product_id)
        )
    logging.info(f"Extracted {category}: {subcategory}")


def scrape_loblaws(driver, output_csv):
    with open(output_csv, "a") as csv_file:
        csv_writer = writer(csv_file)
        headers = (
            "name",
            "brand",
            "category",
            "subcategory",
            "product url",
            "product_id",
        )
        csv_writer.writerow(headers)

        subcategories_list = get_subcategories(driver)

        for subcategories_dict in subcategories_list:
            category = subcategories_dict["category"]
            subcategory = subcategories_dict["subcategory"]
            subcategory_url = subcategories_dict["subcategory_url"]

            extract_products(driver, category, subcategory, subcategory_url, csv_writer)


if __name__ == "__main__":

    service = Service(DRIVER_EXECUTABLE_PATH)
    driver = webdriver.Chrome(service=service)

    # scrape_loblaws(driver, "loblaws_products.csv")
    get_subcategories(driver)
