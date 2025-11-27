import json
import shutil
import tarfile
import tempfile

from DataGenerator import DataGenerator
from lib.LoggableRequester import LoggableRequester
from pathlib import Path

class EURONEXTUnderlyingGenerator(DataGenerator):

    def __init__(self):
        super().__init__()

    @staticmethod
    def get_state(object_key: str)  -> tuple[str, str]:
        tmp_file = tempfile.NamedTemporaryFile(suffix="".join(Path(object_key).suffixes), delete=False)
        baseurl = "https://tradingview-sourcedata-storage.xstaging.tv"
        url = f"{baseurl}/{object_key}"
        try:
            resp = LoggableRequester().request(LoggableRequester.Methods.GET, url)
            with open(tmp_file.name, "wb") as f:
                f.write(resp.content)
        except OSError as e:
            raise e
        with tarfile.open(tmp_file.name, "r:gz") as tar:
            tar.extractall(f"{tmp_file.name}_output")
        return (tmp_file.name, f"{tmp_file.name}_output")
    
    def generate_underlying_csv(self) -> dict[str, str]:

        result = {}
        archive, unzip = self.get_state("ice/903.tar.gz")

        with open(f"{unzip}/snapshots.json", "r") as snapshots:
            for snapshot in snapshots:
                snap = json.loads(snapshot)
                ticker = snap.get("SYMBOL.TICKER")
                if ticker is not None:
                    root = ticker.split("\\")[0].split(":")[1]
                underlying_prefix = snap.get("ENUM.SRC.UNDERLYING.ID")
                underlying_symbol = snap.get("SYMBOL.UNDERLYING.TICKER")
                if underlying_prefix is not None and underlying_symbol is not None:
                    underlying = f"{underlying_prefix}:{underlying_symbol}"
                result[root] = underlying

        shutil.rmtree(archive, ignore_errors=True)
        shutil.rmtree(unzip, ignore_errors=True)

        return result
    
    def generate(self) -> str:

        result = "EuronextUnderlying.csv"

        with open(result, "w") as file:
            file.write("tv-root;underlying\n")
            for root, underlying in self.generate_underlying_csv().items():
                file.write(f"{root};{underlying}\n")

        return result


if __name__ == "__main__":
    try:
        EURONEXTUnderlyingGenerator().generate()
        exit(0)
    except OSError:
        exit(1)
