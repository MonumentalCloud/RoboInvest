"""Global asyncio event queue for the LangGraph workflow.

All producers (price websocket, news streamer, etc.) push dictionaries to
`emit_event`.  The consumer side awaits `get_event` to process the next item.
Each event should at least have a `type` key identifying its nature.
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict

# The queue will be created once the event loop is running to avoid cross-loop issues.
_event_queue: asyncio.Queue[Dict[str, Any]] | None = None


def init_queue() -> None:
    """Create the global event queue bound to the current running loop."""
    global _event_queue
    if _event_queue is None:
        _event_queue = asyncio.Queue()


def emit_event(event: Dict[str, Any]) -> None:
    """Put an event onto the global queue without blocking."""
    if _event_queue is None:
        raise RuntimeError("Event queue not initialized – call init_queue() inside run_forever().")
    _event_queue.put_nowait(event)


async def get_event() -> Dict[str, Any]:
    """Wait for and return the next event from the queue."""
    if _event_queue is None:
        raise RuntimeError("Event queue not initialized – call init_queue() inside run_forever().")
    return await _event_queue.get() 