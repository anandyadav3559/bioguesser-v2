# Authentication App Documentation

This app handles user identification, session management, and JWT issuance.

## Models

### `User`
-   **`user_id`**: UUID (Primary Key).
-   **`username`**: Unique string (auto-generated for guests/google users).
-   **`email`**: Email address (Unique, nullable).
-   **`auth_provider`**: 'guest', 'google', or 'manual'.
-   **`is_guest`**: Boolean flag.

## Authentication Flows

### 1. Guest Login
-   **Endpoint**: `/api/auth/guest/`
-   **Method**: `POST`
-   **Process**:
    1.  Create a new `User` with `is_guest=True`.
    2.  Create a Session in Redis (`session:<user_id>`) with expiration (30 days).
    3.  Issue JWT Access Token (1 hour) and Refresh Token (30 days).
-   **Response**: `user_id`, `access`, `identity_type='guest'`.

### 2. Google OAuth Login
-   **Endpoint**: `/api/auth/google/`
-   **Method**: `POST`
-   **Payload**: `{ "token": "<GOOGLE_ID_TOKEN>" }`
-   **Process**:
    1.  Verify ID Token with Google.
    2.  Get or Create `User` based on email.
    3.  Create/Update Session in Redis (30 days).
    4.  Issue JWT Access Token (1 hour) and Refresh Token (30 days).
-   **Response**: `user_id`, `access`, `identity_type='permanent'`, `email`.

### 3. Logout
-   **Endpoint**: `/api/auth/logout/`
-   **Method**: `POST` (Requires Auth Header)
-   **Process**:
    1.  Deletes the Redis session key `session:<user_id>`.

## Session Management
-   **Storage**: Redis.
-   **Key Format**: `session:<uuid>`
-   **TTL**: 30 Days.
-   **Validation**: The `CustomJWTAuthentication` class checks if the Redis session exists for every request. If missing, the token is considered invalid even if the JWT signature is correct.
