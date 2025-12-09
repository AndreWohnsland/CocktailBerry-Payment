# API Documentation

## Base URL

`http://localhost:8000`

## Endpoints

### Root

**GET /** 

Returns API information.

**Response:**
```json
{
  "message": "CocktailBerry Payment API"
}
```

---

### NFC Scanning

**GET /api/nfc/scan**

Get the latest scanned NFC ID (non-blocking). Returns `null` if no card has been scanned since the last call.

**Response:**
```json
{
  "nfc_id": "A1B2C3D4"
}
```
or `null`

---

### User Management

#### List All Users

**GET /api/users**

List all users with pagination.

**Query Parameters:**
- `skip` (optional): Number of users to skip (default: 0)
- `limit` (optional): Maximum number of users to return (default: 100)

**Response:**
```json
[
  {
    "id": 1,
    "nfc_id": "A1B2C3D4",
    "name": "John Doe",
    "balance": 25.50,
    "is_adult": true
  }
]
```

---

#### Get User by NFC ID

**GET /api/users/{nfc_id}**

Get a specific user by their NFC card ID.

**Response:**
```json
{
  "id": 1,
  "nfc_id": "A1B2C3D4",
  "name": "John Doe",
  "balance": 25.50,
  "is_adult": true
}
```

**Error Responses:**
- `404`: User not found

---

#### Create User

**POST /api/users**

Create a new user.

**Request Body:**
```json
{
  "nfc_id": "A1B2C3D4",
  "name": "John Doe",
  "is_adult": true
}
```

**Response:** (Status: 201 Created)
```json
{
  "id": 1,
  "nfc_id": "A1B2C3D4",
  "name": "John Doe",
  "balance": 0.0,
  "is_adult": true
}
```

**Error Responses:**
- `400`: User with this NFC ID already exists

---

#### Update User

**PUT /api/users/{nfc_id}**

Update user information. All fields are optional.

**Request Body:**
```json
{
  "name": "Jane Doe",
  "is_adult": false,
  "balance": 50.0
}
```

**Response:**
```json
{
  "id": 1,
  "nfc_id": "A1B2C3D4",
  "name": "Jane Doe",
  "balance": 50.0,
  "is_adult": false
}
```

**Error Responses:**
- `404`: User not found

---

#### Delete User

**DELETE /api/users/{nfc_id}**

Delete a user by their NFC card ID.

**Response:** (Status: 204 No Content)

**Error Responses:**
- `404`: User not found

---

### Balance Management

#### Update Balance

**POST /api/balance/update**

Add or subtract from a user's balance. Use negative amounts to subtract.

**Request Body:**
```json
{
  "nfc_id": "A1B2C3D4",
  "amount": 10.0
}
```

**Response:**
```json
{
  "id": 1,
  "nfc_id": "A1B2C3D4",
  "name": "John Doe",
  "balance": 35.50,
  "is_adult": true
}
```

**Error Responses:**
- `404`: User not found

---

### Cocktail Booking

#### Book Cocktail

**POST /api/cocktails/book**

Book a cocktail and deduct the amount from the user's balance. Includes age verification for alcoholic drinks and balance checks.

**Request Body:**
```json
{
  "nfc_id": "A1B2C3D4",
  "amount": 5.50,
  "is_alcoholic": true
}
```

**Response:**
```json
{
  "id": 1,
  "nfc_id": "A1B2C3D4",
  "name": "John Doe",
  "balance": 30.00,
  "is_adult": true
}
```

**Error Responses:**
- `402 Payment Required`: Insufficient balance
- `403 Forbidden`: User is underage and cannot purchase alcoholic cocktails
- `404`: User not found

---

## Error Format

All errors follow this format:

```json
{
  "detail": "Error message description"
}
```

---

## Integration Examples

### Python

```python
import requests

BASE_URL = "http://localhost:8000"

# Create a user
response = requests.post(
    f"{BASE_URL}/api/users",
    json={
        "nfc_id": "A1B2C3D4",
        "name": "John Doe",
        "is_adult": True
    }
)
user = response.json()

# Book a cocktail
response = requests.post(
    f"{BASE_URL}/api/cocktails/book",
    json={
        "nfc_id": "A1B2C3D4",
        "amount": 5.50,
        "is_alcoholic": False
    }
)
updated_user = response.json()
print(f"New balance: €{updated_user['balance']:.2f}")
```

### JavaScript

```javascript
const BASE_URL = "http://localhost:8000";

// Create a user
const response = await fetch(`${BASE_URL}/api/users`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    nfc_id: "A1B2C3D4",
    name: "John Doe",
    is_adult: true
  })
});
const user = await response.json();

// Book a cocktail
const bookResponse = await fetch(`${BASE_URL}/api/cocktails/book`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    nfc_id: "A1B2C3D4",
    amount: 5.50,
    is_alcoholic: false
  })
});
const updatedUser = await bookResponse.json();
console.log(`New balance: €${updatedUser.balance.toFixed(2)}`);
```
