import re

from Handler import Handler
from lib.LoggableRequester import LoggableRequester
from utils import file_writer, get_headers


class ShanghaiHandler(Handler):

    @staticmethod
    def process_content(content: str) -> str:
        """
        Processes the content fetched from the URL by performing multiple string transformations.
        :param content: Raw content as a string
        :return: Processed content as a string
        """
        content = content.rstrip()
        content = content.replace(';', ',').replace('\t', ';')
        content = re.sub(r';{2,}', ';', content)
        content = re.sub(r'\s+;', ';', content)
        content = re.sub(r';\s+', ';', content)
        content = content.replace(';-', ';')
        return content

    def handle(self, data_cluster = None):
        # Define the URL and headers
        url = 'http://query.sse.com.cn/listedcompanies/companylist/downloadCompanyInfoList.do'
        headers = {
            'Referer': 'http://english.sse.com.cn/listed/company/'
        }

        requester = LoggableRequester(self._logger, retries=5, delay=5)

        try:
            resp = requester.request(LoggableRequester.Methods.GET, url, (get_headers() | headers))
            content = resp.content.decode('gb2312', errors='ignore')
            processed_content = self.process_content(content)
            file_writer(processed_content, "sse_descriptions.csv")
            return 0
        except Exception as e:
            self._logger.error(e)
            return 1
