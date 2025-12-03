import json
import tarfile

from DataGenerator import DataGenerator
from s3_utils import read_state
from utils import get_bucket_by_branch


class EURONEXTUnderlyingGenerator(DataGenerator):

    def __init__(self, branch):
        super().__init__()
        self._branch = branch
        self.inner_filename = "snapshots.json"
    
    def generate_underlying_csv(self) -> dict[str, str]:

        result = {}
        bucket = get_bucket_by_branch(self._branch)
        state = read_state(bucket, "ice/903.tar.gz", None)

        with tarfile.open(fileobj=io.BytesIO(state), mode="r:gz") as tar:
            member = tar.getmember(self.inner_filename)
            file_obj = tar.extractfile(member)
            if file_obj is None:
                raise FileNotFoundError(f"Файл {self.inner_filename} не найден в архиве")
            
            for line in file_obj:
                snap = json.loads(line.decode("utf-8"))
                ticker = snap.get("SYMBOL.TICKER")
                if ticker is not None:
                    root = ticker.split("\\")[0].split(":")[1]
                    if root[-1].isdigit():
                        root = root[:-1]
                else:
                    continue
                underlying_prefix = snap.get("ENUM.SRC.UNDERLYING.ID")
                underlying_symbol = snap.get("SYMBOL.UNDERLYING.TICKER")
                if underlying_prefix is not None and underlying_symbol is not None:
                    underlying = f"{underlying_prefix}:{underlying_symbol}"
                else:
                    continue
                result[root] = underlying

        return result
    
    def generate(self) -> list[str]:

        result = "EuronextUnderlying.csv"

        with open(result, "w") as file:
            file.write("tv-root;underlying\n")
            for root, underlying in self.generate_underlying_csv().items():
                file.write(f"{root};{underlying}\n")

        return [result]


if __name__ == "__main__":
    try:
        EURONEXTUnderlyingGenerator().generate()
        exit(0)
    except OSError:
        exit(1)
