import pandas as pd
import requests
import argparse

def post_to_slack(product_list, attachment_header, hook):
    msg_attachments = []
    empty_products_list = product_list.apply(lambda row: ';'.join(row.values.astype(str)), axis=1).tolist()
    empty_products_list.insert(0, "symbol;group;description")
    error_list = [f"- {p}" for p in empty_products_list]
    # if len(error_list) > 25:
        # error_list = ["..."] + error_list[-24:]
    attachment_body = "\n".join(error_list)
    msg_attachments.append({
        "blocks": [
            {"type": "section", "text": {"type": "mrkdwn", "text": attachment_header}},
            {"type": "section", "text": {"type": "mrkdwn", "text": attachment_body}}
        ]
    })
    msg_text = f"one or several symbols not have products"
    msg_body = [{"type": "section", "text": {"type": "mrkdwn", "text": msg_text}}]
    msg = {
        "blocks": msg_body,
        "attachments": msg_attachments,
        "link_names": "1"
    }
    response = requests.post(hook, json=msg)

parser = argparse.ArgumentParser()
parser.add_argument('--idc_hook', type=str,
                    help='IDC slack hook')
parser.add_argument('--hub_hook', type=str,
                    help='hub slack hook')
parser.add_argument('--env', type=str,
                    help='environment staging/prod')
args = parser.parse_args()


symbols = {}
if args.env == 'staging':
    symbols = pd.read_json("https://s3.amazonaws.com/tradingview-symbology-staging/symbols.json")
else:
    symbols = pd.read_json("https://s3.amazonaws.com/tradingview-symbology/symbols.json")


symbols = symbols.query('`symbol-type`== "commodity" or `symbol-type`=="futures"')

symbols = symbols[["symbol", "group", "product", "description", "provider-id"]]
symbols = symbols[symbols['product'].isnull() | (symbols['product'] == "")]
empty_products = symbols[["symbol", "group", "description"]]


if not empty_products.empty:
    empty_products.to_csv("empty_products", index=False)

idc_symbols = symbols[symbols["provider-id"].isin(["ice", "tvc", "six", "moex", "alor"])]
not_idc_symbols = symbols[~symbols["provider-id"].isin(["ice", "tvc", "six", "moex", "alor"])]

empty_products_idc = idc_symbols[["symbol", "group", "description"]]
empty_products_not_idc = not_idc_symbols[["symbol", "group", "description"]]

if not empty_products_idc.empty:
    post_to_slack(empty_products_idc, "@idc-dutyman\nEMPTY PRODUCTS LIST\n", args.idc_hook)

if not empty_products_not_idc.empty:
    post_to_slack(empty_products_not_idc, "@feed-qa @versus-data\nEMPTY PRODUCTS LIST\n", args.hub_hook)
