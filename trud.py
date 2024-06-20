import requests
from openpyxl import Workbook
from bs4 import BeautifulSoup
import time
import re

# Базовый URL API
base_api_url = "http://opendata.trudvsem.ru/api/v1/vacancies/region/"

# Список регионов
regions = [
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
    30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56,
    57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 85, 76, 77, 78, 79, 80, 81, 82, 83,
    84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 99
]

# Создание нового Excel файла
wb = Workbook()
ws = wb.active
ws.title = "Вакансии"
ws.append([
    "id",
    "source",
    "region_code",
    "region_name",
    "company_code",
    "inn",
    "kpp",
    "company_name",
    "ogrn",
    "company_url",
    "creation_date",
    "salary",
    "salary_min",
    "salary_max",
    "job_name",
    "vac_url",
    "employment",
    "schedule",
    "duty",
    "specialisation",
    "education",
    "qualification",
    "experience",
    "address_location",
    "address_lng",
    "address_lat"
])


# Функция для получения данных о вакансиях
def get_vacancies(api_url, params):
    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Ошибка при запросе данных: {response.status_code}")
        return None


# Функция для удаления HTML-тегов из текста
def remove_html_tags(text):
    if text:
        soup = BeautifulSoup(text, "html.parser")
        return soup.get_text(separator=" ").strip()
    return " "


# Функция для удаления недопустимых символов и конвертации в строку
def clean_string(s):
    if s is None:
        return ""
    s = str(s)
    # Удаляем все недопустимые символы с помощью регулярного выражения
    s = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', s)
    return s


# Функция для сохранения данных в Excel
def save_to_excel(vacancies):
    for item in vacancies:
        vacancy = item.get('vacancy', {})
        ws.append([
            clean_string(vacancy.get('id', '')),
            clean_string(vacancy.get('source', '')),
            clean_string(vacancy.get('region', {}).get('region_code', '')),
            clean_string(vacancy.get('region', {}).get('name', '')),
            clean_string(vacancy.get('company', {}).get('companycode', '')),
            clean_string(vacancy.get('company', {}).get('inn', '')),
            clean_string(vacancy.get('company', {}).get('kpp', '')),
            clean_string(vacancy.get('company', {}).get('name', '')),
            clean_string(vacancy.get('company', {}).get('ogrn', '')),
            clean_string(vacancy.get('company', {}).get('url', '')),
            clean_string(vacancy.get('creation-date', '')),
            clean_string(vacancy.get('salary', '')),
            clean_string(vacancy.get('salary_min', '')),
            clean_string(vacancy.get('salary_max', '')),
            clean_string(vacancy.get('job-name', '')),
            clean_string(vacancy.get('vac_url', '')),
            clean_string(vacancy.get('employment', '')),
            clean_string(vacancy.get('schedule', '')),
            clean_string(remove_html_tags(vacancy.get('duty', ''))),
            clean_string(vacancy.get('category', {}).get('specialisation', '')),
            clean_string(vacancy.get('requirement', {}).get('education', '')),
            clean_string(remove_html_tags(vacancy.get('requirement', {}).get('qualification', ''))),
            clean_string(vacancy.get('requirement', {}).get('experience', '')),
            clean_string(vacancy.get('addresses', {}).get('address', [{}])[0].get('location', '')),
            clean_string(vacancy.get('addresses', {}).get('address', [{}])[0].get('lng', '')),
            clean_string(vacancy.get('addresses', {}).get('address', [{}])[0].get('lat', ''))
        ])


# Параметры запроса
params = {
    'offset': 0,
    'limit': 100,
}

# Получение данных по каждому региону
for region_id in regions:
    api_url = f"{base_api_url}{region_id}?text=кассир"
    params['offset'] = 0

    while True:
        data = get_vacancies(api_url, params)
        if data and 'results' in data and 'vacancies' in data['results']:
            vacancies = data['results']['vacancies']
            if not vacancies:
                break
            save_to_excel(vacancies)
            params['offset'] += params['limit']
            time.sleep(1)
        else:
            break

wb.save("vacancies.xlsx")
print("Данные успешно сохранены в vacancies.xlsx")
