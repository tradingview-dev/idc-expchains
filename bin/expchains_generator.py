#!/usr/bin/env python
# coding=utf-8
import argparse
import os
import re
import sys


def print_result(output_file, result):
    result = sorted(result, key=lambda it: it[0])
    if output_file == 'stdout':
        for item in result:
            print(','.join(map(str, item)))
    else:
        with open(output_file, 'w') as f:
            for item in result:
                f.write('{0}\n'.format(','.join(map(str, item))))


def format_to_tv_expchains(root, exp, exg, exp_date):
    year = re.search(r'\d{4}', exp).group(0)
    if exg is not None:
        dbc_symbol = '{0} {1}-{2}'.format(root, exp, exg)
    else:
        dbc_symbol = '{0} {1}'.format(root, exp)
    tv_symbol = root + exp
    rts_symbol = 'F:{0}\\{1}'.format(root, year[-2:])
    tv_root = root
    exp_date = exp_date.translate(None, '/')
    exp_date = exp_date[-4:] + exp_date[:2] + exp_date[2:4]
    return dbc_symbol, rts_symbol, tv_root, tv_symbol, exp_date


def parse_line(line):
    root, exp_exg, exp_date = re.split(r'\s(?=[A-Z])|\t', line.rstrip())
    exp_exg = exp_exg.split('-')
    exp, exg = (exp_exg[0], exp_exg[1]) if len(exp_exg) == 2 else (exp_exg[0], None)
    exp = exp.split('=')[0]
    return root, exp, exg, exp_date


def search_and_parse(input_file, regex):
    result, pattern = [], re.compile(regex, re.MULTILINE)
    with open(input_file, 'r') as input_file:
        for line in input_file:
            if pattern.search(line) is not None:
                root, exp, exg, exp_date = parse_line(line)
                dbc_symbol, rts_symbol, tv_root, tv_symbol, exp_date = format_to_tv_expchains(root, exp, exg, exp_date)
                result.append([tv_symbol, dbc_symbol, rts_symbol, tv_root, exp_date])

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

    result = search_and_parse(args.input_file, args.regex)
    print_result(args.output_file, result)

    return 0


if __name__ == '__main__':
    sys.exit(main(parse_args()))
