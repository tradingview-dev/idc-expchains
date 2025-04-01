from bs4 import BeautifulSoup

import openpyxl
import os
import urllib.request
import requests

def get_url():

    res = dict()

    html = requests.get("https://www.aquis.eu/stock-exchange/statistics").content

    soup = BeautifulSoup(html, "html.parser")
    href = soup.find_all("a", class_="chakra-link css-fhzrj1")

    primary = href[0]
    secondary = href[1]

    res['primary'] = primary['href']
    res['secondary'] =  secondary['href']

    return res


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

    with open(csv_res, 'a', newline='', encoding='utf-8') as csv_file:

        if destination.split(".")[0] == "primary":

            sheet = workbook["Trading Data"]

            for row in sheet.iter_rows(values_only=True):

                if row[0] is not None and row[1] is not None and row[3] is not None and row[4] is not None:
                    csv_file.write(f"{row[0]};{row[1]};{row[3]};{row[4]}\n")

        else:

            sheet = workbook.active

            for row in sheet.iter_rows(values_only=True):

                if row[0] is not None and row[1] is not None and row[2] is not None and row[3] is not None:
                    csv_file.write(f"{row[0]};{row[1]};{row[2]};{row[3]}\n")


def aquis_handler():

    listings = get_url()

    for listing in listings:

        download_file(listings[listing], f"{listing}.xlsx")

        xlsx_to_csv(f"aquis.csv", f"{listing}.xlsx")

        os.remove(f"{listing}.xlsx")
