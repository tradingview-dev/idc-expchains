import pandas as pd

symbols = pd.read_json("https://s3.amazonaws.com/tradingview-symbology-staging/symbols.json")


symbols = symbols.query('`symbol-type`== "commodity" or `symbol-type`=="futures"')

symbols = symbols[["symbol", "group", "product", "description"]]
symbols = symbols[symbols['product'].isnull() | (symbols['product'] == "")]
symbols = symbols[["symbol", "group", "description"]]

if not symbols.empty:
    symbols.to_csv("empty_products", index=False)