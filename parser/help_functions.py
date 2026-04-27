import random
import time

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


def get_items_count(driver):
    return len(driver.find_elements(By.CLASS_NAME, "product-card"))


def scroll_to_bottom(driver):
    last_count = get_items_count(driver)
    stuck_counter = 0  # Счетчик попыток, если количество товаров не растет

    while True:
        actions = ActionChains(driver)
        actions.send_keys(Keys.PAGE_DOWN).perform()

        # Случайная пауза
        time.sleep(random.uniform(0.8, 1.3))

        current_count = get_items_count(driver)

        # Проверяем позицию: мы физически внизу текущего DOM?
        current_pos = driver.execute_script("return window.pageYOffset + window.innerHeight;")
        total_height = driver.execute_script("return document.body.scrollHeight;")

        # Если мы «уперлись» в текущее дно
        if abs(total_height - current_pos) < 10:
            if current_count > last_count:
                # Товары добавились, сбрасываем счетчик и идем дальше
                last_count = current_count
                stuck_counter = 0
            else:
                stuck_counter += 1
                print(f"Внизу страницы. Попытка {stuck_counter} из 3...")
                time.sleep(1.5)  # Даем WB время "подумать" и подгрузить

                if stuck_counter >= 3:
                    print("Товары больше не подгружаются. Конец.")
                    break
        else:
            # Мы еще не внизу текущего куска, просто продолжаем скроллить
            stuck_counter = 0
