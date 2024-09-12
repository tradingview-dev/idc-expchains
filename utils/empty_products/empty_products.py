import json

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
    msg_header = "@idc-dutyman\nEMPTY PRODUCTS LIST\n"
    msg_body = empty_products_idc.to_csv(index=False)
    output_json = {"blocks": [{"type": "section", "text": {"type": "mrkdwn", "text": msg_header}},
                              {"type": "section", "text": {"type": "mrkdwn", "text": msg_body}}]}
    with open('empty_products_idc', 'w', encoding='utf-8') as f:
        json.dump(output_json, f, ensure_ascii=False, indent=4)
    #empty_products_idc.to_csv("empty_products_idc", index=False)

if not empty_products_not_idc.empty:
    msg_header = "@feed-qa @versus-data\nEMPTY PRODUCTS LIST\n"
    msg_body = empty_products_not_idc.to_csv(index=False)
    output_json = {"blocks": [{"type": "section", "text": {"type": "mrkdwn", "text": msg_header}},
                              {"type": "section", "text": {"type": "mrkdwn", "text": msg_body}}]}
    with open('empty_products_not_idc', 'w', encoding='utf-8') as f:
        json.dump(output_json, f, ensure_ascii=False, indent=4)
    #empty_products_not_idc.to_csv("empty_products_not_idc", index=False)
