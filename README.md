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

## Features

CocktailBerry-Payment is an optional extension to CocktailBerry, providing the following features:

- NFC based payment system and user privileges (e.g. age/alcohol restrictions)
- User account management and top-up functionality

Below is a high-level schema of how the service integrates with CocktailBerry and other components.

![Schema of Service](./docs/schema.svg)

The service consists of two main components:

1. **Backend API**:
A RESTful API built with FastAPI, responsible for handling all payment-related operations, user management, and database interactions.
Only one instance of this should be used to have consistent data.
2. **Frontend GUI**:
Management Admin application for owners to create and top up nfc chips/cards.
You can use as many instances as you want.
While you can run it on the same device as the backend, it is recommended to run it on a separate device for better performance and security.

CocktailBerry Machines using the payment option will communicate with the backend API to process payments and manage user balances.
This requires the machines being either on the same network or having access to the backend API over the internet.
User will then pay the cocktails over NFC cards, while service personal can manage the users and top up balances via the GUI separately.

## Setup

If you have experienced CocktailBerry, you know that we try to simplify the setup as much as possible.
We boiled the process down to a few commands, it will still be a little bit more complex than a regular CocktailBerry setup.
While you can run the backend on the same machine as CocktailBerry, or the the Admin payment GUI, it is recommended to run them on separate devices for better performance and security.

The recommended way for a "basic" hardware setup is:

- A Server (can be a Raspberry Pi 4 or similar) running the payment API over docker
- A desktop device connected with a USB NFC reader running the payment GUI, can be Windows
- CocktailBerry machine having a USB NFC reader and connected to the payment API over the network

If you want to really keep it minimalistic, you can also run both API and GUI on the same device, e.g. a Raspberry Pi 4.
In this case you would need to ensure that this device is not down, otherwise users will not be able to order cocktails.
More CocktailBerry machines or GUI instances can be added at any time, just point them to the same backend API.

CocktailBerry machines should be set up according to the official documentation, just ensure that the payment option is enabled and the API URL is set correctly.
For your other devices, follow the steps below, we need to distinguish between Windows and Linux based systems.
MacOS might work as well, but is not officially supported.

### Linux preparation

Linux is the most easy way, since most of the things can be done over a script.
Just run:

```bash
wget -O https://github.com/AndreWohnsland/CocktailBerry-Payment/blob/main/scripts/unix_installer.sh
```

Then follow the [services installation](#service-installation) steps below.

### Windows preparation

Windows can be quite restrictive when it comes to executing scripts and similar tasks.
Make sure the user is able to execute PowerShell scripts and install applications.
If you want to use docker on windows, make sure you [install it](https://docs.docker.com/desktop/setup/install/windows-install/) and set it to auto start with windows.

Then just open a PowerShell terminal as Administrator and run the following command to download and execute the installation script:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://github.com/AndreWohnsland/CocktailBerry-Payment/blob/main/scripts/windows_installer.ps1 | iex"
```

<!-- TODO: LINK -->
<!-- Alternatively, there is also a pre-built executable available for the GUI, which you can download from the release page. -->
<!-- You might not be able to set all options tough when using this directly, so even when using this, going over this preparation and service installation steps is recommended. -->

Then follow the [services installation](#service-installation) steps below.

### Service installation

Make sure you have followed the preparation steps for your OS.
After that you should already be in the CocktailBerry-Payment folder.
You can use:

```bash
uv run -m cocktailberry.setup
```

to start the interactive setup.
You will be prompted for all necessary information and the script will set up everything for you.
You might need to restart your device after the installation is done, depending on the options you selected and your OS.

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

### Open Tasks

- [ ] DB Backups
- [ ] Option to Overwrite (put) nfcs
- [ ] Transaction Logs
