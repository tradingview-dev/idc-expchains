import requests
from deepdiff.serialization import json_dumps

from utils import file_writer, request_with_retries


def fetch_and_save_data(url: str, post_data: dict, output_file: str):
    """
    Fetches data from the Saudi Exchange API and saves it to a file.
    :param url: URL to send the request to
    :param post_data: Data for the POST request
    :param output_file: File path to save the result
    """
    response = request_with_retries(url, post_data=post_data)
    if response != requests.Response():
        try:
            json_data = response.json()
            file_writer(json_dumps(json_data, indent=4, ensure_ascii=False), output_file)
            print(f"Data successfully written to {output_file}")
        except ValueError as e:
            print(f"Error parsing JSON response: {e}")

def saudi_handler():
    url = 'https://www.saudiexchange.sa/wps/portal/saudiexchange/trading/participants-directory/issuer-directory/!ut/p/z1/lc_LCsIwEAXQb-kHSG6jiXGZLhIL9hHTas1GspKAVhHx-63uWt-zGzh3mEscaYhr_TXs_CUcW7_v9o3jWyY56Fyg0LaSMMpWST5TMVJG1n0gMs1hcmkKOmXQq5i4v_KwJetAmY0XWEKD_5bHm5H4nnd9AlOLO1EJE6DAZAheVBxceO7wAB-etP5MToe6bhDSkYyiG8La9T0!/p0/IZ7_5A602H80OOMQC0604RU6VD10F2=CZ6_5A602H80OGSTA0QFSTBN9F10I5=NJgetCompanyListByMarknetAndSectors=/'
    post_data = {
        'sector': 'All',
        'symbol': '',
        'letter': ''
    }
    fetch_and_save_data(url, {**post_data, 'marketType': 'M'}, 'saudi_main_market.json')
    fetch_and_save_data(url, {**post_data, 'marketType': 'S'}, 'saudi_nomu_parallel_market.json')