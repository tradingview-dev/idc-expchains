# IDC Expchains (Expired Chains)

[![pipeline status](https://git.xtools.tv/idc/idc-expchains/badges/master/pipeline.svg)](https://git.xtools.tv/idc/idc-expchains/-/commits/master)

Centralized storage of expired futures to build continuous core symbol-info and related scripts.
See [Knowledge Base: ExpChains](https://kb.xtools.tv/spaces/XWIKI/pages/29299981/ExpChains) for more information.

**Responsible team**: IDC Team (#team-idc)

## Overview
- [Requirements](#requirements)
- [Environment prepare](#environment-prepare)
  - [Ubuntu](#ubuntu)
  - [Windows](#windows)
  - [macOS](#macos)
- [Install an environment manager](#install-an-environment-manager)
- [Prepare the project](#prepare-the-project)
- [Run](#run)
  - [Scripts](#scripts)

## Requirements

| Tool   | Supported Versions                                 |
|--------|----------------------------------------------------|
| OS     | Ubuntu 22.04 and above / Windows 11 + WSL2 / macOS |
| Git    | 1.6.x and above                                    |
| Python | 3.10 and above                                     |
| Ruby   | 3.2 and above                                      |
| Bash   | 5.2 and above                                      |

## Environment prepare
First, you should install the `pipx` package. The `pipx` is a tool that allows you to 
install Python programs in isolated environments without clogging up site-packages.

> This step can be skipped.

### Ubuntu
Run step by step in your terminal:
```
sudo apt update
sudo apt install pipx
pipx ensurepath
```
After that, re-open your terminal OR just run:
```
source ~/.bashrc  # or ~/.zshrc, if you use Zsh
pipx --version
```

### Windows
Open a PowerShell as Administrator:
```
python -m pip install --upgrade pipx
python -m pipx ensurepath
```
After that, re-open a PowerShell and run:
```
pipx --version
```

### macOS
Run step by step in your terminal:
```
brew install pipx
pipx ensurepath
```
After that, re-open a PowerShell and run:
```
pipx --version
```

## Install an environment manager
You can use any environment manager, but we recommend using the `pipenv`.
In your terminal run:
```
pipx install pipenv
```
This will install the latest stable version of `pipenv` in a separate isolated environment, 
and it will be available in the terminal as pipenv.
To check run:
```
pipenv --version
```

In case of skipped [Environment prepare](#environment-prepare) step use:
```
pip install pipenv
```

## Prepare the project
Now you need to create a virtual environment and install required dependencies. 
In your terminal run step by step:
```
cd /path/to/idc-expchains
pipenv install
```

## Run
First, activate a virtual environment, in your terminal run:
```
pipenv shell
```
Now you can run the project scripts (see below). After interacting with the project, 
remember to exit from the virtual environment:
```
exit
```

### Scripts
```shell
./utils/store_expchains/store_expchains.sh "idc-staging.tradingview.com:8071" "hub0-tvc.xstaging.tv:8071 staging"; ./store_expchains_to_sourcedata.sh "staging"
python -m utils.external_data_generator.main --data_cluster=adx --branch=staging
python -m bin.expchains_generator -r .*-DBC -o ../expchains/group.csv
```
