import requests
import pandas as pd
import os

def cftc_handler():
    url = "https://www.cftc.gov/strike-price-xls?col=ExchId%2CContractName&dir=ASC%2CASC"
    response = requests.get(url)

    xlsx_filename = "strike-price-report.xlsx"
    with open(xlsx_filename, "wb") as file:
        file.write(response.content)

    excel_data = pd.read_excel(xlsx_filename)

    # Define a dictionary to map Exchange IDs to exchange names
    exchange_mapping = {
        '01': 'CBOT',
        '02': 'CME',
        '06': 'ICEUS',
        '07': 'COMEX',
        '12': 'NYMEX',
        'E': 'CBOE',
        'SG': 'SGX',
        '41': 'ICEEU'
    }

    exchange_groups = excel_data.groupby('Exchange ID')

    for exchange_id, group in exchange_groups:
        if str(exchange_id) in exchange_mapping:
            exchange_name = exchange_mapping.get(str(exchange_id), str(exchange_id))

            output_filename = f"cftc_{exchange_name}.csv"
            group.to_csv(output_filename, index=False)
            print(f"CSV file for Exchange ID {exchange_id} ({exchange_name}) has been saved as {output_filename}")
        else:
            print(f"Exchange ID {exchange_id} is not in the mapping, skipping file creation.")


    os.remove(xlsx_filename)
