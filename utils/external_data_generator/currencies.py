#!/usr/bin/env python3
# coding=utf-8

import json
import requests
from DataGenerator import DataGenerator
from utils import file_writer


class CurrenciesGenerator(DataGenerator):
    FILE_BLOCKCHAIN_ADDRESSES = "blockchain-addresses"
    FILE_CURRENCY_DESCRIPTIONS = "currency-descriptions"

    def __init__(self, environment: str, file_type: str):
        super().__init__()
        self.environment = environment
        self.file_type = file_type

    @staticmethod
    def get_currencies_url(environment: str) -> str:
        if environment == "staging":
            return "https://tradingview-currencies-staging.xstaging.tv/currencies.json"
        else:
            return "https://tradingview-currencies.tradingview.com/currencies.json"

    @staticmethod
    def _load_currencies(url: str) -> dict:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to load URL: Status code {response.status_code}")
            return {}

        currencies = json.loads(response.text)
        return currencies

    def _generate_blockchain_addresses(self, currencies: list) -> list[str]:
        addresses = []
        for currency in currencies:
            if "cryptoasset-addresses" in currency:
                cryptoasset_addresses = currency["cryptoasset-addresses"]
                if isinstance(cryptoasset_addresses, dict):
                    for blockchain_id, blockchain_address in cryptoasset_addresses.items():
                        addresses.append({
                            "full-blockchain-address": f"{blockchain_id}({blockchain_address})",
                            "currency-id": currency["id"]})

        outfile = "blockchain-addresses.json"
        file_writer(json.dumps(sorted(addresses, key=lambda x: x["full-blockchain-address"])), outfile)
        return [outfile]

    def _generate_currency_descriptions(self, currencies: list) -> list[str]:
        descriptions = [
            {"currency-id": currency["id"], "description": currency["description"]}
            for currency in currencies
            if "description" in currency
        ]

        outfile = "currency-descriptions.json"
        file_writer(json.dumps(sorted(descriptions, key=lambda x: x["currency-id"])), outfile)
        return [outfile]

    def generate(self) -> list[str]:
        currencies = self._load_currencies(self.get_currencies_url(self.environment))
        if not currencies:
            return []

        if self.file_type == self.FILE_CURRENCY_DESCRIPTIONS:
            return self._generate_currency_descriptions(currencies)
        return self._generate_blockchain_addresses(currencies)

if __name__ == "__main__":
    import sys
    file_type = sys.argv[1] if len(sys.argv) > 1 else CurrenciesGenerator.FILE_BLOCKCHAIN_ADDRESSES
    try:
        CurrenciesGenerator(environment="staging", file_type=file_type).generate()
        exit(0)
    except OSError:
        exit(1)

