import asyncio
import websockets
import json

async def test_connection():
    uri = "ws://localhost:8002/ws/multiplayer/lobby/"
    async with websockets.connect(uri) as websocket:
        print(f"Connected to {uri}")
        
        # Send a message
        message = {"message": "Hello Server!"}
        await websocket.send(json.dumps(message))
        print(f"Sent: {message}")
        
        # Receive response
        response = await websocket.recv()
        print(f"Received: {response}")

if __name__ == "__main__":
    asyncio.run(test_connection())
