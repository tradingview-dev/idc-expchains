#!/usr/bin/env python3
# coding=utf-8

import openpyxl
import os
import urllib.request

DESTINATION = 'nasdaq_gids_symbols.xlsx'

MY_CSV = "nasdaq_gids_symbols.csv"

URL = 'https://indexes.nasdaqomx.com/Index/ExportDirectory'


def download_file(url: str, destination: str) -> None:
    """
    Downloads a file from the specified URL and saves it to the destination.

    :param url: URL where the file is downloaded from
    :param destination: The path where the downloaded file will be saved
    """
    try:
        urllib.request.urlretrieve(url, destination)
    except Exception as e:
        print(f"Error downloading file: {e}")
        raise


def get_indices_from_xlsx(destination: str) -> list:
    """
    Extracts and returns a sorted list of symbols from an xlsx file.

    :param destination: Path to the xlsx file
    :return: Sorted list of indices
    """
    gids_indices = []
    try:
        workbook = openpyxl.load_workbook(destination, read_only=True)
        sheet = workbook["Index Directory"]

        for row in sheet.iter_rows(values_only=True):
            if (row[7] == "" and row[6] == "SandP") or row[0] == "Symbol":
                continue
            gids_indices.append(row[0])

        workbook.close()
    except Exception as e:
        print(f"Error reading xlsx file: {e}")
        raise

    return sorted(gids_indices)


def write_to_csv(indices: list) -> None:
    """
    Writes a list of indices to a CSV file.

    :param indices: Sorted list of indices to save in the file
    """
    try:
        with open(MY_CSV, 'w', newline='', encoding='utf-8') as csv_file:
            csv_file.write("tv-symbol\n")

            for index in indices:
                csv_file.write(index + "\n")

    except Exception as e:
        print(f"Error writing to CSV file: {e}")
        raise


def nasdaq_gids_handler():

    download_file(URL, DESTINATION)

    write_to_csv(get_indices_from_xlsx(DESTINATION))

    os.remove(DESTINATION)
