"""
This module provides functions to load and process data from symbols.json (TV) and
company_tickers_exchange.json (SEC) to create symbol mapping.
The processed symbol mapping is then saved to both local and AWS S3 storage.
"""

import csv
import gzip
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set
import time
from argparse import ArgumentParser

import ijson
import requests

# Путь к существующему файлу мэппинга символов с cik для обновления (в случае если символ поменялся для cik) и добавления новых символов
EXISTING_SYMBOL_MAPPING_PATH = "cik_codes.json"

EQUIVALENT_PREFIXES = {"NASDAQ", "NYSE", "AMEX", "CBOE"}

def normalize_symbol(symbol_fullname: str) -> str:
    """Normalize a symbol by removing equivalent prefix."""
    try:
        prefix, ticker = symbol_fullname.split(":", 1)
    except ValueError:
        return symbol_fullname  # fallback, malformed symbol
    if prefix.upper() in EQUIVALENT_PREFIXES:
        return ticker.upper()
    return symbol_fullname.upper()

@dataclass
class TVSymbol:
    """Dataclass to represent a TV symbol."""

    symbol_fullname: str
    symbol_primaryname: str
    popularity: float

    @classmethod
    def from_dict(cls, row: dict) -> "TVSymbol":
        """Creates a TVSymbol instance from a dictionary.

        Args:
            row (dict): A dictionary containing the TV symbol data.

        Returns:
            TVSymbol: An instance of TVSymbol.
        """
        return cls(
            symbol_fullname=row["symbol-fullname"],
            symbol_primaryname=row["symbol-primaryname"],
            popularity=0 if len(row["popularity"]) == 0 else float(row["popularity"]),
        )


@dataclass
class SECSymbol:
    """Dataclass to represent an SEC symbol."""

    cik: int
    exchange: str
    ticker: str
    symbol_primaryname: str = field(default=None)
    is_tv_symbol: int = field(default=0)
    popularity: float = field(default=0.0)
    symbol: str = field(default=None)

    @classmethod
    def from_dict(cls, row: dict) -> "SECSymbol":
        """Creates an SECSymbol instance from a dictionary.

        Args:
            row (dict): A dictionary containing the SEC symbol data.

        Returns:
            SECSymbol: An instance of SECSymbol.
        """
        return cls(cik=int(row["cik"]), exchange=row["exchange"], ticker=row["ticker"])

    @property
    def sec_symbol(self) -> str:
        raw = f"{self.exchange}:{self.ticker}".upper()
        return normalize_symbol(raw)


@dataclass
class SymbolCik:
    """Dataclass to represent a symbol mapping."""

    cik: int
    symbol: str

    @classmethod
    def from_sec_symbol(cls, symbol: SECSymbol) -> "SymbolCik":
        """Creates a SymbolMap instance from an SECSymbol instance.

        Args:
            symbol (SECSymbol): An instance of SECSymbol.

        Returns:
            SymbolCik: An instance of SymbolMap.
        """
        return cls(cik=symbol.cik, symbol=symbol.symbol)

    @classmethod
    def from_dict(cls, row: dict) -> "SymbolCik":
        """Creates a SymbolMap instance from a dictionary.

        Args:
            row (dict): A dictionary containing the symbol mapping data.

        Returns:
            SymbolMap: An instance of SymbolMap.
        """
        return cls(cik=int(row["cik"]), symbol=row["symbol"])


@dataclass
class SymbolMapping:
    """Dataclass to manage a list of symbol mappings."""

    symbols: List[SymbolCik] = field(default_factory=list)

    @classmethod
    def read_from_csv(cls, filepath) -> "SymbolMapping":
        """Reads symbol mappings from a CSV file.

        Args:
            filepath (str): The path to the CSV file.

        Returns:
            SymbolMapping: An instance of SymbolMapping containing the read data.
        """
        symbols = []
        if Path(filepath).is_file():
            with open(filepath, mode="r") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    symbols.append(SymbolCik.from_dict(row))
        else:
            print(f"Old symbol_mapping not found!")
        return cls(symbols=symbols)

    def write_to_csv(self, filepath) -> None:
        """Writes the symbol mappings to a CSV file.

        Args:
            filepath (str): The path to the CSV file.
        """
        fieldnames = ["cik", "symbol"]
        with open(filepath, mode="w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for symbol in self.symbols:
                writer.writerow(symbol.__dict__)

    def write_to_symlistfeed(self, filepath) -> None:
        """Writes the symbol mappings to a symlistfeed-format file.

        Args:
            filepath (str): The path to the symlistfeed file.
        """

        json_data = {
            "fields": ["cik-code"],
            "symbols": []
        }

        for symbol in self.symbols:
            json_data["symbols"].append({
                     "f": [symbol.cik],
                     "s": symbol.symbol
            })

        with open(filepath, "w", newline="") as json_file:
            json.dump(json_data, json_file)

    def update_with_new_mapping(self, new_symbols: List[SymbolCik]) -> None:
        """Updates the symbol mappings with new data.

        Args:
            new_symbols (List[SymbolMap]): A list of new symbol mappings.
        """
        existing_symbols_dict = {symbol.cik: symbol for symbol in self.symbols}

        for new_symbol in new_symbols:
            existing_symbols_dict[new_symbol.cik] = new_symbol

        self.symbols = list(existing_symbols_dict.values())


def load_tv_symbols(
    url: str = "",
    symbol_types: Optional[Set[str]] = None,
    filtered_tv_symbols_path = "/tmp/filtered_tv_symbols.csv",
    batch_size: int = 1000,
) -> None:
    """Fetches TV symbols from a JSON URL, filters them, and saves to a CSV file.

    Args:
        url (str): The URL of the symbols.json file containing symbols.
        symbol_types (Optional[Set[str]]): A set of symbol types to filter. Defaults to None.
        filtered_tv_symbols_path (str): The path where the filtered CSV will be saved. Defaults to "/tmp/filtered_tv_symbols.csv".
        batch_size (int): The number of records to write at a time. Defaults to 1000.
    """
    cols_to_use = ["symbol-fullname", "symbol-primaryname", "popularity", "symbol-type"]

    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with gzip.GzipFile(fileobj=r.raw) as decompressed_file:
            items = ijson.items(decompressed_file, "item")
            with open(filtered_tv_symbols_path, "w", newline="") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=cols_to_use)
                writer.writeheader()
                buffer = []
                for item in items:
                    filtered_item = {k: item[k] for k in cols_to_use if k in item}
                    if symbol_types is None or filtered_item.get("symbol-type") in symbol_types:
                        buffer.append(filtered_item)
                    if len(buffer) >= batch_size:
                        writer.writerows(buffer)
                        buffer.clear()
                if buffer:
                    writer.writerows(buffer)


def load_sec_symbols(
    url: str = "https://www.sec.gov/files/company_tickers_exchange.json", sec_symbols_path = "/tmp/sec_symbols.csv"
) -> None:
    """Fetches SEC symbols and saves them to a CSV file.

    Args:
        url (str): The URL of the company_tickers_exchange.json file containing symbols.
        sec_symbols_path (str): The path where the SEC symbols CSV will be saved.
    """
    headers = {"User-Agent": "FL dev@fl.com", "Accept-Encoding": "gzip, deflate"}
    response = requests.get(url, headers=headers)
    data = response.json()
    fields = data["fields"]
    data = data["data"]

    with open(sec_symbols_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(fields)
        for row in data:
            writer.writerow(row)


def read_tv_symbols(filepath) -> Dict[str, TVSymbol]:
    """Reads TV symbols from a CSV file.

    Args:
        filepath (str): The path to the CSV file.

    Returns:
        Dict[str, TVSymbol]: A dictionary of TV symbols indexed by symbol fullname.
    """
    tv_symbols = {}
    with open(filepath, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            tv_symbol = TVSymbol.from_dict(row)
            key = normalize_symbol(tv_symbol.symbol_fullname)
            tv_symbols[key] = tv_symbol
    return tv_symbols


def read_sec_symbols(filepath) -> List[SECSymbol]:
    """Reads SEC symbols from a CSV file.

    Args:
        filepath (str): The path to the CSV file.

    Returns:
        List[SECSymbol]: A list of SECSymbol instances.
    """
    sec_symbols = []
    with open(filepath, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            sec_symbols.append(SECSymbol.from_dict(row))
    return sec_symbols


def join_symbols(tv_symbols: Dict[str, TVSymbol], sec_symbols: List[SECSymbol]) -> List[SECSymbol]:
    """Joins TV symbols with SEC symbols.

    Args:
        tv_symbols (Dict[str, TVSymbol]): A dictionary of TV symbols.
        sec_symbols (List[SECSymbol]): A list of SEC symbols.

    Returns:
        List[SECSymbol]: A list of joined SEC symbols.
    """
    for sec_symbol in sec_symbols:
        if sec_symbol.sec_symbol in tv_symbols:
            tv_symbol = tv_symbols[sec_symbol.sec_symbol]
            sec_symbol.symbol_primaryname = tv_symbol.symbol_primaryname
            sec_symbol.is_tv_symbol = 1
            sec_symbol.popularity = tv_symbol.popularity
            sec_symbol.symbol = tv_symbol.symbol_fullname
    return [sec_symbol for sec_symbol in sec_symbols if sec_symbol.is_tv_symbol]


def filter_sort_deduplicate_symbols(symbols: List[SECSymbol]) -> List[SymbolCik]:
    """Filters, sorts, and deduplicates SEC symbols.

    Args:
        symbols (List[SECSymbol]): A list of SEC symbols.

    Returns:
        List[SymbolMap]: A list of unique symbol mappings sorted by CIK and popularity.
    """
    if any(x.popularity < 0 for x in symbols):
        raise ValueError("Negative popularity of symbol")

    symbols.sort(key=lambda x: (x.cik, -x.popularity))
    unique_cik = set()
    final_data = []
    for symbol in symbols:
        if symbol.cik not in unique_cik:
            unique_cik.add(symbol.cik)
            final_data.append(SymbolCik.from_sec_symbol(symbol))
    return final_data


def get_new_symbol_mapping(
    filtered_tv_symbols_path = "/tmp/filtered_tv_symbols.csv", sec_symbols_path = "/tmp/sec_symbols.csv"
) -> List[SymbolCik]:
    """Fetches new symbol mappings.

    Args:
        filtered_tv_symbols_path (str): The path to the filtered TV symbols CSV file.
        sec_symbols_path (str): The path to the SEC symbols CSV file.

    Returns:
        List[SymbolMap]: A list of new symbol mappings.
    """
    tv_symbols = read_tv_symbols(filtered_tv_symbols_path)
    sec_symbols = read_sec_symbols(sec_symbols_path)
    joined_symbols = join_symbols(tv_symbols, sec_symbols)
    final_data = filter_sort_deduplicate_symbols(joined_symbols)
    return final_data


def update_existing_symbol_mapping():
    """Adds new symbols and updates current symbols in symbol mapping with new data.

    Args:
        symbol_mapping_from_s3_path (str): Path to the existing symbol mapping CSV file loaded from S3.
        updated_mapping_path (str): Path where the updated symbol mapping CSV will be saved.
    """

    # Read existing symbol mapping
    existing_symbol_mapping = SymbolMapping.read_from_csv(EXISTING_SYMBOL_MAPPING_PATH)

    # Get new symbol mapping
    new_symbol_mapping = get_new_symbol_mapping()

    # Update existing symbol mapping with new data
    existing_symbol_mapping.update_with_new_mapping(new_symbol_mapping)

    # Write the updated symbol mapping to symlistfeed format
    existing_symbol_mapping.write_to_symlistfeed(EXISTING_SYMBOL_MAPPING_PATH)

    # Write the updated symbol mapping to CSV
    # existing_symbol_mapping.write_to_csv(EXISTING_SYMBOL_MAPPING_PATH)


def main():
    """Main function to update and save symbol mappings."""

    parser = ArgumentParser(description='Symlist-data-file delivery to symlistfeed-preprocessor.')
    parser.add_argument('--env',         type=str, required=True,
                        help="Environment staging/production. Used for request symbols")
    args = parser.parse_args()
    # Load TV-symbols and save local
    print("Start loading TV-symbols")
    start_time = time.time()
    filtered_tv_symbols_path = "/tmp/filtered_tv_symbols.csv"
    symbol_types = {"stock", "fund", "dr", "structured", "warrant"}
    symbols_url = "https://tradingview-symbology.tradingview.com/symbols.json"
    if args.env == "staging":
        symbols_url = "http://tradingview-symbology-staging.xstaging.tv/symbols.json"
    load_tv_symbols(url=symbols_url, filtered_tv_symbols_path=filtered_tv_symbols_path, symbol_types=symbol_types)
    print(f"Time spent loading TV-symbols: {time.time() - start_time:.2f} seconds")

    # Load SEC-symbols and save local
    print("Start loading SEC-symbols")
    start_time = time.time()
    sec_symbols_path = "/tmp/sec_symbols.csv"
    load_sec_symbols(sec_symbols_path=sec_symbols_path)
    print(f"Time spent loading SEC-symbols: {time.time() - start_time:.2f} seconds")

    # Update local symbol mapping
    print("Update symbol mapping")
    start_time = time.time()
    update_existing_symbol_mapping()
    print(f"Time spent updating symbol mapping: {time.time() - start_time:.2f} seconds")


if __name__ == "__main__":
    main()