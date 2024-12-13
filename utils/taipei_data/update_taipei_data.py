import json
import random
import time

import requests
from deepdiff.serialization import json_dumps


def get_headers() -> dict:
    """
    :return: headers with random user-agent
    """
    USER_AGENTS: list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 ",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 YaBrowser/20.12.1.178 Yowser/2.5 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0"
        ]

    random_number = random.randint(0, len(USER_AGENTS) - 1)
    headers = {
        "accept": "*/*",
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "priority": "u=1, i",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": USER_AGENTS[random_number],
        "x-requested-with": "XMLHttpRequest"
    }
    return headers

def collect_info(url, additional_data):
    max_retries = 5
    delay = 5

    retries = 0
    response_result = requests.Response()
    while retries < max_retries:
        try:
            if len(additional_data) > 0:
                response_result = requests.post(url, headers=get_headers(), data=additional_data)
            else:
                response_result = requests.post(url, headers=get_headers())
            if response_result.ok:
                return response_result
            elif response_result.status_code != 200:
                retries += 1
                print(
                    f"{response_result.status_code} fail. Attempt {retries}/{max_retries}. Repeat after {delay} seconds...")
                time.sleep(delay)
        except requests.exceptions.RequestException as e:
            print(f"Fail request: {e}")
            retries += 1
            time.sleep(delay)

    return response_result


def join_objects(left, right, description_type):
    left_map = {it['symbol']: it[description_type] for it in left}
    right_map = {it['symbol']: it[description_type] for it in right}

    result_map = left_map.copy()
    result_map.update(right_map)

    return [{'symbol': symbol, description_type: result_map[symbol]} for symbol in
              list(left_map.keys()) + [key for key in right_map.keys() if key not in left_map]]

# ---descriptions------
descriptions = []
response = collect_info("https://info.tpex.org.tw/api/etfFilter?lang=en-us", {})
if response != requests.Response():
    tmp = response.json().get('data', {})
    result = []
    for item in tmp:
        transformed_item = {
            "symbol": item["stockNo"],
            "description": item["stockName"]
        }
        result.append(transformed_item)
    descriptions = join_objects(descriptions, result, "description")


add_data = {
    'type': 'domestic',
    'id': '',
    'response': 'json'
}
response = collect_info("https://www.tpex.org.tw/www/en-us/ETN/list", add_data)
if response != requests.Response():
    response_data = response.json()
    result = [{'symbol': item[0], 'description': item[1]} for item in response_data['tables'][0]['data']]
    descriptions = join_objects(descriptions, result, "description")

add_data = {
    'type': 'foreign',
    'id': '',
    'response': 'json'
}
response = collect_info("https://www.tpex.org.tw/www/en-us/ETN/list", add_data)
if response != requests.Response():
    response_data = response.json()
    result = [{'symbol': item[0], 'description': item[1]} for item in response_data['tables'][0]['data']]
    descriptions = join_objects(descriptions, result, "description")

add_data = {
    'type': 'code',
    'code': '',
    'id': '',
    'response': 'json'
}
response = collect_info("https://www.tpex.org.tw/www/en-us/fund/recomSearch", add_data)
if response != requests.Response():
    response_data = response.json()
    result = [{'symbol': item[0], 'description': item[1]} for item in response_data['tables'][0]['data']]
    descriptions = join_objects(descriptions, result, "description")

with open('taipei_descriptions.json', "w", encoding="utf-8") as f:
    f.write(json_dumps(descriptions, indent=4, ensure_ascii=False))


# ---local-descriptions------
local_descriptions = []
response = collect_info("https://info.tpex.org.tw/api/etfFilter?lang=zh-tw", {})
if response != requests.Response():
    tmp = response.json().get('data', {})
    result = []
    for item in tmp:
        transformed_item = {
            "symbol": item["stockNo"],
            "local-description": item["stockName"]
        }
        result.append(transformed_item)
    local_descriptions = join_objects(local_descriptions, result, "local-description")

add_data = {
    'type': 'domestic',
    'id': '',
    'response': 'json'
}
response = collect_info("https://www.tpex.org.tw/www/zh-tw/ETN/list", add_data)
if response != requests.Response():
    response_data = response.json()
    result = [{'symbol': item[0], 'local-description': item[1]} for item in response_data['tables'][0]['data']]
    local_descriptions = join_objects(local_descriptions, result, "local-description")

add_data = {
    'type': 'foreign',
    'id': '',
    'response': 'json'
}
response = collect_info("https://www.tpex.org.tw/www/zh-tw/ETN/list", add_data)
if response != requests.Response():
    response_data = response.json()
    result = [{'symbol': item[0], 'local-description': item[1]} for item in response_data['tables'][0]['data']]
    local_descriptions = join_objects(local_descriptions, result, "local-description")

add_data = {
    'code': '',
    'cate': '02',
    'type': 'stkType',
    'stkType': '',
    'id': '',
    'response': 'json'
}
response = collect_info("https://www.tpex.org.tw/www/zh-tw/company/otcSearch", add_data)
if response != requests.Response():
    response_data = response.json()
    result = [{'symbol': item[0], 'local-description': item[1]} for item in response_data['tables'][0]['data']]
    local_descriptions = join_objects(local_descriptions, result, "local-description")


add_data = {
    'alphabet': '',
    'code': '',
    'cate': '',
    'type': 'stkType',
    'stkType': '',
    'id': '',
    'response': 'json'
}
response = collect_info("https://www.tpex.org.tw/www/zh-tw/company/emergingSearch", add_data)
if response != requests.Response():
    response_data = response.json()
    result = [{'symbol': item[0], 'local-description': item[1]} for item in response_data['tables'][0]['data']]
    local_descriptions = join_objects(local_descriptions, result, "local-description")

add_data = {
    'alphabet': '',
    'code': '',
    'cate': '',
    'type': 'stkType',
    'stkType': 'RR',
    'id': '',
    'response': 'json'
}
response = collect_info("https://www.tpex.org.tw/www/zh-tw/company/emergingSearch", add_data)
if response != requests.Response():
    response_data = response.json()
    result = [{'symbol': item[0], 'local-description': item[1]} for item in response_data['tables'][0]['data']]
    local_descriptions = join_objects(local_descriptions, result, "local-description")

add_data = {
    'code': '',
    'cate': '02',
    'type': 'stkType',
    'stkType': 'RR',
    'id': '',
    'response': 'json'
}
response = collect_info("https://www.tpex.org.tw/www/zh-tw/company/otcSearch", add_data)
if response != requests.Response():
    response_data = response.json()
    result = [{'symbol': item[0], 'local-description': item[1]} for item in response_data['tables'][0]['data']]
    local_descriptions = join_objects(local_descriptions, result, "local-description")

add_data = {
    'type': 'code',
    'code': '',
    'id': '',
    'response': 'json'
}
response = collect_info("https://www.tpex.org.tw/www/zh-tw/fund/recomSearch", add_data)
if response != requests.Response():
    response_data = response.json()
    result = [{'symbol': item[0], 'local-description': item[1]} for item in response_data['tables'][0]['data']]
    local_descriptions = join_objects(local_descriptions, result, "local-description")

with open('taipei_local_descriptions.json', "w", encoding="utf-8") as f:
    f.write(json_dumps(local_descriptions, indent=4, ensure_ascii=False))