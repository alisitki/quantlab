import time
from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class CollectorState:
    start_time: float = field(default_factory=time.time)
    last_event_ts: float = 0
    last_write_ts: float = 0
    total_events: int = 0
    event_counts: Dict[str, int] = field(default_factory=lambda: {"bbo": 0, "trade": 0, "mark_price": 0, "funding": 0, "open_interest": 0})
    writer_stats: Dict[str, Any] = field(default_factory=dict)
    
    # For EPS calculation
    _last_counts: Dict[str, int] = field(default_factory=lambda: {"bbo": 0, "trade": 0, "mark_price": 0, "funding": 0, "open_interest": 0})
    _last_check_time: float = field(default_factory=time.time)
    eps: Dict[str, float] = field(default_factory=lambda: {"bbo": 0.0, "trade": 0.0, "mark_price": 0.0, "funding": 0.0, "open_interest": 0.0})

    def update_event(self, stream_type: str):
        self.last_event_ts = time.time() * 1000
        self.total_events += 1
        if stream_type in self.event_counts:
            self.event_counts[stream_type] += 1
        
        # Periodic EPS update
        now = time.time()
        elapsed = now - self._last_check_time
        if elapsed >= 10:
            for s in self.eps:
                delta = self.event_counts[s] - self._last_counts[s]
                self.eps[s] = round(delta / elapsed, 1)
                self._last_counts[s] = self.event_counts[s]
            self._last_check_time = now
