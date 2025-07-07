from __future__ import annotations

from typing import Any, Dict

from langgraph.graph import Graph, END, START  # type: ignore

from agents.world_monitor import WorldMonitorAgent
from agents.simple_organic_strategy import SimpleOrganicStrategyAgent
from agents.rag_playbook import RAGPlaybookAgent
from agents.trade_executor import TradeExecutorAgent
from agents.budget_agent import BudgetAgent
from utils.logger import logger  # type: ignore

import asyncio


# Instantiate agents
world_monitor = WorldMonitorAgent()
strategy_agent = SimpleOrganicStrategyAgent()
rag_agent = RAGPlaybookAgent()
executor_agent = TradeExecutorAgent()
budget_agent = BudgetAgent()


def build_graph() -> Graph:
    graph: Graph = Graph()

    # Add nodes
    def observe_sync(_: Dict[str, Any] | None = None) -> Dict[str, Any]:
        return asyncio.run(world_monitor.observe())
    graph.add_node("observe", observe_sync)
    graph.add_node("decide", strategy_agent)
    graph.add_node("execute", executor_agent)
    graph.add_node("budget", budget_agent)

    # Store node (uses lambda)
    def store_node(data: Dict[str, Any]) -> Dict[str, Any]:
        rag_agent.store_trade(data)
        return data

    graph.add_node("store", store_node)

    # Wire edges using constants
    graph.add_edge(START, "observe")
    graph.add_edge("observe", "decide")
    graph.add_edge("decide", "execute")
    graph.add_edge("execute", "budget")
    graph.add_edge("budget", "store")
    graph.add_edge("store", END)

    return graph


def run_once() -> Dict[str, Any]:
    g = build_graph().compile()
    output = g.invoke({})
    logger.info(f"Workflow output: {output}")
    return output


# Event-driven architecture

import asyncio
from typing import Any, Dict

from events import get_event, emit_event, init_queue
from agents.research_planner import ResearchPlannerAgent
from agents.action_executor import ActionExecutorAgent

from utils.logger import logger  # type: ignore


# Instantiate agents
planner = ResearchPlannerAgent()
executor = ActionExecutorAgent()


async def consumer_loop() -> None:
    """Continuously process events from the queue."""
    while True:
        event = await get_event()
        logger.info(f"Consumer got event {event}")

        # Step 1: planner decides task
        task = planner(event)
        # Step 2: executor runs it
        result = executor(task)
        logger.info(f"Task result: {result}")


async def run_forever() -> None:
    """Entry point to launch feeders and consumer."""

    # Initialise the event queue now that the loop is running
    init_queue()

    # Simple ticker to emit a heartbeat event every 5 minutes (placeholder)
    async def heartbeat() -> None:
        while True:
            emit_event({"type": "heartbeat"})
            await asyncio.sleep(300)

    # Start tasks
    tasks = [asyncio.create_task(consumer_loop()), asyncio.create_task(heartbeat())]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(run_forever()) 