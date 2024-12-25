import re
from utils import request_with_retries, file_writer, get_headers

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


def fetch_and_process_data(url: str, headers: dict, output_path: str):
    """
    Fetches the data from the URL, processes it, and writes the output to a file.
    :param url: URL to fetch the data from
    :param headers: Headers to use in the request
    :param output_path: Path to save the processed output
    """
    response = request_with_retries(url, max_retries=5, additional_headers=headers, delay=5)

    if response.status_code == 200:
        content = response.content.decode('gb2312', errors='ignore')
        processed_content = process_content(content)
        file_writer(processed_content, output_path)
        print(f"Data successfully written to {output_path}")
    else:
        print(f"Failed to fetch data. HTTP status code: {response.status_code}")


def shanghai_handler():
    # Define the URL and headers
    url = 'http://query.sse.com.cn/listedcompanies/companylist/downloadCompanyInfoList.do'
    headers = {
        'Referer': 'http://english.sse.com.cn/listed/company/'
    }

    fetch_and_process_data(url, headers, 'sse_descriptions.csv')