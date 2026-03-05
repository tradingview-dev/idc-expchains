from DataGenerator import DataGenerator
from s3_utils import upload_state


class CFIUploader(DataGenerator):

    def __init__(self, branch):
        super().__init__()
        self._branch = branch

    def generate(self) -> list[str]:

        upload_cfi(self._branch)

        return []

def upload_cfi(branch: str):
    upload_state("cfi_dict/cfi-dict-en.json", get_bucket(branch), "cfi/cfi-dict-en.json")


def get_bucket(branch: str) -> str:
    buckets = {
        "staging": "tradingview-pub-staging",
        "master": "tradingview-pub"
    }
    return buckets[branch]

if __name__ == "__main__":
    try:
        CFIUploader("staging").generate()
        exit(0)
    except OSError:
        exit(1)
