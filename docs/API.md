# API Documentation

Base URL: `http://localhost:8000/api`

## Authentication

### Guest Login
-   **URL**: `/auth/guest/`
-   **Method**: `POST`
-   **Auth Required**: No
-   **Response**:
    ```json
    {
      "access": "jwt_access_token",
      "user_id": "uuid",
      "identity_type": "guest"
    }
    ```

### Google Login
-   **URL**: `/auth/google/`
-   **Method**: `POST`
-   **Body**: `{ "token": "google_id_token" }`
-   **Auth Required**: No
-   **Response**:
    ```json
    {
      "access": "jwt_access_token",
      "user_id": "uuid",
      "identity_type": "permanent",
      "email": "user@example.com",
      "created": true
    }
    ```

### Get Current User
-   **URL**: `/auth/me/`
-   **Method**: `GET`
-   **Auth Required**: Yes (`Authorization: Bearer <token>`)
-   **Response**:
    ```json
    {
      "identity_type": "guest/permanent",
      "user_id": "uuid",
      "username": "guest_12345",
      "email": "..."
    }
    ```

### Logout
-   **URL**: `/auth/logout/`
-   **Method**: `POST`
-   **Auth Required**: Yes
-   **Response**: `{ "message": "Logged out successfully" }`

## Users
### List Users (Admin Only)
-   **URL**: `/auth/users/`
-   **Method**: `GET`
-   **Auth Required**: Yes (Admin)
-   **Response**: Array of user objects.
