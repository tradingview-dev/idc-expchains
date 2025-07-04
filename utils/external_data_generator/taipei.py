from deepdiff.serialization import json_dumps

from DataGenerator import DataGenerator
from lib.LoggableRequester import LoggableRequester
from utils import file_writer, get_headers


class TaipeiDataGenerator(DataGenerator):

    @staticmethod
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

    def generate(self) -> list[str]:
        requester = LoggableRequester(self._logger, retries=5, delay=5)

        # ---descriptions------
        descriptions = []

        # Collect descriptions for ETF (English)
        url = "https://info.tpex.org.tw/api/etfFilter?lang=en-us"
        try:
            resp = requester.request(LoggableRequester.Methods.GET, url, get_headers())
            tmp = resp.json().get('data', {})
            result = [{"symbol": item["stockNo"], "description": item["stockName"]} for item in tmp]
            descriptions = self.join_objects(descriptions, result, "description")
        except (OSError, KeyError) as e:
            self._logger.error(e)
            raise e

        # Collect domestic, foreign, and other descriptions in English
        req_list = [
            ("https://www.tpex.org.tw/www/en-us/ETN/list", {"type": "domestic", "response": "json"}),
            ("https://www.tpex.org.tw/www/en-us/ETN/list", {"type": "foreign", "response": "json"}),
        ]
        for request in req_list:
            try:
                resp = requester.request(LoggableRequester.Methods.POST, request[0], get_headers(), request[1])
                response_data = resp.json()
                if 'tables' in response_data and len(response_data['tables']) > 0:
                    result = [{'symbol': item[0], 'description': item[1]} for item in
                              response_data['tables'][0]['data']]
                    descriptions = self.join_objects(descriptions, result, "description")
            except (OSError, KeyError) as e:
                self._logger.error(e)
                raise e

        taipei_descriptions = "taipei_descriptions.json"
        try:
            file_writer(json_dumps(sorted(descriptions, key=lambda r: r["symbol"]), indent=4, ensure_ascii=False), taipei_descriptions)
        except OSError as e:
            self._logger.error(e)
            raise e

        # ---local-descriptions------
        local_descriptions = []

        # Collect local descriptions for ETF (Chinese)
        url = "https://info.tpex.org.tw/api/etfFilter?lang=zh-tw"
        try:
            resp = requester.request(LoggableRequester.Methods.GET, url, get_headers())
            tmp = resp.json().get('data', {})
            result = [{"symbol": item["stockNo"], "local-description": item["stockName"]} for item in tmp]
            local_descriptions = self.join_objects(local_descriptions, result, "local-description")
        except (OSError, KeyError) as e:
            self._logger.error(e)
            raise e

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
            try:
                resp = requester.request(LoggableRequester.Methods.POST, request[0], get_headers(), request[1])
                response_data = resp.json()
                if 'tables' in response_data and len(response_data['tables']) > 0:
                    result = [{'symbol': item[0], 'local-description': item[1]} for item in
                              response_data['tables'][0]['data']]
                    local_descriptions = self.join_objects(local_descriptions, result, "local-description")
            except (OSError, KeyError) as e:
                self._logger.error(e)
                raise e

        taipei_local_descriptions = "taipei_local_descriptions.json"
        try:
            file_writer(json_dumps(sorted(local_descriptions, key=lambda r: r["symbol"]), indent=4, ensure_ascii=False), taipei_local_descriptions)
        except OSError as e:
            self._logger.error(e)
            raise e

        return [taipei_descriptions, taipei_local_descriptions]


if __name__ == "__main__":
    try:
        TaipeiDataGenerator().generate()
        exit(0)
    except (OSError, KeyError):
        exit(1)
