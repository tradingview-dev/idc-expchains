import json
import tarfile

from DataGenerator import DataGenerator
from io import BytesIO
from s3_utils import read_state
from utils import get_bucket_by_branch


class NASDAQOMXUnderlyingGenerator(DataGenerator):

    def __init__(self, branch):
        super().__init__()
        self._branch = branch
        self.inner_filename = "./snapshots.json"

    @staticmethod
    def get_bucket_by_branch(branch: str) -> str:
        buckets = {
            "staging": "tradingview-sourcedata-storage-staging",
            "stable": "tradingview-sourcedata-storage-stable",
            "master": "tradingview-sourcedata-storage"
        }
        return buckets[branch]

    def generate_underlying_csv(self) -> dict[str, str]:

        result = {}
        bucket = self.get_bucket_by_branch(self._branch)
        state = read_state(bucket, "ice/725.tar.gz", None)

        with tarfile.open(fileobj=BytesIO(state), mode="r:gz") as tar:
            member = tar.getmember(self.inner_filename)
            file_obj = tar.extractfile(member)
            if file_obj is None:
                raise FileNotFoundError(f"Файл {self.inner_filename} не найден в архиве")

            for line in file_obj:
                snap = json.loads(line.decode("utf-8"))
                ticker = snap.get("SYMBOL.TICKER")
                if ticker is not None:
                    underlying_mic = snap.get("MIC.CODE")
                    if underlying_mic is not None:
                        result[ticker] = underlying_mic
                    else:
                        continue
                else:
                    continue

        return result

    def generate(self) -> list[str]:

        result = "NASDAQOMXUnderlying.csv"

        with open(result, "w") as file:
            file.write("underlying-symbol;underlying-mic\n")
            for root, underlying in self.generate_underlying_csv().items():
                file.write(f"{root};{underlying}\n")

        return [result]


if __name__ == "__main__":
    try:
        NASDAQOMXUnderlyingGenerator("staging").generate()
        exit(0)
    except OSError:
        exit(1)
