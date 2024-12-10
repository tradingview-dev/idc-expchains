import json
import random
import time

import requests


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

url = "http://webapi.thecse.com/trading/listed/market/security_maintenance.json"


MAX_RETRIES = 5
DELAY = 5

retries = 0
while retries < MAX_RETRIES:
    try:
        response = requests.get(url, headers=get_headers())
        if response.status_code == 200:
            with open("canadian_descriptions.json", "w") as f:
                f.write(response.text)
            break
        elif response.status_code != 200:
            retries += 1
            print(
                f"{response.status_code} fail. Attempt {retries}/{MAX_RETRIES}. Repeat after {DELAY} seconds...")
            time.sleep(DELAY)
        else:
            response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Fail request: {e}")
        retries += 1
        time.sleep(DELAY)


