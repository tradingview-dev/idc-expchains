import pandas as pd

symbols = pd.read_json("https://s3.amazonaws.com/tradingview-symbology-staging/symbols.json")


symbols = symbols.query('`symbol-type`== "commodity" or `symbol-type`=="futures"')

symbols = symbols[["symbol", "group", "product", "description", "provider-id"]]
symbols = symbols[symbols['product'].isnull() | (symbols['product'] == "")]
empty_products = symbols[["symbol", "group", "description"]]


if not empty_products.empty:
    empty_products.to_csv("empty_products", index=False)

idc_symbols = symbols[symbols["provider-id"].isin(["ice", "tvc", "six", "moex"])]
not_idc_symbols = symbols[~symbols["provider-id"].isin(["ice", "tvc", "six", "moex"])]

empty_products_idc = idc_symbols[["symbol", "group", "description"]]
empty_products_not_idc = not_idc_symbols[["symbol", "group", "description"]]

if not empty_products_idc.empty:
    empty_products_idc.to_csv("empty_products_idc", index=False)

if not empty_products_not_idc.empty:
    empty_products_not_idc.to_csv("empty_products_not_idc", index=False)
