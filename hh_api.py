import requests
from typing import Iterable
from itertools import count

from data_processing import predict_rub_salary


HH_BASE_URL = "https://api.hh.ru/vacancies"
HH_MAX_VACANCIES_PER_PAGE = 100
HH_MOSCOW_INDEX = 1


def predict_hh_rub_salary(vacancy: dict) -> int | None:
    salary = vacancy.get("salary")
    if salary and salary["currency"] == "RUR":
        salary_from = salary.get("from")
        salary_to = salary.get("to")

        return predict_rub_salary(salary_from, salary_to)


def get_all_hh_vacancies(
        url: str,
        search_request: str
        ) -> list:

    vacancies = []
    for page in count(0):
        payload = {
            "text": f"Программист {search_request}",
            "area": HH_MOSCOW_INDEX,
            "per_page": HH_MAX_VACANCIES_PER_PAGE,
            "page": page
        }

        page_response = requests.get(url, params=payload)
        page_response.raise_for_status()

        page_data = page_response.json()
        vacancies.extend(page_data["items"])
        if page >= page_data["pages"]-1:
            break
    return vacancies


def get_stats_on_hh_vacancies(search_requests: Iterable) -> dict:
    vacancy_stats = {}
    for search_request in search_requests:
        amount_of_salaries = 0
        vacancies_processed = 0
        vacancies = get_all_hh_vacancies(HH_BASE_URL, search_request)
        vacancies_found = len(vacancies)

        for vacancy in vacancies:
            predicted_salary = predict_hh_rub_salary(vacancy)

            if predicted_salary:
                amount_of_salaries = amount_of_salaries + predicted_salary
                vacancies_processed += 1

        if vacancies_processed:
            average_salary = int(amount_of_salaries / vacancies_processed)
        else:
            average_salary = 0

        vacancy_stats[search_request] = {
            "vacancies_found": vacancies_found,
            "vacancies_processed": vacancies_processed,
            "average_salary": average_salary
        }
    return vacancy_stats
