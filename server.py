import asyncio
import websockets

async def handler(ws):
    async for message in ws:
        print("Received:", message)
        await ws.send(f"Server received: {message}")

async def main():
    async with websockets.serve(handler, "0.0.0.0", 8080):
        print("✅ WebSocket server running on ws://localhost:8080/ws")
        await asyncio.Future()

asyncio.run(main())
