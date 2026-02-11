# Authentication Module

The `authentication` app manages user identity, login flows, and session security.

## 📦 Models

### `User`
Extends `AbstractBaseUser`.
-   **`user_id`**: UUID, Primary Key.
-   **`username`**: String. Unique. Auto-generated for guests (e.g., `guest_123abc`).
-   **`email`**: EmailField. Unique. Nullable (Guests have no email).
-   **`auth_provider`**: Enum: `guest`, `google`, `email`.
-   **`is_guest`**: Boolean. True if the user is a guest.

## 🔗 API Endpoints

### 1. Guest Login
Create a new temporary guest account.

-   **URL**: `/api/auth/guest/`
-   **Method**: `POST`
-   **Auth Required**: No
-   **Response**:
    ```json
    {
        "user_id": "uuid-string",
        "username": "guest_xyz",
        "identity_type": "guest",
        "tokens": {
            "access": "jwt-access-token",
            "refresh": "jwt-refresh-token"
        }
    }
    ```

### 2. Google Login
Login or Register using a Google ID Token.

-   **URL**: `/api/auth/google/`
-   **Method**: `POST`
-   **Auth Required**: No
-   **Body**:
    ```json
    {
        "token": "google-id-token-from-frontend"
    }
    ```
-   **Response**:
    ```json
    {
        "user_id": "uuid-string",
        "username": "John Doe",
        "email": "john@example.com",
        "identity_type": "permanent",
        "tokens": {
            "access": "jwt-access-token",
            "refresh": "jwt-refresh-token"
        }
    }
    ```

### 3. Logout
Invalidates the user's session in Redis.

-   **URL**: `/api/auth/logout/`
-   **Method**: `POST`
-   **Auth Required**: Yes (Bearer Token)
-   **Response**: `200 OK`

## 🧠 Session Management Strategy

We allow concurrent logins but maintain control via Redis.

1.  **Login**: 
    -   A key `session:{user_id}` is set in Redis with a TTL (e.g., 30 days).
    -   Value: Timestamp or session metadata.
2.  **Request**: 
    -   Custom Permission class verifies `Authorization` header.
    -   Decodes JWT to get `user_id`.
    -   Checks if `session:{user_id}` exists in Redis.
    -   If not found (expired or logged out), request is denied `401 Unauthorized`.
3.  **Logout**:
    -   Deletes `session:{user_id}` from Redis.
