"""Shared constants for the frontend."""

# HTTP Status Codes
HTTP_OK = 200
HTTP_CREATED = 201
HTTP_NO_CONTENT = 204

# NFC Scanning Configuration
NFC_SCAN_TIMEOUT = 10.0  # Timeout for one-shot NFC scan in seconds

# Balance limits
MIN_BALANCE = -1000.0  # Minimum allowed balance for data integrity
MAX_BALANCE = 1000.0  # Maximum balance for input validation
