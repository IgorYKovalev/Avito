from bs4 import BeautifulSoup
import os
import pandas as pd
import re
import json


# Функция для извлечения данных из одного HTML файла
def extract_data_from_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    soup = BeautifulSoup(content, 'html.parser')

    data = {}

    # Извлечение данных из JSON в <script>
    script_tag = soup.find('script', string=re.compile(r'"@type": "JobPosting"'))
    if script_tag:
        json_text = re.search(r'{.*}', script_tag.string, re.DOTALL).group()
        json_data = json.loads(json_text)

        data['date_posted'] = json_data.get('datePosted')
        data['job_id'] = json_data.get('identifier', {}).get('value')
        data['job_title'] = json_data.get('title')
        data['min_value'] = json_data.get('baseSalary', {}).get('value', {}).get('minValue')
        data['max_value'] = json_data.get('baseSalary', {}).get('value', {}).get('maxValue')
        # Рассчёт средней зарплаты
        if data['min_value'] and data['max_value']:
            data['average_salary'] = (data['min_value'] + data['max_value']) / 2
        elif data['min_value']:
            data['average_salary'] = data['min_value']
        elif data['max_value']:
            data['average_salary'] = data['max_value']
        else:
            data['average_salary'] = None

        data['currency'] = json_data.get('baseSalary', {}).get('currency')
        # Очистка поля description от HTML тегов
        raw_description = json_data.get('description', '')
        data['description'] = BeautifulSoup(raw_description, 'html.parser').get_text(separator=" ")

        data['employment_type'] = json_data.get('employmentType')
        data['company_name'] = json_data.get('hiringOrganization', {}).get('name')
        data['industry'] = json_data.get('industry')
        data['address_region'] = json_data.get('jobLocation', {}).get('address', {}).get('addressRegion')
        data['street_address'] = json_data.get('jobLocation', {}).get('address', {}).get('streetAddress')
        data['latitude'] = json_data.get('jobLocation', {}).get('geo', {}).get('latitude')
        data['longitude'] = json_data.get('jobLocation', {}).get('geo', {}).get('longitude')
        data['job_url'] = json_data.get('sameAs')

    return data


# Функция для обработки всех HTML файлов в папке
def parse_all_html_files(folder='html'):
    all_data = []
    for filename in os.listdir(folder):
        if filename.endswith('.html'):
            file_path = os.path.join(folder, filename)
            file_data = extract_data_from_html(file_path)
            all_data.append(file_data)

    return all_data


# Сохранение данных в Excel
def save_data_to_excel(data, filename='parsed_data.xlsx'):
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)


# Основная функция для запуска процесса парсинга и сохранения данных
def main():
    folder = 'html'
    parsed_data = parse_all_html_files(folder)
    save_data_to_excel(parsed_data)


if __name__ == '__main__':
    main()
