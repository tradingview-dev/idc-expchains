#!/usr/bin/env python3
# coding=utf-8
import argparse
import inspect
import os
import re
import sys
from typing import Optional

ILLEGAL_SYMBOL_MESSAGE = 'Illegal symbol'


def print_result(output_file: str, result: list) -> None:
    """
    Prints results to a file or std out.
    :param output_file: a file to write results, if not specified the program will write to std out
    :param result: the results to write
    """
    result = sorted(result, key=lambda it: it[3] + it[4])
    if output_file == 'stdout':
        for item in result:
            print(','.join(map(str, item)))
    else:
        with open(output_file, 'w') as f:
            for item in result:
                f.write('{0}\n'.format(','.join(map(str, item))))


def format_to_tv_expchains(root: str, exp: str, exg: Optional[str], exp_date: str) -> tuple:
    """
    Formats source expchains components to tv expchains components.
    :param root: source root component
    :param exp: source exp component
    :param exg: source exg (exchange) component
    :param exp_date: source exp_date component
    :return: a tuple of tv expchains components
    :raise ValueError: if failed to parse passed expiration date
    """
    match = re.match(r'(?P<y1>\d{4})(?P<m1>[A-Z])|(?P<m2>[A-Z])(?P<e>\d?)(?P<y2>\d{4})', exp)  # try to parse expiration date
    if not match or match.group('e'):
        if exg:
            raise ValueError('{0}: {1} "{2} {3} {4}"'.format(inspect.currentframe().f_code.co_name, ILLEGAL_SYMBOL_MESSAGE, root, exp, exp_date))
        else:
            raise ValueError('{0}: {1} "{2} {3}-{4} {5}"'.format(inspect.currentframe().f_code.co_name, ILLEGAL_SYMBOL_MESSAGE, root, exp, exg, exp_date))
    year = match.group('y1') or match.group('y2')
    month = match.group('m1') or match.group('m2')
    dbc_symbol = '{0} {1}-{2}'.format(root, exp, exg) if exg else '{0} {1}'.format(root, exp)
    tv_symbol = root + month + year
    rts_symbol = 'F:{0}\\{1}{2}'.format(root, month, year[-2:])
    tv_root = root
    exp_date = re.sub(r'/', '', exp_date)
    exp_date = re.sub(r' ', '0', exp_date)
    exp_date = exp_date[-4:] + exp_date[:2] + exp_date[2:4]
    return tv_symbol, dbc_symbol, rts_symbol, tv_root, exp_date


def parse_line(line: str) -> tuple:
    """
    Parses a passed line to components.
    :param line: line to parse
    :return: components of the passed line
    :raise ValueError: if failed to split the passed line into required components
    """
    try:
        # the exp_exg variable must have an expiration component and should have an exchange component
        root, exp_exg, exp_date = re.split(r'(?<![\t/])\s', line.rstrip())
    except ValueError:
        raise ValueError('{0}: {1} "{2}"'.format(inspect.currentframe().f_code.co_name, ILLEGAL_SYMBOL_MESSAGE, line.rstrip()))
    exp_exg = exp_exg.split('-')
    exp, exg = (exp_exg[0], exp_exg[1]) if len(exp_exg) == 2 else (exp_exg[0], None)
    return root, exp, exg, exp_date


def parse(lines: list) -> list:
    """
    Tries to parse each line into components,
    and tries to format the components to tv expchains format.
    :param lines: a list of lines to parse
    :return: a list of expchains components
    :raise ValueError: if failed to parse a line or failed to format the components to tv expchains format
    """
    result = []
    for line in lines:
        try:
            root, exp, exg, exp_date = parse_line(line)
            result.append(format_to_tv_expchains(root, exp, exg, exp_date))
        except ValueError as e:
            sys.stderr.write('{0} has been skipped\n'.format(e))
    return result


def search(input_file: str, regex: str) -> list:
    """
    Reads a file line by line and tests each line for passed template.
    :param input_file: a file to parse
    :param regex: a template to test
    :return: a list of matched lines
    """
    result, pattern = [], re.compile(regex, re.MULTILINE)
    with open(input_file, 'r') as input_file:
        for line in input_file:
            if pattern.search(line):
                if '=' in line:
                    continue  # drop the entries with session ID
                result.append(line)
    return result


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--regex', dest='regex', type=str, metavar='<regex>',
                        help='regular expression to filtering by interested symbols', required=True)
    parser.add_argument('-i', '--tab-file-path', dest='input_file', type=str, metavar='<tab-file-path>',
                        help='input file path (default: ExpChains.tab)', default='ExpChains.tab')
    parser.add_argument('-o', '--out', dest='output_file', type=str, metavar='<out>',
                        help='output file path (use stdout to write in stdout, default: stdout)', default='stdout')
    return parser.parse_args()


def main(args):
    if not os.path.isfile(args.input_file):
        print('File {0} not found. You should to specify a path to downloaded *.tab file or '
              'place it nearly this script.'.format(args.input_file))
        return 1

    result = parse(search(args.input_file, args.regex))
    print_result(args.output_file, result)

    return 0


if __name__ == '__main__':
    sys.exit(main(parse_args()))
