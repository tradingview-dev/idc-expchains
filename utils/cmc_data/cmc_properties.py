#!/usr/bin/env python3
import argparse
import csv
import json
import sys


class CMCProperties:
    def __init__(self, file, currencies, out_file):
        self.file = file
        self.currencies = currencies
        self.out_file = out_file

    @staticmethod
    def map_currency_id(currency: str) -> str:
        if currency.upper() == "GRT":
            return "XTVCGRAPH"
        return f"XTVC{currency.upper()}"

    @staticmethod
    def read_currencies(currencies_path: str) -> dict:
        with open(currencies_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        result = {}
        for record in data:
            result[record["id"]] = record
        return result

    def run(self) -> None:
        with open(self.file, "r", encoding="utf-8") as f:
            data = json.load(f)["data"]

        defi_coins = [r for r in data if "defi" in r.get("tags", [])]

        currencies = self.read_currencies(self.currencies)

        defi_coins_ids = []
        for record in defi_coins:
            cid = self.map_currency_id(record["symbol"])
            if cid not in currencies:
                print(f"WARN: Unknown currency-id {cid}")
            defi_coins_ids.append(cid)

        defi_coins_ids.sort()

        with open(self.out_file, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["currency-id"])
            for cid in defi_coins_ids:
                writer.writerow([cid])


def main():
    parser = argparse.ArgumentParser(description="Process CMC properties.")
    parser.add_argument("-f", "--file", required=True, help="Input JSON file")
    parser.add_argument("-c", "--currencies", required=True, help="Currencies JSON file")
    parser.add_argument("-o", "--output", required=True, help="Output CSV file")

    args = parser.parse_args()

    requester = CMCProperties(file=args.file, currencies=args.currencies, out_file=args.output)
    requester.run()


if __name__ == "__main__":
    sys.exit(main())
