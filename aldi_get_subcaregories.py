from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

driver = webdriver.Chrome()

driver.get("https://www.aldi.co.uk/")
wait = WebDriverWait(driver, 30)


cookies = wait.until(
    EC.element_to_be_clickable(
        (By.XPATH, '//button[@id="onetrust-accept-btn-handler"]')
    )
)
cookies.click()

harmburger_menu = wait.until(
    EC.element_to_be_clickable(
        (By.XPATH, "//span[@class='sr-only' and contains(text(), 'Aldi Menu')]")
    )
)
try:
    harmburger_menu.click()
except:
    driver.execute_script("arguments[0].click();", harmburger_menu)
# harmburger_menu.click()
time.sleep(2)
category_items = driver.find_elements(
    by=By.XPATH,
    value="//li[@class='header__item header__item--nav slim-fit js-list-toggle text-uppercase']",
)


for category_item in category_items:

    time.sleep(1)
    category = category_item.find_element(
        by=By.XPATH, value=".//span[@class='linkName ']"
    ).text
    print(category.upper())
    try:
        category_item.click()
    except:
        driver.execute_script("arguments[0].click();", category_item)
    time.sleep(1)

    category_groups = driver.find_elements(
        by=By.XPATH,
        value="//ul[@class='header__list header__list--secondary js-list js-second-level-submenu expanded']/li[@class='header__item header__item--secondary single-fourth js-list-toggle js-list-dropdown avoid-click-lg']",
    )
    for category_group in category_groups:
        group_name = category_group.find_element(by=By.XPATH, value="./div/a").text
        print(group_name)
        subcategories = category_group.find_elements(by=By.XPATH, value="./ul//li")
        for subcategory_elem in subcategories:
            try:
                subcategory = subcategory_elem.find_element(
                    by=By.XPATH, value=".//a"
                ).text
            except:
                continue
            subcategory_url = subcategory_elem.find_element(
                by=By.XPATH, value="./a"
            ).get_attribute("href")
            print(subcategory, subcategory_url)

    back_button = driver.find_element(
        by=By.XPATH, value="//div[@class='back_container js-menu-back']"
    )
    time.sleep(1)
    try:
        back_button.click()
    except:
        driver.execute_script("arguments[0].click();", back_button)
