import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from parser.help_functions import scroll_to_bottom
from selenium.webdriver.chrome.service import Service

# Если обычный webdriver.Chrome() не находит путь:
# service = Service(executable_path="/usr/bin/chromedriver")
# driver = webdriver.Chrome(service=service, options=options)


def run_selenium_parser(url_wb: str):
    options = Options()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--blink-settings=imagesEnabled=false")
    options.add_argument("--no-sandbox")

    browser = webdriver.Chrome(options=options)
    wait = WebDriverWait(browser, 15)

    try:

        browser.set_page_load_timeout(30)
        browser.get(url_wb)

        # Закрытие поп-ап окна
        try:
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "main-page__content")))
            body = browser.find_element(By.TAG_NAME, "body")
            body.send_keys(Keys.ESCAPE)
            time.sleep(1)
            print("Попап закрыт")
        except:
            browser.execute_script("window.stop();")
            body = browser.find_element(By.TAG_NAME, "body")
            body.send_keys(Keys.ESCAPE)
            time.sleep(1)
            print("Попап закрыт принудительно")

        # Принятие куков
        try:
            cookie_accept_btn = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "cookies__btn")))
            cookie_accept_btn.click()
            time.sleep(1)
            print("Куки подтверждены")
        except:
            pass

        try:
            wait_short = WebDriverWait(browser, 7)
            goods_count_elem = wait_short.until(EC.presence_of_element_located((By.CLASS_NAME, "goods-count")))
            print(f"Найдено товаров: {goods_count_elem.text}")
        except:
            # скорее всего, товаров по такой цене нет
            print("Товары по заданным фильтрам не найдены (пустая страница).")
            return []

        scroll_to_bottom(browser)

        product_list = browser.find_element(By.CLASS_NAME, "product-card-list")
        product_cards = product_list.find_elements(By.TAG_NAME, "article")
        print(f"Собрано карточек: {len(product_cards)}")

        scraped_data = list()

        for product_card in product_cards:
            name = product_card.find_element(By.CLASS_NAME, "product-card__name").text
            dirty_price = product_card.find_element(By.CLASS_NAME, "price__wrap").text
            price = int(''.join(filter(str.isdigit, dirty_price.split('\n')[0])))
            article = int(product_card.get_attribute("data-nm-id"))
            href = product_card.find_element(By.CLASS_NAME, "product-card__link").get_attribute("href")

            product = {
                "Наименование": name,
                "Артикул": article,
                "Цена сейчас": price,
                "Ссылка": href
            }
            scraped_data.append(product)

        return scraped_data
    except Exception as e:
        print(f"Ошибка: {e}")
        return None

    finally:
        browser.quit()
