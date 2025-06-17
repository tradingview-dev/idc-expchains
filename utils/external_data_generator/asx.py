from DataGenerator import DataGenerator
from lib.LoggableRequester import LoggableRequester
from utils import get_headers, file_writer


class ASXDataGenerator(DataGenerator):

    def generate(self) -> list[str]:

        url = "https://asx.api.markitdigital.com/asx-research/1.0/companies/directory/file"
        out = "asx_descriptions.csv"

        requester = LoggableRequester(self._logger, retries=5, delay=5)
        try:
            resp = requester.request(LoggableRequester.Methods.GET, url, get_headers())
            file_writer(resp.text, out)
        except IOError as e:
            self._logger.error(e)
            raise e

        return [out]


if __name__ == "__main__":
    try:
        ASXDataGenerator().generate()
        exit(0)
    except OSError:
        exit(1)
