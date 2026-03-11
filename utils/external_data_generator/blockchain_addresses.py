#!/usr/bin/env python3
# coding=utf-8

import json
import requests
from DataGenerator import DataGenerator
from utils import file_writer


class BlockchainAddressesGenerator(DataGenerator):
    def __init__(self, environment: str):
        super().__init__()
        self.environment = environment

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


    def generate(self) -> list[str]:
        currencies = self._load_currencies(self.get_currencies_url(self.environment))
        if not currencies:
            return []

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

if __name__ == "__main__":
    try:
        BlockchainAddressesGenerator(environment="staging").generate()
        exit(0)
    except OSError:
        exit(1)

