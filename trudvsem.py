import requests
from openpyxl import Workbook
from bs4 import BeautifulSoup
import time
import re

# меняем название вакансии после ?text=кассир или курьер и т.д.
# api_url = "http://opendata.trudvsem.ru/api/v1/vacancies/region/46?text=кассир"
api_url = "http://opendata.trudvsem.ru/api/v1/vacancies?text=кассир"

# Параметры запроса
params = {
    'offset': 0,
    'limit': 100
}

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
def get_vacancies(params):
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


# Получение данных постранично
while True:
    data = get_vacancies(params)
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
