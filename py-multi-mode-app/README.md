# Python Multi-Mode App (Tkinter GUI + Async WebSocket Server)

This example shows how to run the same **Controller** in a background **thread** for two modes:

1. **Server mode**: `asyncio` WebSocket server in the main thread, broadcasting data from the Controller.
2. **GUI mode**: Tkinter mainloop in the main thread, updating the UI from the Controller.

All communication across threads uses simple, typed **Channels** (wrapping `queue.Queue`) with per-topic configs and backpressure policies.

## Layout

```
py-multi-mode-app/
├── README.md
├── requirements.txt
├── messages.py
├── channels.py
├── controller.py
├── bridge_async.py
├── server_mode.py
├── tk_mode.py
├── run_server.py
└── run_gui.py
```

## Quick start

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate

pip install -r requirements.txt

# Run server mode (WebSocket on ws://localhost:8765)
python run_server.py

# Try a quick client in another terminal:
python - <<'PY'
import asyncio, websockets
async def main():
    async with websockets.connect("ws://127.0.0.1:8765") as ws:
        print(await ws.recv())  # hello
        for _ in range(5):
            print(await ws.recv())
asyncio.run(main())
PY

# GUI mode
python run_gui.py
```

## References

- Python `queue.Queue` (thread-safe): https://docs.python.org/3/library/queue.html
- `asyncio` loop + thread interaction: https://docs.python.org/3/library/asyncio-eventloop.html#asyncio.loop.call_soon_threadsafe
- `asyncio.Queue`: https://docs.python.org/3/library/asyncio-queue.html
- Tkinter `after()` scheduling: https://docs.python.org/3/library/tkinter.html#widget.after
- `websockets` library: https://websockets.readthedocs.io/en/stable/
