import os
import random
import shutil
import difflib
import time
import requests
from deepdiff.serialization import json_dumps
from git import Repo

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 ",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 YaBrowser/20.12.1.178 Yowser/2.5 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0"
]

def get_headers() -> dict:
    """
    Returns headers with a random user-agent
    """
    random_number = random.randint(0, len(USER_AGENTS) - 1)
    headers = {
        "accept": "*/*",
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "priority": "u=1, i",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": USER_AGENTS[random_number],
        "x-requested-with": "XMLHttpRequest"
    }
    return headers

def request_with_retries(url: str, post_data: dict = None, additional_headers: dict = {}, max_retries: int = 5, delay: int = 5) -> requests.Response:
    """
    Makes a request with retry logic.
    :param additional_headers: additional headers
    :param url: URL for the request
    :param post_data: Data for a POST request (optional)
    :param max_retries: Maximum number of retry attempts
    :param delay: Delay between retries in seconds
    :return: Response object from the request
    """
    retries = 0
    while retries < max_retries:
        try:
            # If post_data is provided, make a POST request
            if post_data:
                response = requests.post(url, headers=(get_headers() | additional_headers), data=post_data)
            else:
                response = requests.get(url, headers=(get_headers() | additional_headers))

            if response.status_code == 200:
                return response
            else:
                retries += 1
                print(f"{response.status_code} fail. Attempt {retries}/{max_retries}. Repeat after {delay} seconds...")
                time.sleep(delay)
        except requests.exceptions.RequestException as e:
            print(f"Fail request: {e}")
            retries += 1
            time.sleep(delay)
    return requests.Response()

def file_writer(output: str, path: str):
    """
    Writes output to path file
    """
    with open(path, "w", encoding="utf-8") as f:
        f.write(output)

def default_request_handler(url: str, path: str, post_data: dict = None):
    response = request_with_retries(url, post_data=post_data)
    if response != requests.Response():
        file_writer(response.text, path)

def json_request_handler(url: str, path: str, post_data: dict = None):
    response = request_with_retries(url, post_data=post_data)
    if response != requests.Response():
        file_writer(json_dumps(response.json(), indent=4, ensure_ascii=False), path)


def compare_and_overwrite_files(file_names: list[str], dir1, dir2: str) -> list[str]:
    """
    Compares files with the same names in two directories and overwrites the files in dir1 if they are different,
    and the new file's size does not exceed twice the size of the old file.

    :param file_names: List of filenames to compare.
    :param dir1: Path to the first directory (where the original files are).
    :param dir2: Path to the second directory (where the new files are).
    :return: array of changed files names
    """
    res = []
    for filename in file_names:
        file1_path = os.path.join(dir1, filename)
        file2_path = os.path.join(dir2, filename)

        if os.path.exists(file1_path) and os.path.exists(file2_path):
            size1 = os.path.getsize(file1_path)
            size2 = os.path.getsize(file2_path)
            print("-----------DEBUG-------------")
            print(size1)
            print(size2)
            print(file1_path)
            print(file2_path)
            show_diff(file1_path, file2_path)

            if files_are_different(file1_path, file2_path):
                with open(file1_path, 'rb') as f1, open(file2_path, 'rb') as f2:
                    if size1 * 2 > size2:
                        print(f"File {filename} have diff")
                        show_diff(file1_path, file2_path)
                        shutil.copy(str(file1_path), str(file2_path))
                        os.remove(file1_path)
                        res.append(filename)
                    else:
                        print(f"Skipping {filename}: New file size less twice the size of the old file.")
        else:
            if os.path.exists(file1_path):
                print(f"Skipping {filename}: File not found in both directories. {file1_path} Not found")
            if os.path.exists(file2_path):
                print(f"Skipping {filename}: File not found in both directories. {file2_path} Not found")
    return res

def show_diff(file1_path: str, file2_path: str):
    with open(file1_path, 'r', encoding='utf-8') as f1, open(file2_path, 'r', encoding='utf-8') as f2:
        file1_lines = f1.readlines()
        file2_lines = f2.readlines()

    diff = difflib.unified_diff(file1_lines, file2_lines, fromfile=file1_path, tofile=file2_path)

    for line in diff:
        print(line, end="")

def files_are_different(file1_path, file2_path):
    # Open both files in binary mode and compare chunk by chunk
    with open(file1_path, 'rb') as f1, open(file2_path, 'rb') as f2:
        while True:
            chunk1 = f1.read(4096)  # Read in chunks of 4 KB
            chunk2 = f2.read(4096)
            if chunk1 != chunk2:
                return True
            if not chunk1:  # End of file reached
                return False

def delivery(file_names: list[str], branch):
    if branch == "":
        return
    EXPCHAINS_REPO = "git@git.xtools.tv:idc/idc-expchains.git"
    EXPCHAINS_DIR = "./idc-expchains"
    DICTIONARY_DIR = EXPCHAINS_DIR.join('dictionaries')
    NEW_FILES_DIR = "/var/tmp"
    NEW_FILES_DIR = NEW_FILES_DIR.join("external_data_generator")

    if not os.path.exists(EXPCHAINS_DIR):
        try:
            repo = Repo.clone_from(EXPCHAINS_REPO, EXPCHAINS_DIR, branch=branch, depth=1, single_branch=True)
        except Exception as e:
            print("Fail to clone git repo")
            raise e
        print("Successful clone")
    else:
        repo = Repo(EXPCHAINS_DIR)
        print(f"Updating branch {branch} from repo {EXPCHAINS_REPO}... ", False)
        try:
            origin = repo.remotes.origin
            origin.fetch()
            repo.heads[branch].checkout()
            origin.pull()
        except Exception as e:
            print("Fail to update repo")
            raise e
        print("Successful update repo")

    index = repo.index
    changed_files = compare_and_overwrite_files(file_names, NEW_FILES_DIR, DICTIONARY_DIR)
    print(f"!!!DEBUG!!!!!! {changed_files}")
    if changed_files != []:
        index.add(changed_files)
        print(f"Updating expchains in {branch}... ")
        index.commit(f"Autocommit {', '.join(changed_files)} data")
        repo.remotes.origin.push()
    else:
        print(f"No changes in {branch}")
