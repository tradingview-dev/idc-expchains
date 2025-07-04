# TV Exchanges

[![pipeline status](https://git.xtools.tv/idc/exchanges/badges/master/pipeline.svg)](https://git.xtools.tv/idc/exchanges/-/commits/master)

Centralized storage of the list of exchanges supported by TradingView and their properties and descriptions.

**Responsible team**: IDC Team (#team-idc)

## Overview
- [Project Description](#project-description)
- [Getting the Sources](#getting-the-sources)
- [Requirements](#requirements)
- [System-based prepare](#system-based-prepare)
  - [Ubuntu](#ubuntu)
  - [Windows](#windows)
  - [MacOS](#macos)
- [Commonly prepare](#commonly-prepare)
- [Prepare the project](#prepare-the-project)
- [Run](#run)
  - [Validations](#validations)
  - [Generators](#generators)

## Project Description
To get more information about the project structure, please go to [Knowledge Base](./doc/structure.md).

## Getting the Sources
In your terminal, navigate to the directory that will contain the exchanges top-level repository 
and use the git command line to make a clone:
```
git clone git@git.xtools.tv:idc/exchanges.git
```
Alternatively, if you're behind a firewall and want to use the https protocol:
```
git clone https://git.xtools.tv/idc/exchanges.git
```

## Requirements

| Tool         | Supported Versions                                 |
|--------------|----------------------------------------------------|
| OS           | Ubuntu 22.04 and above / Windows 11 + WSL2 / macOS |
| Git          | 1.6.x and above                                    |
| Python       | 3.10 and above                                     |

## System-based prepare
First, you need to install the `pipx` package. The `pipx` is a tool that allows you to 
install Python programs in isolated environments without clogging up site-packages.

### Ubuntu
Run step by step in your terminal:
```
sudo apt update
sudo apt install pipx
pipx ensurepath
```
After that, re-open your terminal and run:
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

### MacOS
Run step by step in your terminal:
```
brew install pipx
pipx ensurepath
```
After that, re-open a PowerShell and run:
```
pipx --version
```

## Commonly prepare
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

## Prepare the project
Now you need to create a virtual environment and install required dependencies. 
In your terminal run step by step:
```
cd /path/to/exchanges
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

### Validations
```shell
python -m bin.checkers.SIFieldsChecker -s ./symbolinfo-fields.yaml
python -m bin.checkers.ExchangesChecker -p providers.yaml -e exchanges/ -s true
python -m bin.checkers.NewsProviderChecker -n news/
python -m bin.checkers.FinIndicatorsChecker -i financial-indicators/indicators.yaml -c economic-categories.yaml
```

### Generators
```shell
python -m bin.generators.build_exchange_info --exchanges-path exchanges/ --out ./out/exchange-info.json
python -m bin.generators.build_news_providers -n ./news/ -N ./out/news-providers.json
python -m bin.generators.build_economic_sources --sources ./economic-sources.yaml --out ./out/economic-sources.json
python -m bin.generators.build_fields_permissions --symbolinfo-fields ./symbolinfo-fields.yaml --out ./out/fields-permissions.json
python -m bin.generators.build_restrictions --exchanges-path ./exchanges --out ./out/restrictions.json
python -m bin.generators.build_economic_categories --categories-path ./economic-categories.yaml --out ./out/economic-categories.json
python -m bin.generators.build_exchange_sources2 --exchanges-path ./exchanges --economic-sources-path ./economic-sources.yaml --out ./out/exchange-sources2.json
python -m bin.generators.build_world_economy_indicators --indicators-path ./financial-indicators --categories-path ./economic-categories.yaml --out ./out/world-economy-indicators.json
python -m bin.generators.build_financial_indicators2 --indicators-path ./financial-indicators --out ./out/financial-indicators2.json
```
