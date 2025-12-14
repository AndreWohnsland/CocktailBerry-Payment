<img src="https://raw.githubusercontent.com/AndreWohnsland/CocktailBerry/master/docs/pictures/CocktailBerry.svg" alt="CocktailBerry"/>

<br/>

![GitHub release (latest by date)](https://img.shields.io/github/v/release/AndreWohnsland/CocktailBerry)
![GitHub Release Date](https://img.shields.io/github/release-date/AndreWohnsland/CocktailBerry)
![Python Version](https://img.shields.io/badge/python-%3E%3D%203.11-blue)
![GitHub](https://img.shields.io/github/license/AndreWohnsland/CocktailBerry)
![GitHub issues](https://img.shields.io/github/issues-raw/AndreWohnsland/CocktailBerry)
[![Documentation Status](https://readthedocs.org/projects/cocktailberry/badge/?version=latest)](https://cocktailberry.readthedocs.io)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=AndreWohnsland_CocktailBerry&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=AndreWohnsland_CocktailBerry)
![GitHub Repo stars](https://img.shields.io/github/stars/AndreWohnsland/CocktailBerry?style=social)

[![Support CocktailBerry](https://img.shields.io/badge/Support%20CocktailBerry-donate-yellow)](https://www.buymeacoffee.com/AndreWohnsland)

CocktailBerry is a Python and Qt (or React for v2) based app for a cocktail machine on the Raspberry Pi.
It enables you to build your own, fully customized machine, while still be able to use the identical software on each machine.
Detailed information, installation steps and SetUp can be found at the [Official Documentation](https://docs.cocktailberry.org).

# CocktailBerry-Payment

Payment Service for [CocktailBerry](https://github.com/AndreWohnsland/CocktailBerry).
This service enables payment options for CocktailBerry, allowing users to integrate payment and balance management over NFC.
It is the central management point for service personal to initialize and manage user accounts, balances and transactions.

## Setup

TBD.

## Features

TBD.

## Development

This project uses [uv](https://docs.astral.sh/uv/) to manage all its dependencies.
To get started, you need to install uv and then install the dependencies.

```bash
uv sync --all-extras
```

We also use pre-commits to check the code style and run some tests before every commit.
You can install them with:

```bash
uv run pre-commit install --install-hooks
```

This will install all dependencies and you can start developing.
Then just run:

```bash
uv run -m cocktailberry.api
```

for the backend.
You can run the user management with:

```bash
uv run -m cocktailberry.gui
```

in another terminal.

## Open Tasks

- [ ] Docker files for backend and frontend
- [ ] Compose Files + templates build by cli
- [ ] CLI to set everything up
- [ ] Translation validation in CI (all keys present)
- [ ] Installer scripts for both Linux and Windows
- [ ] DB Backups
- [ ] Option to Overwrite (put) nfcs
