from bs4 import BeautifulSoup
from typing import List

import openpyxl
import os
import urllib.request
import requests

BASE_URI = "https://www.aquis.eu"

def get_aquis_symbols()-> List[List[str]]:
    """
    request symbols
    :return slice with symbols
    """
    res = []

    companies = requests.get(f"{BASE_URI}/companies").content
    soup = BeautifulSoup(companies, "html.parser")
    symbols = soup.find_all("a", class_="chakra-link css-pz0aee")
    for symbol in symbols:
        res.append(get_symbol_params(symbol.text))
    return res

def get_symbol_params(symbol: str)-> List[str]:
    """
    :param symbol: symbol string
    :return: array with symbols params
    """

    symbol_page = requests.get(f"{BASE_URI}/companies/{symbol}").content

    soup = BeautifulSoup(symbol_page, "html.parser")
    isin = soup.find("p", class_="chakra-text css-4vttjp").text
    description = soup.find("h1", class_="chakra-heading css-135d5ex").text
    currency = soup.find("p", class_="chakra-text css-bjhtoj").text.split(" ")[2]
    return [description, symbol, isin, currency]


def get_secondary_listing_url_file()-> str:

    html = requests.get("https://www.aquis.eu/stock-exchange/statistics").content

    soup = BeautifulSoup(html, "html.parser")
    files = soup.find_all("a", class_="chakra-link css-fhzrj1")
    for file in files:
        if file.find("p").text.startswith("Secondary"):
            return file['href']

    return None

def download_file(url: str, destination: str) -> None:
    """
    :param url: url where the file is downloaded from
    :param destination: the name of the file in which the downloaded file is saved
    """
    urllib.request.urlretrieve(url, destination)


def xlsx_to_csv(csv_res: str, destination: str) -> None:
    """
    :param csv_res:
    :param destination: file name where one page of the file is saved in csv format
    """
    workbook = openpyxl.load_workbook(destination, read_only=True)

    with open(csv_res, 'w', newline='', encoding='utf-8') as csv_file:

        sheet = workbook.active

        for row in sheet.iter_rows(values_only=True):

            if row[0] is not None and row[1] is not None and row[2] is not None and row[3] is not None:
                csv_file.write(f"{row[0]};{row[1]};{row[2]};{row[3]}\n")

        for symbol in get_aquis_symbols():
            csv_file.write(f"{symbol[0]};{symbol[1]};{symbol[2]};{symbol[3]}\n")


def aquis_handler():

    secondary = get_secondary_listing_url_file()

    download_file(secondary, f"aquis.xlsx")

    xlsx_to_csv(f"aquis.csv", f"aquis.xlsx")

    os.remove(f"aquis.xlsx")
