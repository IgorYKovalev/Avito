import requests
from openpyxl import Workbook
from bs4 import BeautifulSoup


# меняем название вакансии после ?text=кассир или курьер и т д
# api_url = "http://opendata.trudvsem.ru/api/v1/vacancies?text=курьер"
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


# Функция для сохранения данных в Excel
def save_to_excel(vacancies):
    for item in vacancies:
        vacancy = item.get('vacancy', {})
        ws.append([
            vacancy.get('id', ''),
            vacancy.get('source', ''),
            vacancy.get('region', {}).get('region_code', ''),
            vacancy.get('region', {}).get('name', ''),
            vacancy.get('company', {}).get('companycode', ''),
            vacancy.get('company', {}).get('inn', ''),
            vacancy.get('company', {}).get('kpp', ''),
            vacancy.get('company', {}).get('name', ''),
            vacancy.get('company', {}).get('ogrn', ''),
            vacancy.get('company', {}).get('url', ''),
            vacancy.get('creation-date', ''),
            vacancy.get('salary', ''),
            vacancy.get('salary_min', ''),
            vacancy.get('salary_max', ''),
            vacancy.get('job-name', ''),
            vacancy.get('vac_url', ''),
            vacancy.get('employment', ''),
            vacancy.get('schedule', ''),
            remove_html_tags(vacancy.get('duty', '')),
            vacancy.get('category', {}).get('specialisation', ''),
            vacancy.get('requirement', {}).get('education', ''),
            remove_html_tags(vacancy.get('requirement', {}).get('qualification', '')),
            vacancy.get('requirement', {}).get('experience', ''),
            vacancy.get('addresses', {}).get('address', [{}])[0].get('location', ''),
            vacancy.get('addresses', {}).get('address', [{}])[0].get('lng', ''),
            vacancy.get('addresses', {}).get('address', [{}])[0].get('lat', '')
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
    else:
        break


wb.save("vacancies.xlsx")
print("Данные успешно сохранены в vacancies.xlsx")
