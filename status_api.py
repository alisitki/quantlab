import asyncio
from aiohttp import web
from state import CollectorState
from config import SYMBOLS

class StatusAPI:
    def __init__(self, state: CollectorState, queue: asyncio.Queue):
        self.state = state
        self.queue = queue
        self.app = web.Application()
        self.app.add_routes([
            web.get('/health', self.handle_health),
            web.get('/streams', self.handle_streams),
            web.get('/metrics', self.handle_metrics),
        ])
        self.runner = None

    async def handle_health(self, request):
        data = {
            "status": "running",
            "uptime_sec": int(time_now() - self.state.start_time),
            "queue_size": self.queue.qsize(),
            "storage_backend": self.state.writer_stats.get("backend", "s3"), # derived from writer_stats
            "last_event_ts": self.state.last_event_ts,
            "last_write_ts": self.state.last_write_ts
        }
        return web.json_response(data)

    async def handle_streams(self, request):
        # Static map from logic (this is what we normally collect)
        data = {
            "symbols": SYMBOLS,
            "streams": {
                "binance": ["bbo", "trade", "mark_price", "funding"],
                "bybit": ["bbo", "trade", "mark_price", "funding", "open_interest"],
                "okx": ["bbo", "trade", "mark_price", "funding", "open_interest"]
            }
        }
        return web.json_response(data)

    async def handle_metrics(self, request):
        data = {
            "events_per_sec": self.state.eps,
            "queue_size": self.queue.qsize(),
            "total_events": self.state.total_events,
            "writer": self.state.writer_stats
        }
        return web.json_response(data)

    async def start(self, host='127.0.0.1', port=9100):
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, host, port)
        await site.start()
        print(f"[API] Status API started at http://{host}:{port}")

    async def stop(self):
        if self.runner:
            await self.runner.cleanup()
            print("[API] Status API stopped")

def time_now():
    import time
    return time.time()

async def status_api_task(state: CollectorState, queue: asyncio.Queue):
    """Task to run the Status API."""
    api = StatusAPI(state, queue)
    try:
        await api.start()
        # Keep alive until cancelled
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        await api.stop()
    except Exception as e:
        print(f"[API] Error: {e}")
