#!/usr/bin/env python3
# coding=utf-8

import csv
import openpyxl
import os
import re
import urllib.request


WHITELIST = ["NYSE", "ARCA", "BATSZ", "AMEX"]

DESTINATION = 'symbolsNYSE.xlsx'

MY_CSV = "symbolsNYSE.csv"

URL = 'https://www.nyse.com/publicdocs/nyse/symbols/Symbol_Distribution.xlsx'


def download_file(url: str, destination: str) -> None:
    """
    :param url: url where the file is downloaded from
    :param destination: the name of the file in which the downloaded file is saved
    """
    urllib.request.urlretrieve(url, destination)


def xlsx_to_csv(destination: str) -> None:
    """
    :param destination: file name where one page of the file is saved in csv format
    """
    workbook = openpyxl.load_workbook(destination, read_only=True)
    sheet = workbook["ARCX"]

    with open(MY_CSV, 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)

        for row in sheet.iter_rows(values_only=True):
            csv_writer.writerow(row)


def get_mic_code(market: str) -> str:
    """
    :param market: market from the exchange
    :return: mic-code for symbolinfo
    """
    if market == "NYSE":
        return "XNYS"

    if market == "ARCA":
        return "ARCX"

    if market == "AMEX":
        return "XASE"

    if market == "BATSZ":
        return "BATS"


def get_description(description: str) -> str:
    """
    :param description: description of the symbol from the exchange
    :return: description for symbolinfo
    """
    if "�" in description:
        return description.replace("�", " ")

    if ";" in description:
        return f"{description.split(';')[0]} -{description.split(';')[1]}"

    return description


def get_tv_symbol(symbol: str) -> str:
    """
    :param symbol: symbol from the exchange
    :return: tv-symbol for symbolinfo
    """
    tv_symbol = re.match(
        r'(?P<pr1>.*)\s(?P<pr2>[PR])R(?P<pr3>.)*|'
        r'(?P<dotsym1>.*)\s(?P<dotsym2>.$)|'
        r'(?P<ws1>.*)\sWS(?P<ws2>.)*|'
        r'(?P<rt1>.*)\sRT', symbol
    )
    if tv_symbol and tv_symbol.group('pr1') is not None:
        return (tv_symbol.group('pr1') + '/' + tv_symbol.group('pr2')) + (
            tv_symbol.group('pr3') if tv_symbol.group('pr3') is not None else '')

    if tv_symbol and tv_symbol.group('dotsym1') is not None:
        return tv_symbol.group('dotsym1') + '.' + tv_symbol.group('dotsym2')

    if tv_symbol and tv_symbol.group('ws1') is not None:
        return (tv_symbol.group('ws1') + '/W') + (tv_symbol.group('ws2') if tv_symbol.group('ws2') is not None else '')

    if tv_symbol and tv_symbol.group('rt1') is not None:
        return tv_symbol.group('rt1') + '/R'

    return symbol


def get_symbolinfo_lists(my_csv: str) -> tuple:
    """
    :param my_csv: csv file name
    :return: 2 lists with symbols, descriptions and mic-codes for symbolinfo
    """
    nyse_symbol_list = []
    amex_symbol_list = []

    with open(f'{my_csv}', encoding='utf-8') as symbols:
        file = csv.reader(symbols, delimiter=",")

        for i in file:

            if i[5] in WHITELIST:

                description = get_description(i[0])
                tv_sym = get_tv_symbol(i[1])
                mic = get_mic_code(i[5])

                if i[5] == "NYSE":
                    nyse_symbol_list.append(f"{tv_sym};{description};{mic}")

                else:
                    amex_symbol_list.append(f"{tv_sym};{description};{mic}")

    return nyse_symbol_list, amex_symbol_list


def nyse_handler():

    download_file(URL, DESTINATION)
    xlsx_to_csv(DESTINATION)
    nyse_symbol_list, amex_symbol_list = get_symbolinfo_lists(MY_CSV)

    with open("nyse_data.csv", "w") as file:
        file.write("tv-symbol;description;mic-code\n")

        for i in nyse_symbol_list:
            file.write(f"{i}\n")

    with open("amex_data.csv", "w") as file:
        file.write("tv-symbol;description;mic-code\n")

        for i in amex_symbol_list:
            file.write(f"{i}\n")

    os.remove(DESTINATION)
    os.remove(MY_CSV)
