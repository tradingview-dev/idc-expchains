import difflib
import os
import random
import shutil
import subprocess

from git import Repo

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 ",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 YaBrowser/25.6.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0",
]


def get_useragent() -> str:
    random_number = random.randint(0, len(USER_AGENTS) - 1)
    return USER_AGENTS[random_number]

def get_headers() -> dict:
    """
    Returns HEADERS with a random user-agent
    """
    headers = {
        "accept": "*/*",
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "priority": "u=1, i",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": get_useragent(),
        "x-requested-with": "XMLHttpRequest"
    }
    return headers


def file_writer(output: str, path: str):
    """
    Writes output to a path file
    """
    with open(path, "w", encoding="utf-8") as f:
        f.write(output)


def compare_and_overwrite_files(file_names, new_dir, prev_dir, check_diff):
    """
    Compares files with the same names in two directories and overwrites the files in prev_dif if they are different,
    and the new file's size does not twice less the size of the old file.

    :param file_names: List of filenames to compare.
    :param new_dir: Path to the directory where the new files are.
    :param prev_dir: Path to the directory where the existing files are.
    :param check_diff: Verify size changes.
    :return: Array of changed files names
    """
    res = []
    for file_name in file_names:
        new_file_path = os.path.join(new_dir, file_name)
        prev_file_path = os.path.join(prev_dir, file_name)
        if os.path.exists(new_file_path) and os.path.exists(prev_file_path):
            new_size = os.path.getsize(new_file_path)
            prev_size = os.path.getsize(prev_file_path)
            print(f"New file {new_file_path} has size {new_size}")
            print(f"Prev file {prev_file_path} has size {prev_size}")
            show_diff(str(prev_file_path), str(new_file_path))

            if files_are_different(new_file_path, prev_file_path):
                if check_diff and new_size * 2 < prev_size:
                    print(f"Skipping {file_name}: New file size less twice the size of the old file.")
                else:
                    print(f"File {file_name} have diff")
                    shutil.copy(str(new_file_path), str(prev_file_path))
                    res.append(prev_file_path)
        else:
            if os.path.exists(new_file_path):
                print(f"Skipping {file_name}: File not found in both directories. {prev_file_path} Not found")
            if os.path.exists(prev_file_path):
                print(f"Skipping {file_name}: File not found in both directories. {new_file_path} Not found")
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


def git_commit(file_names: list[str], branch, check_diff=True):
    if branch == "":
        raise ValueError("Branch is not specified")

    expchains_repo = "git@git.xtools.tv:idc/idc-expchains.git"
    expchains_dir = "./idc-expchains"
    dictionary_dir = os.path.join(expchains_dir, 'dictionaries')
    new_files_dir = os.path.join("/var/tmp", "external_data_generator")

    if not os.path.exists(expchains_dir):
        print("Cloning a git repo... ")
        try:
            repo = Repo.clone_from(expchains_repo, expchains_dir, branch=branch, depth=1, single_branch=True)
        except Exception as e:
            print("Fail to clone git repo")
            raise e
        print("Successful clone")
    else:
        repo = Repo(expchains_dir)
        print(f"Updating branch {branch} from repo {expchains_repo}... ")
        try:
            origin = repo.remotes.origin
            origin.fetch()
            repo.heads[branch].checkout()
            origin.pull()
        except Exception as e:
            print("Fail to update repo")
            raise e
        print("Successful updated repo")

    index = repo.index
    changed_files = compare_and_overwrite_files(file_names, new_files_dir, dictionary_dir, check_diff)
    environment = os.environ['ENVIRONMENT']
    if changed_files and environment != "stable":
        index.add(['/'.join(p.split('/')[2:]) for p in changed_files])
        print(f"Updating expchains in {branch}... ")
        index.commit(f"Autocommit {', '.join([os.path.basename(p) for p in changed_files])} data")
        repo.remotes.origin.push()
    else:
        print(f"No changes in {branch}")


def remove_repo():
    EXPCHAINS_DIR = "./idc-expchains"
    if os.path.exists(EXPCHAINS_DIR):
        shutil.rmtree(EXPCHAINS_DIR)


def load_from_repo(file_names: list[str], branch):
    if branch == "":
        return
    EXPCHAINS_REPO = "git@git.xtools.tv:idc/idc-expchains.git"
    EXPCHAINS_DIR = "./idc-expchains"
    DICTIONARY_DIR = os.path.join(EXPCHAINS_DIR, 'dictionaries')
    NEW_FILES_DIR = "/var/tmp"
    NEW_FILES_DIR = os.path.join(NEW_FILES_DIR, "external_data_generator")

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

    for f_name in file_names:
        print(f"Copy {f_name} from repo")
        repo_file = os.path.join(DICTIONARY_DIR, f_name)
        target_file = os.path.join(NEW_FILES_DIR, f_name)
        shutil.copy(repo_file, target_file)


def execute_to_file(cmd_line: list, out_file: str):
    with open(out_file, "w", encoding="utf-8") as f:
        cmd_result = subprocess.run(cmd_line, stdout=f)
        if cmd_result.returncode != 0:
            raise RuntimeError(f"External command {cmd_line} finished with non zero code: " + str(cmd_result.returncode))
        else:
            print(f"External command {cmd_line} finished successfully")
