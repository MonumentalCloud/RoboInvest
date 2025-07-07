# pyright: reportGeneralTypeIssues=false

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction  # type: ignore

from core.config import config
from utils.logger import logger  # type: ignore


class RAGPlaybookAgent:
    """Stores trade memories in a Chroma vector DB using OpenAI embeddings."""

    COLLECTION = "trade_memories"
    RESEARCH_COLLECTION = "research_memories"

    def __init__(self) -> None:
        # Set up embedding function
        if not config.openai_api_key:
            logger.warning("RAG | OpenAI key missing – embeddings disabled; using in-memory fallback")
            self._client = None
            self._mem: List[Dict[str, Any]] = []
            self._research_mem: List[Dict[str, Any]] = []
            return

        embed_fn = OpenAIEmbeddingFunction(api_key=config.openai_api_key, model_name="text-embedding-3-small")
        self._client = chromadb.PersistentClient(path=config.chroma_db_path)
        try:
            self._collection = self._client.get_or_create_collection(  # type: ignore[arg-type]
                self.COLLECTION, embedding_function=embed_fn
            )
            self._research = self._client.get_or_create_collection(  # type: ignore[arg-type]
                self.RESEARCH_COLLECTION, embedding_function=embed_fn
            )
        except Exception as exc:
            logger.error(f"RAG | Chroma error {exc}; falling back to memory")
            self._client = None
            self._mem = []
            self._research_mem = []

    # ------------------------------------------------------------------
    def store_trade(self, trade: Dict[str, Any]) -> None:
        trade_id = (
            f"trade_{len(self._collection.get()['ids'])}"  # type: ignore[index]
            if self._client else f"trade_{len(getattr(self, '_mem', []))}"
        )
        trade = {**trade, "timestamp": datetime.utcnow().isoformat(), "id": trade_id}

        if self._client:
            doc = self._trade_to_text(trade)
            self._collection.add(documents=[doc], metadatas=[trade], ids=[trade_id])
        else:
            self._mem.append(trade)  # type: ignore
        logger.info(f"RAG | stored {trade['symbol']}")

    def retrieve(self, context: Dict[str, Any]) -> Dict[str, Any]:
        if not self._client:
            # return last 5
            recent = getattr(self, "_mem", [])[-5:]  # type: ignore
            return {"similar_trades": recent}

        query = self._context_to_text(context)
        res = self._collection.query(query_texts=[query], n_results=5, include=["metadatas"])
        return {"similar_trades": res.get("metadatas", [[]])[0]}

    # ------------------------------------------------------------------
    @staticmethod
    def _trade_to_text(trade: Dict[str, Any]) -> str:
        return f"{trade.get('action')} {trade.get('symbol')} reasoning: {trade.get('reasoning')} outcome: {trade.get('outcome')}"

    @staticmethod
    def _context_to_text(ctx: Dict[str, Any]) -> str:
        return f"sentiment {ctx.get('sentiment')} top_symbol {ctx.get('symbol')}"

    # ------------------------------------------------------------------
    def store_research(self, memo: Dict[str, Any]) -> None:
        memo_id = f"research_{datetime.utcnow().timestamp()}"
        # Sanitize metadata – Chroma allows only str/int/float/bool, no None
        clean_meta: Dict[str, Any] = {}
        for k, v in memo.items():
            if v is None:
                clean_meta[k] = ""
            elif isinstance(v, (str, int, float, bool)):
                clean_meta[k] = v
            else:
                clean_meta[k] = str(v)

        if self._client:
            doc = clean_meta.get("summary") or str(clean_meta)
            self._research.add(documents=[doc], metadatas=[clean_meta], ids=[memo_id])  # type: ignore[arg-type]
        else:
            self._research_mem.append(clean_meta)  # type: ignore[attr-defined]
        logger.info("RAG | stored research memo")


# singleton instance for easy import
rag_agent = RAGPlaybookAgent() 