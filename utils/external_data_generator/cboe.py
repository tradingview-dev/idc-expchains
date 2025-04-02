import requests

def cboe_handler():
    
    csv = requests.get("https://www.cboe.com/us/equities/market_statistics/listed_symbols/csv/").text
    
    with open("cboe.csv", "w") as file:
        for line in csv.split("\n"):
            file.write(f"{line.split(',')[0]}\n")
