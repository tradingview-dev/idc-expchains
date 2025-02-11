import requests
from deepdiff.serialization import json_dumps

from utils import request_with_retries, file_writer


def collect_info(url, additional_data=None):
    """
    Function to send requests with retries using utils.request_with_retries.
    :param url: URL to send the request to.
    :param additional_data: Optional dictionary for POST data.
    :return: Response object.
    """
    response = request_with_retries(url, post_data=additional_data)
    return response


def join_objects(left, right, description_type):
    """
    Merges two lists of objects based on their 'symbol' key.
    :param left: Left list of dictionaries.
    :param right: Right list of dictionaries.
    :param description_type: The key name for the description.
    :return: Combined list of dictionaries.
    """
    left_map = {it['symbol']: it[description_type] for it in left}
    right_map = {it['symbol']: it[description_type] for it in right}

    result_map = left_map.copy()
    result_map.update(right_map)

    return [{'symbol': symbol, description_type: result_map[symbol]} for symbol in
            list(left_map.keys()) + [key for key in right_map.keys() if key not in left_map]]


def taipei_handler():
    # ---descriptions------
    descriptions = []

    # Collect descriptions for ETF (English)
    request = ("https://info.tpex.org.tw/api/etfFilter?lang=en-us", {})
    print(f"Requesting {request}")
    response = collect_info(request[0], request[1])
    if response != requests.Response():
        tmp = response.json().get('data', {})
        result = [{"symbol": item["stockNo"], "description": item["stockName"]} for item in tmp]
        descriptions = join_objects(descriptions, result, "description")

    # Collect domestic, foreign, and other descriptions in English
    req_list = [
        ("https://www.tpex.org.tw/www/en-us/ETN/list", {"type": "domestic", "response": "json"}),
        ("https://www.tpex.org.tw/www/en-us/ETN/list", {"type": "foreign", "response": "json"}),
    ]
    for request in req_list:
        print(f"Requesting {request}")
        response = collect_info(request[0], request[1])
        if response != requests.Response():
            response_data = response.json()
            if 'tables' in response_data and len(response_data['tables']) > 0:
                result = [{'symbol': item[0], 'description': item[1]} for item in response_data['tables'][0]['data']]
                descriptions = join_objects(descriptions, result, "description")

    file_writer(json_dumps(sorted(descriptions, key=lambda r: r["symbol"]), indent=4, ensure_ascii=False), 'taipei_descriptions.json')

    # ---local-descriptions------
    local_descriptions = []

    # Collect local descriptions for ETF (Chinese)
    request = ("https://info.tpex.org.tw/api/etfFilter?lang=zh-tw", {})
    print(f"Requesting {request}")
    response = collect_info("https://info.tpex.org.tw/api/etfFilter?lang=zh-tw", {})
    if response != requests.Response():
        tmp = response.json().get('data', {})
        result = [{"symbol": item["stockNo"], "local-description": item["stockName"]} for item in tmp]
        local_descriptions = join_objects(local_descriptions, result, "local-description")

    # Collect local descriptions (domestic, foreign, etc.) in Chinese
    req_list = [
        ("https://www.tpex.org.tw/www/zh-tw/company/otcSearch", {"cate": "02", "type": "stkType", "stkType": "+", "response": "json"}),
        ("https://www.tpex.org.tw/www/zh-tw/company/otcSearch", {"cate": "02", "type": "stkType", "stkType": "RR", "response": "json"}),
        ("https://www.tpex.org.tw/www/zh-tw/ETN/list", {"type": "domestic", "response": "json"}),
        ("https://www.tpex.org.tw/www/zh-tw/ETN/list", {"type": "foreign", "response": "json"}),
        ("https://www.tpex.org.tw/www/zh-tw/company/emergingSearch", {"type": "domestic", "response": "json"}),
        ("https://www.tpex.org.tw/www/zh-tw/company/emergingSearch", {"type": "foreign", "response": "json"}),
    ]
    for request in req_list:
        print(f"Requesting {request}")
        response = collect_info(request[0], request[1])
        if response != requests.Response():
            response_data = response.json()
            if 'tables' in response_data and len(response_data['tables']) > 0:
                result = [{'symbol': item[0], 'local-description': item[1]} for item in response_data['tables'][0]['data']]
                local_descriptions = join_objects(local_descriptions, result, "local-description")

    file_writer(json_dumps(sorted(local_descriptions, key=lambda r: r["symbol"]), indent=4, ensure_ascii=False), 'taipei_local_descriptions.json')