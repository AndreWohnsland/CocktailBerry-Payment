# Copilot Instructions for CocktailBerry-Payment

## Project Overview

CocktailBerry-Payment is a payment and balance management service for the [CocktailBerry](https://github.com/AndreWohnsland/CocktailBerry) cocktail machine project. It provides NFC-based payment options, user account management, and transaction handling for service personnel.

## Tech Stack

- **Backend**: FastAPI (Python web framework for building APIs)
- **Frontend/Admin UI**: Streamlit (Python-based web app framework)
- **Server**: Uvicorn (ASGI server)
- **Database**: SQLite with SQLAlchemy ORM and Alembic for migrations
- **Python Version**: >= 3.13
- **Package Manager**: uv (modern Python package manager)

## Code Style & Conventions

### Python Standards
- Follow PEP 8 with a line length of 120 characters
- Use type annotations for all function parameters and return values
- Use pathlib for file path operations (enforced via ruff's PTH rules)
- Prefer list/dict comprehensions over map/filter

### Naming Conventions
- Use snake_case for functions and variables
- Use PascalCase for classes
- Use UPPER_CASE for constants
- Prefix private methods/attributes with underscore

### Imports
- Group imports: standard library, third-party, local
- Use isort for import ordering
- Use conventional import aliases (e.g., `import numpy as np`)

### Documentation
- Docstrings are optional but encouraged for complex functions
- Use Google-style docstrings when documenting

## Project Structure (Planned)

```
cocktailberry-payment/
├── src/
│   ├── backend/           # FastAPI application code
│   │   ├── api/           # FastAPI routes and endpoints
│   │   ├── core/          # Core/internal (config, settings)
│   │   ├── models/        # Pydantic models and database schemas
│   │   ├── services/      # Business logic layer
│   │   ├── db/            # Database connections and queries
│   │   └── utils/         # Helper functions and utilities
│   └── frontend/          # Streamlit admin interface
│       ├── view/          # basic ui components + pages
│       ├── data/          # if needed: data handling functions
├── tests/                 # pytest test files
├── main.py                # Application entry point
└── pyproject.toml         # Project configuration
```

## FastAPI Guidelines

- Use Pydantic models for request/response validation
- Implement proper HTTP status codes
- Use dependency injection for shared resources
- Group related endpoints with APIRouter
- Follow RESTful naming conventions for endpoints
- Use async/await for I/O-bound operations

## Streamlit Guidelines

- Keep the UI simple and intuitive for service personnel
- Use session state for maintaining user data across reruns
- Organize pages using Streamlit's multipage app structure
- Validate user inputs before processing

## Testing

- Use pytest for unit and integration tests
- Aim for good test coverage (pytest-cov)
- Test API endpoints with FastAPI's TestClient
- Mock external dependencies in tests

## Development Workflow

1. Install dependencies: `uv sync`
2. Install pre-commit hooks: `uv run pre-commit install --install-hooks`
3. Run the application: `uv run main.py`
4. Run tests: `uv run pytest`
5. Type checking: `uv run mypy .`
6. Linting: `uv run ruff check .`

## Key Features to Implement

- User account creation and management via NFC
- Balance top-up and deduction
- Transaction history and logging
- Service personnel authentication
- Integration with CocktailBerry main application
- Real-time balance updates

## Common Patterns

### API Endpoint Example
```python
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

router = APIRouter(prefix="/users", tags=["users"])

class UserCreate(BaseModel):
    nfc_id: str
    name: str

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate) -> dict:
    """Create a new user account."""
    # Implementation here
    return {"message": "User created", "nfc_id": user.nfc_id}
```

### Streamlit Page Example
```python
import streamlit as st

st.set_page_config(page_title="CocktailBerry Payment", page_icon="🍹")

st.title("Balance Management")

if "balance" not in st.session_state:
    st.session_state.balance = 0.0

amount = st.number_input("Amount", min_value=0.0, step=0.50)
if st.button("Add Balance"):
    st.session_state.balance += amount
    st.success(f"New balance: €{st.session_state.balance:.2f}")
```

## When Helping with This Project

1. **Always use type hints** for function signatures
2. **Prefer async functions** for API endpoints
3. **Use Pydantic models** for data validation
4. **Follow the existing ruff configuration** for linting rules
5. **Write code compatible with Python 3.13+**
6. **Use uv commands** instead of pip/poetry for package management
7. **Keep the code simple** - this is for service personnel, not developers
