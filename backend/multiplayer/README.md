# `multiplayer` App

The `multiplayer` app provides real-time WebSocket support for multiplayer game sessions using **Django Channels**.

---

## Current State

The app currently implements the WebSocket connection layer and a broadcast lobby. Full multiplayer game orchestration (synced rounds, guesses, leaderboard pushes) is **planned but not yet implemented** — the REST-based `game` app handles all round and scoring logic today.

---

## Stack

| Component        | Library                                             |
| ---------------- | --------------------------------------------------- |
| WebSocket server | [Django Channels](https://channels.readthedocs.io/) |
| Channel layer    | Redis (`channels_redis`)                            |
| Auth             | `CustomJWTAuthentication` (via query string token)  |

---

## Consumer: `GameConsumer`

File: `consumers.py`

An `AsyncWebsocketConsumer` that manages the WebSocket lifecycle.

### Connection (`connect`)

1. Extracts the JWT from the WebSocket URL query string (`?token=...`)
2. Verifies the token and resolves the `User` via `get_user_from_token()`
3. If invalid → closes connection with code `4003`
4. Joins the `multiplayer_lobby` channel group and accepts the connection

### Disconnection (`disconnect`)

Leaves the channel group. Safe even if connection was never fully established (checks for `room_group_name`).

### Message Handling (`receive` / `chat_message`)

Broadcasts any received message to all members of the channel group:

```
Client → receive() → group_send() → chat_message() → all clients in group
```

---

## Routing

File: `routing.py`

WebSocket URL pattern:

```
ws://<host>/ws/game/
```

---

## Authentication

The WebSocket handshake doesn't support HTTP headers in the browser, so the JWT is passed as a query parameter:

```
ws://localhost:8000/ws/game/?token=<access_token>
```

The consumer validates the token using `database_sync_to_async` to safely perform the DB lookup from an async context.

---

## Planned Features

- Synced round start/end events pushed to all players in a room
- Real-time guess submission and score reveal
- Room-specific channel groups (currently all clients share a single `lobby` group)
- Player join/leave notifications

---

## Dependencies

- **`authentication`** — `User` model for token resolution
- **`game`** — Will consume `GameService` methods once full multiplayer is implemented
- **Redis** — Required as the Django Channels channel layer backend
