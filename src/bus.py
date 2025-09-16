from __future__ import annotations

import os
from src.infra.redis_bus import EventBus


REDIS_URL = os.getenv("REDIS_URL")
bus = EventBus(REDIS_URL)

