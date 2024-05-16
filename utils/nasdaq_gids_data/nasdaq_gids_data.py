#!/usr/bin/env python3
# coding=utf-8

import openpyxl
import os
import urllib.request

DESTINATION = 'nasdaq_gids_symbols.xlsx'

MY_CSV = "nasdaq_gids_symbols.csv"

URL = 'https://indexes.nasdaqomx.com/Home/ExportGidsDirectory'


def download_file(url: str, destination: str) -> None:
    """
    :param url: url where the file is downloaded from
    :param destination: the name of the file in which the downloaded file is saved
    """
    urllib.request.urlretrieve(url, destination)


def get_indices_from_xlsx(destination: str) -> list:
    """
    :param destination: file name where page of the indices list
    """
    gids_indices = []
    workbook = openpyxl.load_workbook(destination, read_only=True)
    sheet = workbook["Index Directory"]

    for row in sheet.iter_rows(values_only=True):

        if row[2] == "E" or row[0] == "Symbol":
            continue

        gids_indices.append(row[0])

    return sorted(gids_indices)


def write_to_csv(indices: list) -> None:
    """
    :param indices: sorted indices list for saved in file
    """
    with open(MY_CSV, 'w', newline='', encoding='utf-8') as csv_file:
        csv_file.write("tv-symbol\n")

        for index in indices:
            csv_file.write(index + "\n")


if __name__ == "__main__":

    download_file(URL, DESTINATION)

    write_to_csv(get_indices_from_xlsx(DESTINATION))

    os.remove(DESTINATION)
