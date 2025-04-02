import requests


class CmeProductsParser:

    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-endcoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.5",
        "connection": "keep-alive",
        "host": "www.cmegroup.com",
        "referer": "https://www.cmegroup.com/markets/products.html",
        "priority": "u=1, i",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:136.0) Gecko/20100101 Firefox/136.0",
    }

    base_url = "https://www.cmegroup.com/services/product-slate"

    def __init__(self, product_type):
        self.product_type = product_type

    def get_total_pages(self):

        first_page = requests.get(f"{self.base_url}?sortAsc=false&sortField=oi&pageNumber=1&pageSize=500&group=&subGroup=&venues=&exch=&cleared={self.product_type}&isProtected", headers=self.headers).json()

        total_pages = first_page['props']['pageTotal']

        return total_pages

    def parse_symbols(self):

        with open(f"{self.product_type}_products.csv", "w") as file:

            file.write("prodCode;name;Group;Sub Group\n")

            total_pages = self.get_total_pages()

            for i in range(1, total_pages+1):
                page = requests.get(f"{self.base_url}?sortAsc=false&sortField=oi&pageNumber={i}&pageSize=500&group=&subGroup=&venues=&exch=&cleared={self.product_type}&isProtected", headers=self.headers).json()

                products = page['products']

                for product in products:
                    root = product['prodCode']
                    description = product['name']
                    group = product['group']
                    subGroup = product['subGroup']

                    file.write(f"{root};{description};{group};{subGroup}\n")


def cme_handler(product):

    a = CmeProductsParser(product)

    a.parse_symbols()
