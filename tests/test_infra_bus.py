import asyncio

import pytest

from src.infra.redis_bus import EventBus


@pytest.mark.asyncio
async def test_eventbus_memory_publish_read():
    bus = EventBus(url=None)
    sid = await bus.publish("idea_stream", {"foo": "bar"})
    assert isinstance(sid, str)

    recent = await bus.read_recent("idea_stream", count=10)
    assert isinstance(recent, list)
    assert recent and recent[0]["foo"] == "bar"
