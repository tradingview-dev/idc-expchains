#!/usr/bin/env python3
# coding=utf-8

import csv
import argparse
import sys
import re

MONTH_TO_NUM = {
    "Jan": "01",
    "Feb": "02",
    "Mar": "03",
    "Apr": "04",
    "May": "05",
    "Jun": "06",
    "Jul": "07",
    "Aug": "08",
    "Sep": "09",
    "Oct": "10",
    "Nov": "11",
    "Dec": "12",
}


def build_sort_key(symbol_series_pos, date_pos, line):
    symbol_series = line[symbol_series_pos]
    date_str = line[date_pos]
    date_re_search = re.search(r"([0-9]{2})-([A-Za-z]{3})-([0-9]{2})", date_str)
    date_day = date_re_search.group(1)
    date_mon = date_re_search.group(2)
    date_year = date_re_search.group(3)
    date_mon_fmt = MONTH_TO_NUM.get(date_mon, date_mon)
    date_fmt = f"20{date_year}{date_mon_fmt}{date_day}"

    return date_fmt + ":" + symbol_series


def add_symbol_series_column(from_csv: str, to_csv: str):
    """
    :param from_csv: original csv file name
    :param to_csv: modified csv file name
    """

    header = None
    symbol_list = []

    symbol_pos = -1
    series_pos = -1
    date_pos = -1

    with open(f'{from_csv}', encoding='utf-8') as symbols:
        file = csv.reader(symbols, delimiter=",")
        line_no = 0
        for line in file:
            if line_no == 0:
                symbol_pos = line.index("SYMBOL")
                series_pos = line.index("SERIES")
                date_pos = line.index("DATE_OF_LISTING")
                header = ["SYMBOL_SERIES"] + line
            else:
                sym_ser = f'{line[symbol_pos]}.{line[series_pos]}'
                symbol_list.append([sym_ser] + line)
            line_no += 1

    sorted_list = sorted(symbol_list, key=lambda l: build_sort_key(0, date_pos+1, l), reverse=True)

    with open(f"{to_csv}", "w") as file:
        file.write(",".join(header) + "\n")
        for line in sorted_list:
            file.write(",".join(line) + "\n")



def nse_emerge_handler():
    add_symbol_series_column("nse_raw_listing.csv", "nse_sme_listing.csv")
    return 0
