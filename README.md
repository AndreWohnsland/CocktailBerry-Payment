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
It is the central management point for service personnel to initialize and manage user accounts, balances and transactions.

## Features

- **FastAPI Backend**: RESTful API for user and balance management
  - User CRUD operations (Create, Read, Update, Delete)
  - Balance top-up and deduction
  - Cocktail booking with age verification and balance checks
  - NFC card scanning integration
  
- **Streamlit Frontend**: User-friendly web interface for service personnel
  - User Management: Create, edit, and delete users via NFC
  - Balance Top-up: Add or subtract balance from user accounts
  - Real-time NFC scanning
  
- **NFC Integration**: Automatic card scanning at program start
  - Callbacks for real-time card detection
  - Graceful fallback when hardware is not available
  
- **Single Entrypoint**: Both API and frontend run from one command
  - FastAPI runs on port 8000
  - Streamlit runs on port 8501
  
- **SQLite Database**: Lightweight, file-based storage
  - User profiles with NFC ID, name, balance, and age status
  - Located at `~/.cocktailberry/payment.db`

## Setup

### Prerequisites

- Python >= 3.13
- [uv](https://docs.astral.sh/uv/) package manager
- NFC reader hardware (optional - software works without it for testing)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/AndreWohnsland/CocktailBerry-Payment.git
cd CocktailBerry-Payment
```

2. Install dependencies:
```bash
uv sync
```

3. (Optional) Install pre-commit hooks:
```bash
uv run pre-commit install --install-hooks
```

### Running the Application

Start both the API and frontend with a single command:

```bash
uv run main.py
```

This will start:
- **FastAPI Backend** at http://localhost:8000
- **Streamlit Frontend** at http://localhost:8501

The API documentation is available at http://localhost:8000/docs

## Usage

### Service Personnel Interface (Streamlit)

1. Open http://localhost:8501 in your browser
2. Choose between two tabs:
   - **User Management**: Create, edit, or delete users
   - **Balance Top-Up**: Add or subtract balance from user accounts
3. Click "Scan NFC Card" to read a user's card
4. Follow the on-screen prompts to complete your action

### API Integration

The API can be integrated with the CocktailBerry main application for cocktail booking:

```python
import requests

# Book a cocktail
response = requests.post(
    "http://localhost:8000/api/cocktails/book",
    json={
        "nfc_id": "A1B2C3D4",
        "amount": 5.50,
        "is_alcoholic": True
    }
)

if response.status_code == 200:
    user = response.json()
    print(f"Booking successful! New balance: €{user['balance']:.2f}")
elif response.status_code == 403:
    print("Error: User is underage")
elif response.status_code == 402:
    print("Error: Insufficient balance")
```

See [API Documentation](docs/API.md) for complete endpoint details.

## Project Structure

```
cocktailberry-payment/
├── src/
│   ├── backend/           # FastAPI application
│   │   ├── api/           # API routes and endpoints
│   │   ├── core/          # NFC integration and config
│   │   ├── models/        # Database and Pydantic models
│   │   ├── services/      # Business logic
│   │   └── db/            # Database connection
│   └── frontend/          # Streamlit application
│       ├── view/          # UI components
│       └── data/          # API client
├── tests/                 # Pytest tests with in-memory DB
├── docs/                  # Documentation
├── main.py                # Application entrypoint
└── pyproject.toml         # Project configuration
```

## Development

### Running Tests

The project uses pytest for testing. Tests are located in the `tests/` directory and use an in-memory SQLite database.

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_user_service.py

# Run with coverage
uv run pytest --cov=src
```

**Test Structure:**
- `tests/conftest.py` - Shared fixtures including in-memory database setup
- `tests/test_user_service.py` - Service layer tests (27 tests covering all user operations)

All tests mock the NFC reader and use dependency injection with in-memory databases, so no hardware is required.

### Linting

```bash
uv run ruff check .
```

### Type Checking

```bash
uv run mypy .
```

## NFC Hardware

The application supports USB-connected PC/SC NFC readers. When hardware is not available, the application runs in fallback mode where NFC scanning returns `null`.

For production use with real NFC hardware, ensure:
- The `pyscard` library is installed
- PC/SC drivers are available on your system
- Your NFC reader is connected and recognized

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run linting and tests
5. Submit a pull request

## License

See [LICENSE](LICENSE) file for details.
