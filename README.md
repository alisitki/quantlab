# QuantLab Multi-Exchange Crypto Data Collector

Production-ready high-performance data collector for USDT-USDC margined perpetual futures from Binance, Bybit, and OKX.

---

## 1️⃣ What the Collector IS
The QuantLab Collector is a **RAW market data ingestion service** designed for high-performance capture of cryptocurrency futures data. It consumes real-time market data exclusively through **WebSocket streams** and writes these events, unmodified, to a RAW Parquet layer. Its sole responsibility is to act as a faithful recorder of the exchange's "WebSocket truth." It does not improve data, fix gaps, backfill history, reorder events, deduplicate records, or interpret signals.

---

## 2️⃣ What the Collector is NOT
To maintain strict architectural separation and data integrity, the collector explicitly excludes the following responsibilities:
- **NOT a recovery system**: It does not attempt to mend broken history.
- **NOT a COMPACT layer**: It does not perform deduplication or reordering.
- **NOT a trading engine**: It has no execution or risk management capabilities.
- **NOT a data correction engine**: It records what it sees, including errors or gaps.
- **NOT self-healing/auto-restarting**: It reports its state but does not take autonomous corrective actions.

These responsibilities are deferred to downstream layers (e.g., COMPACT or Replay) to ensure the RAW layer remains an unadulterated source of truth.

---

## 3️⃣ Data Semantics (RAW Contract)
The RAW layer provided by the collector adheres to a strict contract:
- **Data Source**: Exclusively WebSocket stream data.
- **Parquet Schema**: Fixed, versioned (v1), and immutable.
- **Guarantees**:
  - **Schema Stability**: The structure of the stored data will not change.
  - **No Contamination**: ZERO snapshot data, REST markers, or backfill alignment events are written to RAW.
- **Non-Guarantees**:
  - **Continuity**: Gaps may occur due to network or exchange issues.
  - **Ordering**: Event ordering across reconnects or multi-exchange streams is not guaranteed in the RAW layer.

---

## 🚀 Key Features
- **Multi-Exchange**: Concurrent WebSocket streams for Binance, Bybit, and OKX.
- **Normalization**: Unified event schema for BBO, Trades, Mark Price, Funding, and Open Interest.
- **Reliability**: Non-blocking queue architecture with effective data loss tracking.
- **Storage**: Highly efficient Parquet storage with S3 integration.
- **Alignment**: Post-reconnect RAM-only gap synchronization using REST snapshots.
- **Observability**: Structured JSON logging, 30s heartbeats, and a status API.

---

## 4️⃣ Runtime Architecture
The system is composed of localized, specialized components:
- **WebSocket Handlers**: Independent tasks for Binance, Bybit, and OKX that subscribe and parse streams.
- **Non-Blocking Ingestion Queue**: A central buffer that decouples stream ingestion from storage writing.
- **Writer Loop**: A high-throughput task that buffers events and performs atomic writes to S3/Local storage.
- **Gap Detection**: A read-only analytical thread that monitors `ts_event` continuity.
- **Snapshot Alignment**: A RAM-only mechanism that fetches REST timestamps post-reconnect to synchronize gap tracking without persisting non-WebSocket data.
- **Metrics & State Tracking**: A centralized, observable state object updated in real-time.

---

## 5️⃣ Stability Model
The collector's stability is built on **pressure relief** rather than backpressure.
- **Non-blocking queue**: Handlers drop events if the storage layer cannot keep up, preventing connection saturation.
- **Controlled Drops**: Explicitly measuring data loss is preferred over risking connection stability.
- **Tuned Throughput**: `FLUSH_INTERVAL` is set to 2s to ensure high S3 write concurrency.
- **Baseline**: Post-rollout queue utilization typically remains <20%, with reconnects reduced to zero under normal operations.

---

## 6️⃣ Observability Model
The collector provides explicit, machine-readable visibility into its operation.

### Logs
All logs are emitted as **structured JSON** to STDOUT:
- `collector_start`, `ws_connect`, `gap_detected`, `queue_full_drop`, `state_change`, `heartbeat`.

### Heartbeat
Emitted every **30 seconds**. It is the primary signal for health and load monitoring.

### State Model
- **READY**: Normal operation.
- **DEGRADED**: High queue utilization (>80%), active event drops, or high gap rate.
- **OFFLINE**: No WebSockets connected.
- **ERROR**: Fatal internal exception or writer failure.

---

## 📂 Repository Structure
- `collector/`: Core application logic.
  - `collector.py`: Orchestration and signal handling.
  - `writer.py`: Parquet buffering and S3 upload logic.
  - `state.py`: Runtime metric tracking and state derivation.
  - `status_api.py`: Read-only HTTP status/metrics API.
- `check_raw_sanity.py`: S3 data integrity and schema verification utility.

---

## 🛠 Setup & Usage
1. **Clone & Install**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Configure Environment** (`.env`):
   ```env
   STORAGE_BACKEND=s3
   S3_ENDPOINT=...
   S3_BUCKET=...
   ```
3. **Start Collector**:
   ```bash
   python3 collector/collector.py [--symbols BTCUSDT,ETHUSDT]
   ```

---

## 7️⃣ APIs Exposed (READ-ONLY)
- **GET /status**: Returns derived state, uptime, and last 15m performance metrics.
- **GET /metrics**: Returns detailed internal counters (JSON format).

---

## 8️⃣ Failure & Downtime Handling
When the collector stops or fails, the impact is systematically measured via the `check_raw_sanity.py` utility. Downtime is quantified as an OFFLINE window and documented via gap counts to ensure transparency.

---

## 9️⃣ Explicit Invariants
The following rules MUST NEVER be violated:
- **RAW schema immutability**: Field structure is final.
- **No REST data in RAW**: Only WebSocket messages are persisted.
- **No Alignment persistence**: Alignment events exist in RAM only.
- **No Auto-healing**: The collector reports loss; it never manufactures data to fill it.

---

## 🔒 10️⃣ Lock Statement
QuantLab Collector is complete, stable, observable, and architecturally final.
This component is LOCKED.
Any future work must occur in downstream layers (COMPACT, Replay, ML).
