# Multiplayer App

This Django app handles real-time multiplayer functionality using Django Channels.

## Overview

The `multiplayer` app provides WebSocket consumers to manage game state and real-time communication between players. Currently, it supports a basic chat lobby where messages are broadcast to all connected clients.

## WebSocket Endpoints

### Lobby Connection

- **URL:** `ws/multiplayer/lobby/`
- **Protocol:** `ws://` (or `wss://` in production)

To connect to the lobby, use a WebSocket client to connect to the above URL.

## Consumers

### `GameConsumer`

The `GameConsumer` in `consumers.py` handles the WebSocket connection logic.

- **Connection:** Upon connection, the client is added to the "lobby" group (`multiplayer_lobby`).
- **Disconnection:** The client is removed from the group upon disconnection.
- **Receiving Messages:** Expects a JSON payload with a `message` key.
- **Broadcasting:** When a message is received, it is broadcast to all clients in the "lobby" group.

## Message Format

### Sending a Message (Client -> Server)

Messages should be sent as a JSON string:

```json
{
    "message": "Hello, world!"
}
```

### Receiving a Message (Server -> Client)

The server broadcasts messages to all connected clients in the following JSON format:

```json
{
    "message": "Hello, world!"
}
```

## Setup

Ensure your `asgi.py` is configured to route WebSocket requests to this app's routing configuration.

Example `asgi.py`:

```python
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import multiplayer.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(
        multiplayer.routing.websocket_urlpatterns
    ),
})
```

## Testing Connection

You can test the WebSocket connection using command-line tools like `wscat` or `websocat`.

### Using `wscat` (Node.js)

1.  **Install:**
    ```bash
    npm install -g wscat
    ```

2.  **Connect:**
    ```bash
    wscat -c ws://127.0.0.1:8000/ws/multiplayer/lobby/
    ```

3.  **Send a Message:**
    Once connected, type the JSON message and hit Enter:
    ```json
    {"message": "Hello from wscat!"}
    ```

### Using `websocat` (Rust/Binary)

1.  **Install:**
    Refer to the [websocat installation guide](https://github.com/vi/websocat).

2.  **Connect:**
    ```bash
    websocat ws://127.0.0.1:8000/ws/multiplayer/lobby/
    ```

3.  **Send a Message:**
    Type the JSON message and hit Enter:
    ```json
    {"message": "Hello from websocat!"}
    ```

### Using `curl` (Connection Check Only)

You can check if the endpoint is reachable (returns a 101 Switching Protocols) using `curl`:

```bash
curl -i -N \
    -H "Connection: Upgrade" \
    -H "Upgrade: websocket" \
    -H "Host: 127.0.0.1:8000" \
    -H "Origin: http://127.0.0.1:8000" \
    http://127.0.0.1:8000/ws/multiplayer/lobby/
```

