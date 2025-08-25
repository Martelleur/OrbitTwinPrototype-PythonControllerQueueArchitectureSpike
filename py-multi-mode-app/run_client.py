import asyncio, websockets
async def main():
    async with websockets.connect("ws://127.0.0.1:8765") as ws:
        print(await ws.recv())  # hello
        for _ in range(5):
            print(await ws.recv())
asyncio.run(main())