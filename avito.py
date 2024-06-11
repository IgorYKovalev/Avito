import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
import json
import pandas as pd
import dateparser


# Функция для извлечения данных из одного поста
def extract_post_data(post):
    data = {}

    # Извлечение времени размещения вакансии
    try:
        posted_data = post.find_element(
            By.CLASS_NAME, 'iva-item-dateInfoStep-_acjp').find_element(By.TAG_NAME, 'p').text

        parsed_date = dateparser.parse(posted_data)
        if parsed_date:
            posted_data = parsed_date.strftime('%Y-%m-%d')
        else:
            posted_data = 'Нет данных'

        data['posted_data'] = posted_data

    except:
        data['posted_data'] = 'Нет данных'

    # Извлечение названия
    try:
        data['name'] = post.find_element(By.CLASS_NAME, 'iva-item-titleStep-pdebR').find_element(By.TAG_NAME, 'h3').text
    except:
        data['name'] = 'Нет названия'

    # Извлечение цены
    try:
        price_meta = post.find_element(By.CLASS_NAME, 'price-price-JP7qe').find_elements(By.TAG_NAME, 'meta')
        for meta in price_meta:
            if meta.get_attribute('itemprop') == 'price':
                data['price'] = int(meta.get_attribute('content'))
                break
    except:
        data['price'] = None

    # Извлечение описания
    try:
        data['description'] = post.find_element(By.CLASS_NAME, 'iva-item-descriptionStep-C0ty1').text
    except:
        data['description'] = 'Нет описания'

    # Извлечение ссылки и ID
    try:
        link_element = post.find_element(By.CLASS_NAME, 'iva-item-titleStep-pdebR').find_element(By.TAG_NAME, 'a')
        data['url'] = link_element.get_attribute('href')
        data['id'] = data['url'].split('_')[-1].split('?')[0]  # Извлечение ID из URL
    except:
        data['url'] = 'Нет ссылки'
        data['id'] = ''

    # Извлечение города
    try:
        data['city'] = post.find_element(By.CLASS_NAME, 'geo-root-zPwRk').find_element(By.TAG_NAME, 'span').text
    except:
        data['city'] = 'Нет города'

    return data


# Функция для извлечения данных с текущей страницы
def get_posts_from_page(driver):
    posts_data = []
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "items-items-kAJAg")))
    blocks = driver.find_element(By.CLASS_NAME, "items-items-kAJAg")
    posts = blocks.find_elements(By.CLASS_NAME, 'iva-item-body-KLUuy')
    for post in posts:
        try:
            description = post.find_element(By.CLASS_NAME, 'iva-item-descriptionStep-C0ty1').text
        except:
            description = 'Нет'

        if description != 'Нет':
            post_data = extract_post_data(post)
            posts_data.append(post_data)
    return posts_data


# Функция для перехода на следующую страницу
def navigate_to_next_page(driver):
    try:
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-marker='pagination-button/nextPage']"))
        )
        driver.execute_script("arguments[0].scrollIntoView();", next_button)  # Прокрутка до кнопки
        driver.execute_script("arguments[0].click();", next_button)  # JavaScript-клик по кнопке
        # Ожидание загрузки новой страницы
        WebDriverWait(driver, 10).until(
            EC.staleness_of(next_button)  # ожидание, что старая кнопка станет неактуальной (страница обновилась)
        )
        time.sleep(2)
        return True
    except Exception as e:
        print(f"Ошибка перехода на следующую страницу: {e}")
        return False


# Функция для сохранения данных в JSON
def save_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# Функция для сохранения данных в Excel
def save_to_excel(data, filename):
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)


# Основная функция для запуска скрипта
def main(url, num_pages=None):
    base = []
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(options=options)
    stealth(
        driver,
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )
    driver.get(url)
    time.sleep(5)

    page_count = 0
    while True:
        base.extend(get_posts_from_page(driver))
        page_count += 1
        if num_pages is not None and page_count >= num_pages:
            break
        if not navigate_to_next_page(driver):
            break

    driver.quit()
    return base


if __name__ == '__main__':
    url = input("Введите URL страницы для сбора данных: ")
    num_pages = int(input("Введите количество страниц для сбора данных (или 0 для сбора всех страниц): "))
    if num_pages == 0:
        num_pages = None

    data = main(url, num_pages)

    save_format = input("Введите формат сохранения (json/excel): ").strip().lower()
    if save_format == "json":
        filename = input("Введите имя файла для сохранения (например, data.json): ")
        save_to_json(data, filename)
    elif save_format == "excel":
        filename = input("Введите имя файла для сохранения (например, data.xlsx): ")
        save_to_excel(data, filename)
    else:
        print("Неподдерживаемый формат. Пожалуйста, выберите 'json' или 'excel'.")
