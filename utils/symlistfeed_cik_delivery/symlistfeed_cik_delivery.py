from argparse import ArgumentParser
from types import SimpleNamespace
from time import sleep
from os import path
from urllib.error import HTTPError
from urllib.request import urlopen
import urllib.request as network
from contextlib import closing
from json import loads, load, dumps
from gzip import decompress, BadGzipFile
from difflib import Differ

_RESPONSIBLE = 'IDC'


class SymlistFeedSettings:
    _ENVIRONMENT: dict = {
        'testing': {
            'to_s3':   'https://symlistfeed-storage-dev.nyc.xstaging.tv/files/{provider}/{filename}?ruleset={ruleset_filename}',
            'from_s3': 'https://symlistfeed-storage-dev.nyc.xstaging.tv/files/{provider}/{filename}'
        },
        'staging': {
            'to_s3':   'https://symlistfeed-storage-hub0.nyc.xstaging.tv/files/{provider}/{filename}?ruleset={ruleset_filename}',
            'from_s3': 'https://symlistfeed-storage-hub0.nyc.xstaging.tv/files/{provider}/{filename}'
        },
        'stable':  {
            'to_s3':   'https://symlistfeed-storage.xstaging.tv/files/{provider}/{filename}?ruleset={ruleset_filename}',
            'from_s3': 'https://symlistfeed-storage.xstaging.tv/files/{provider}/{filename}'
        },
        'master':  {
            'to_s3':   'https://symlistfeed-storage.xtools.tv/files/{provider}/{filename}?ruleset={ruleset_filename}',
            'from_s3': 'https://symlistfeed-storage.xtools.tv/files/{provider}/{filename}'
        },
    }

    def __init__(self, environment: str) -> None:
        self.urls: SimpleNamespace = SimpleNamespace(**self._ENVIRONMENT[environment])


class InteractionWithSymlistFeedPreprocessor:
    def __init__(self, provider: str, filename_path: str, ruleset_filename: str, environment: str,
                 is_not_gzip: bool) -> None:
        self._provider:                          str = provider
        self._filename_path:                     str = filename_path
        self._filename:                          str = self._filename_path.split('/')[-1].split('.')[0]
        self._file_extension:                    str = self._filename_path.split('/')[-1].split('.')[-1]
        self._ruleset_filename:                  str = ruleset_filename
        self._settings:          SymlistFeedSettings = SymlistFeedSettings(environment)
        self._is_not_gzip:                      bool = is_not_gzip

        self._remote_content: (None, dict) = None
        self._local_content:  (None, dict) = None

    @staticmethod
    def _do_request(link: str, headers: dict, method: str, data: (None, dict) = None, attempts: int = 3) -> dict:

        print('Do request for {}...'.format(link))

        request_settings = network.Request(link, data=data, headers=headers, method=method)
        while attempts:
            try:

                with closing(urlopen(request_settings)) as response:
                    try:
                        return loads(decompress(response.read()))
                    except BadGzipFile:
                        return loads(urlopen(request_settings).read())

            except HTTPError as err:
                print('Request error: {}, link - {}, do it again...'.format(err.status, link))
                print(err.read().decode())
                attempts -= 1
                sleep(2)

        if not attempts:
            print('Attempts were exhausted, return empty response...')
            return {}

    def read_from_remote_file(self) -> None:

        print('Get remote file...')

        link = self._settings.urls.from_s3.format(filename=self._filename, provider=self._provider)
        self._remote_content = self._do_request(link,
                                                {
                                                    'User-Agent':      _RESPONSIBLE,
                                                    'Content-Type':    'application/json',
                                                    'Accept-Encoding': 'gzip'
                                                },
                                                "GET")

    def read_from_local_file(self) -> None:

        print('Read local file...')

        filename_path = path.abspath(self._filename_path)

        try:
            with open(filename_path, 'r') as f:
                self._local_content = load(f)
        except FileNotFoundError as err:
            print('Error - {}, exit...'.format(err))
            exit(1)

    def compare_files(self) -> bool:

        print('Compare local & remote files...')

        local_content = dumps(self._local_content, sort_keys=True, indent=4).splitlines(keepends=False)
        remote_content = dumps(self._remote_content, sort_keys=True, indent=4).splitlines(keepends=False)

        diff_size = len(str(local_content)) / len(str(remote_content))

        return diff_size > 0.8

    def send_local_file(self) -> None:

        print('Send local file...')

        link = self._settings.urls.to_s3.format(provider=self._provider, filename=self._filename,
                                                ruleset_filename=self._ruleset_filename)

        response = self._do_request(link,
                                    {'User-Agent': _RESPONSIBLE},
                                    "POST",
                                    data=dumps(self._local_content, sort_keys=True, indent=4).encode('utf-8'))

        if response.get('status', '') != 'ok':
            print('NOTE', response)
            exit(1)

        else:
            print('SUCCESS', response)


def get_options() -> InteractionWithSymlistFeedPreprocessor:
    parser = ArgumentParser(description='Symlist-data-file delivery to symlistfeed-preprocessor.')
    parser.add_argument('--provider',         type=str, required=True,
                        help="Rule's directory. Provider name is the name of the responsible team.")
    parser.add_argument('--filename-path',    type=str, required=True,
                        help="Total .json file name path, within the repository; symlist format, prepared in advance.")
    parser.add_argument('--ruleset-filename', type=str, required=True,
                        help=".json file name with rules. The file itself located in provider.")
    parser.add_argument('--environment',      type=str, required=True,
                        help="Environment name: testing, staging, stable or master.")
    parser.add_argument('--is-not-gzip',      required=False, action='store_true',
                        help="Used for work with decompressed data.")
    args = parser.parse_args()

    return InteractionWithSymlistFeedPreprocessor(
        args.provider,
        args.filename_path,
        args.ruleset_filename,
        args.environment,
        args.is_not_gzip
    )


def main():

    task = get_options()
    task.read_from_remote_file()
    task.read_from_local_file()
    is_diff_ok = task.compare_files()
    if is_diff_ok:
        task.send_local_file()
    else:
        print('ERROR: new file is much smaller than previous, upload cancelled')
        exit(1)


if __name__ == '__main__':
    main()