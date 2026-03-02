# `authentication` App

The `authentication` app handles all identity management for BioGuesser — guest sessions, Google OAuth, JWT issuance, and user profile retrieval. It defines the custom `User` model used throughout the project.

---

## Model

### `User`

A custom, lightweight user model (does **not** extend `AbstractUser` to keep it minimal).

| Field            | Type             | Description                             |
| ---------------- | ---------------- | --------------------------------------- |
| `user_id`        | `UUIDField`      | Primary key                             |
| `username`       | `CharField(100)` | Unique display name                     |
| `email`          | `EmailField`     | Unique, nullable (guests have no email) |
| `is_guest`       | `BooleanField`   | `True` for ephemeral guest sessions     |
| `auth_provider`  | `CharField(50)`  | `"guest"`, `"google"`, or `"manual"`    |
| `created_at`     | `DateTimeField`  | Auto-set                                |
| `last_active_at` | `DateTimeField`  | Auto-updated on every save              |

**DB table**: `users`

**Indexes**: `auth_provider`, `created_at`, `last_active_at`

---

## Authentication Flow

### JWT + Redis Session

All protected endpoints use a **dual-layer** authentication strategy:

1. **JWT** (`rest_framework_simplejwt`) — signed token containing `user_id` and `identity_type`
2. **Redis session** — a `session:{user_id}` key acts as a revocation layer; logging out deletes this key, instantly invalidating the token even before expiry

The `CustomJWTAuthentication` class (`authentication.py`) validates both layers on every request.

### Identity Types

| Type        | `is_guest` | TTL     | Behaviour on logout                       |
| ----------- | ---------- | ------- | ----------------------------------------- |
| `guest`     | `True`     | 4 hours | Account is **deleted** (no residual data) |
| `permanent` | `False`    | 30 days | Session revoked, account kept             |

---

## API Endpoints

Base prefix: `/auth/`

### `POST /auth/guest/`

Creates an ephemeral guest user and returns a JWT. No body required.

**Response:**

```json
{ "access": "jwt...", "user_id": "uuid", "identity_type": "guest" }
```

---

### `POST /auth/google/`

Verifies a Google ID token and signs in (or creates) the corresponding permanent user.

**Body:**

```json
{ "token": "<google_id_token>" }
```

**Response:**

```json
{
  "access": "jwt...",
  "user_id": "uuid",
  "identity_type": "permanent",
  "email": "...",
  "created": true
}
```

---

### `POST /auth/permanent/`

Creates a manual (non-OAuth) permanent user account.

**Body:**

```json
{ "email": "user@example.com" }
```

---

### `GET /auth/me/`

Returns the current user's profile, stats, and game history.

**Response:**

```json
{
  "user_id": "uuid",
  "username": "anand",
  "is_guest": false,
  "stats": { "games_played": 12, "total_score": 847.5, "high_score": 98.0 },
  "game_history": [{ "room_code": "...", "score": 72.5, "rounds": 5 }]
}
```

---

### `PATCH /auth/me/`

Updates the current user's username. Validates uniqueness and max length (100 chars).

**Body:**

```json
{ "username": "newname" }
```

---

### `DELETE /auth/me/`

Permanently deletes the user's account and clears their Redis session. Cascades to profiles, rooms, and guesses.

---

### `POST /auth/logout/`

Revokes the Redis session. For guest users, also deletes the account.

---

### `GET /auth/users/`

Admin-only. Returns all users.

---

### JWT Token Endpoints (via `simplejwt`)

| Method | Path             | Description          |
| ------ | ---------------- | -------------------- |
| `POST` | `/auth/login/`   | Obtain token pair    |
| `POST` | `/auth/refresh/` | Refresh access token |

---

## Supporting Modules

| File                | Purpose                                                                  |
| ------------------- | ------------------------------------------------------------------------ |
| `authentication.py` | `CustomJWTAuthentication` — validates JWT + Redis session                |
| `services.py`       | `get_user_profile_data()` — aggregates profile + game history for `/me/` |
| `middleware.py`     | Attaches user to request context                                         |
| `throttling.py`     | Custom rate limit classes                                                |
| `management/`       | Django management commands (e.g. guest cleanup)                          |

---

## Dependencies

- **`userprofile`** — `UserProfile` stats read by `get_user_profile_data()`
- **`game`** — Room/round history read for the `/me/` game history
- **Redis** — Session store; required for token revocation
