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

    csv_filename = "strike-price-report.csv"
    excel_data.to_csv(csv_filename, index=False)

    os.remove(xlsx_filename)

    print(f"CSV file has been saved as {csv_filename} ")