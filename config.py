"""
Configuration constants for the multi-exchange collector.
"""
import os

# Symbols to collect (USDT-margined perpetual futures)
SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "BNBUSDT",
    "SOLUSDT",
    "XRPUSDT",
    "ADAUSDT",
    "DOGEUSDT",
    "LINKUSDT",
    "OPUSDT",
    "SEIUSDT",
]

# WebSocket endpoints
BINANCE_WS_URL = "wss://fstream.binance.com/stream?streams="
BYBIT_WS_URL = "wss://stream.bybit.com/v5/public/linear"
OKX_WS_URL = "wss://ws.okx.com:8443/ws/v5/public"

# Writer settings
BUFFER_SIZE = 1000
FLUSH_INTERVAL = 5  # seconds
DATA_DIR = "/opt/quantlab/collectorV2/data"

# Queue settings
QUEUE_MAXSIZE = 100000

# Reconnect settings
RECONNECT_DELAY = 2  # seconds
MAX_RECONNECT_DELAY = 60  # seconds
HEARTBEAT_TIMEOUT = 30  # seconds

# Schema versioning (increment when event structure changes)
STREAM_VERSION = 1

# Storage backend: "local" or "s3"
STORAGE_BACKEND = os.getenv("STORAGE_BACKEND", "local")

# S3 settings (only used when STORAGE_BACKEND = "s3")
S3_ENDPOINT = os.getenv("S3_ENDPOINT", "")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", "")
S3_BUCKET = os.getenv("S3_BUCKET", "")
S3_PREFIX = os.getenv("S3_PREFIX", "")

