import re

from DataGenerator import DataGenerator
from lib.LoggableRequester import LoggableRequester
from utils import file_writer, get_headers


class ShanghaiDataGenerator(DataGenerator):

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

    def generate(self) -> list[str]:
        # Define the URL and HEADERS
        url = 'http://query.sse.com.cn/listedcompanies/companylist/downloadCompanyInfoList.do'
        headers = {
            'Referer': 'http://english.sse.com.cn/listed/company/'
        }

        sse_descriptions = "sse_descriptions.csv"

        requester = LoggableRequester(self._logger, retries=5, delay=5)
        try:
            resp = requester.request(LoggableRequester.Methods.GET, url, (get_headers() | headers))
            content = resp.content.decode('gb2312', errors='ignore')
            processed_content = self.process_content(content)
            file_writer(processed_content, sse_descriptions)
            return [sse_descriptions]
        except (UnicodeDecodeError, OSError) as e:
            self._logger.error(e)
            raise e


if __name__ == "__main__":
    try:
        ShanghaiDataGenerator().generate()
        exit(0)
    except OSError:
        exit(1)
