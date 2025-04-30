from typing import Dict
import requests

headers = {
    "accept": "application/json, text/plain, */*",
    "accept-endcoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.5",
    "connection": "keep-alive",
    "host": "data.krx.co.kr",
    "referer": "http://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201060202",
    "priority": "u=1, i",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:136.0) Gecko/20100101 Firefox/136.0",
}

def get_korean_descriptions()-> Dict[str, str]:
    """
    request korean locale description
    :return: dict with korean descriptions
    """
    res = {}
    other_roots = requests.get("http://data.krx.co.kr/comm/bldAttendant/executeForResourceBundle.cmd?baseName=krx.mdc.i18n.component&key=B107.bld&locale=ko", headers=headers).json()["result"]["output"]
    for description in other_roots:
        res[description["value"]] = description["name"]
    data = {
        'locale': 'ko_KR',
        'prodId': 'KRDRVFUEQU',
        'subProdId': '',
        'csvxls_isNo': 'false',
        'bld': '/dbms/comm/component/drv_clss11'
    }
    equity_roots = requests.post("http://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd", data=data, headers=headers).json()["output"]
    for description in equity_roots:
        res[description["value"]] = description["name"]
    return res


def get_en_descriptions()-> Dict[str, str]:
    """
    request en locale description
    :return: dict with en descriptions
    """
    res = {}
    other_roots = requests.get("http://data.krx.co.kr/comm/bldAttendant/executeForResourceBundle.cmd?baseName=krx.mdc.i18n.component&key=B107.bld&locale=en", headers=headers).json()["result"]["output"]
    for description in other_roots:
        res[description["value"]] = description["name"]
    data = {
        'locale': 'en',
        'prodId': 'KRDRVFUEQU',
        'subProdId': '',
        'csvxls_isNo': 'false',
        'bld': '/dbms/comm/component/drv_clss11'
    }
    equity_roots = requests.post("http://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd", data=data, headers=headers).json()["output"]
    for description in equity_roots:
        res[description["value"]] = description["name"]
    return res


def merge_descriptions(en, ko):
    """
    merge descriptions
    :param en: dict with en descriptions
    :param ko: dict with korean descriptions
    :return: dict with merged en-korean descriptions
    """
    res = {}
    for k, v in en.items():
        res[v] = ko[k]
    return res


def to_csv(data):
    """
    writing result to csv
    :param data: dict with merged en-korean descriptions
    :return: None
    """
    with open("krx_local_descriptions.csv", "w") as file:
        file.write("root-description;local-description\n")
        for description, local_description in data.items():
            file.write(f"{description};{local_description}\n")


def krx_handler():

    merge = merge_descriptions(get_en_descriptions(), get_korean_descriptions())

    to_csv(merge)
