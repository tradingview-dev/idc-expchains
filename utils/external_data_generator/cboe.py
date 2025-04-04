import requests

def cboe_handler():
    
    csv = requests.get("https://www.cboe.com/us/equities/market_statistics/listed_symbols/csv/").text
    
    with open("cboe.csv", "w") as file:
        file.write("Name;underlying-symbol\n")
        for line in csv.split("\n"):
            symbol = line.split(',')[0]
            if symbol == "Name":
                continue
            file.write(f"{line.split(',')[0]};CBOE:{line.split(',')[0]}\n")
