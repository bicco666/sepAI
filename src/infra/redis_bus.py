from __future__ import annotations

import asyncio
import json
import os
from typing import Any, Dict, List, Tuple


class EventBus:
    def __init__(self, url: str | None = None) -> None:
        self._url = url or os.getenv("REDIS_URL")
        self._redis = None
        # in-memory fallback: stream -> list[(id, data)]
        self._mem: Dict[str, List[Tuple[str, Dict[str, Any]]]] = {}
        self._seq = 0

    async def _ensure(self) -> None:
        if self._redis is not None or not self._url:
            return
        try:
            # Lazy import to avoid hard dep if unused
            import redis.asyncio as redis  # type: ignore

            self._redis = redis.from_url(self._url, decode_responses=True)
            # simple ping to verify
            await self._redis.ping()
        except Exception:
            self._redis = None

    async def publish(self, stream: str, data: Dict[str, Any]) -> str:
        await self._ensure()
        if self._redis is not None:
            # Store as JSON payload
            payload = {"json": json.dumps(data, separators=(",", ":"))}
            return await self._redis.xadd(stream, payload)
        # memory fallback
        self._seq += 1
        sid = f"mem-{self._seq}"
        self._mem.setdefault(stream, []).append((sid, data))
        return sid

    async def read_recent(self, stream: str, count: int = 20) -> List[Dict[str, Any]]:
        await self._ensure()
        if self._redis is not None:
            # XRANGE tail
            entries = await self._redis.xrevrange(stream, count=count)
            out: List[Dict[str, Any]] = []
            for _id, fields in entries:
                try:
                    if isinstance(fields, dict) and "json" in fields:
                        out.append(json.loads(fields["json"]))
                    else:
                        out.append(fields)
                except Exception:
                    continue
            return out
        # memory fallback
        return [e[1] for e in reversed(self._mem.get(stream, []))][:count]

