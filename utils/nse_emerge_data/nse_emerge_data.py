#!/usr/bin/env python3
# coding=utf-8

import csv
import argparse
import sys

def add_symbol_series_column(from_csv: str, to_csv: str):
    """
    :param from_csv: original csv file name
    :param to_csv: modified csv file name
    """

    symbol_list = []

    symbol_pos = -1
    series_pos = -1

    with open(f'{from_csv}', encoding='utf-8') as symbols:
        file = csv.reader(symbols, delimiter=",")
        line_no = 0
        for line in file:
            if line_no == 0:
                symbol_pos = line.index("SYMBOL")
                series_pos = line.index("SERIES")
                symbol_list.append(["SYMBOL_SERIES"] + line)
            else:
                sym_ser = f'{line[symbol_pos]}.{line[series_pos]}'
                symbol_list.append([sym_ser] + line)
            line_no += 1

    with open(f"{to_csv}", "w") as file:
        for line in symbol_list:
            file.write(",".join(line)+"\n")

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--source', dest='source', type=str, metavar='<src>',
                        help='source csv path', required=True)
    parser.add_argument('-t', '--target', dest='target', type=str, metavar='<tgt>',
                        help='target csv path', required=True)
    return parser.parse_args()

def main(args):
    add_symbol_series_column(args.source, args.target)
    return 0

if __name__ == '__main__':
    sys.exit(main(parse_args()))
