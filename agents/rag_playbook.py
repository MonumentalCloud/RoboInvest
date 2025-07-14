# pyright: reportGeneralTypeIssues=false

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, cast

import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction  # type: ignore

from core.config import config
from core.openai_manager import openai_manager
from utils.logger import logger  # type: ignore


class RAGPlaybookAgent:
    """AI-powered RAG agent that stores and analyzes trade memories using OpenAI embeddings and LLM reasoning."""

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

        # AI-powered trade analysis
        enhanced_trade = self._analyze_trade_for_storage(trade)

        if self._client:
            doc = self._trade_to_text(enhanced_trade)
            self._collection.add(documents=[doc], metadatas=[enhanced_trade], ids=[trade_id])
        else:
            self._mem.append(enhanced_trade)  # type: ignore
        logger.info(f"RAG | stored {trade['symbol']} with AI analysis")

    def retrieve(self, context: Dict[str, Any]) -> Dict[str, Any]:
        if not self._client:
            # return last 5
            recent = getattr(self, "_mem", [])[-5:]  # type: ignore
            return {"similar_trades": recent}

        query = self._context_to_text(context)
        res = self._collection.query(query_texts=[query], n_results=5, include=["metadatas"])
        similar_trades_raw = res.get("metadatas", [[]])[0]
        
        # Convert to proper type
        similar_trades = cast(List[Dict[str, Any]], similar_trades_raw)
        
        # AI-powered memory synthesis
        synthesis = self._synthesize_memories(similar_trades, context)
        
        return {
            "similar_trades": similar_trades,
            "ai_synthesis": synthesis
        }

    def _analyze_trade_for_storage(self, trade: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to analyze and enhance trade data before storage."""
        try:
            prompt = f"""Analyze this trade for enhanced storage and future retrieval:

Trade: {trade}

Provide enhanced analysis in JSON format:
{{
    "key_lessons": ["list", "of", "key", "lessons"],
    "success_factors": ["list", "of", "success", "factors"],
    "risk_indicators": ["list", "of", "risk", "indicators"],
    "market_conditions": "market conditions during trade",
    "strategy_effectiveness": "high/medium/low",
    "similar_patterns": ["list", "of", "similar", "patterns"],
    "improvement_suggestions": ["list", "of", "suggestions"],
    "confidence_score": 0.0-1.0
}}"""

            response = openai_manager.chat_completion([
                {"role": "system", "content": "You are a trade analysis expert. Be thorough and objective."},
                {"role": "user", "content": prompt}
            ], temperature=0.2)

            try:
                import json
                analysis = json.loads(response["content"] or "{}")
                return {**trade, "ai_analysis": analysis}
            except Exception as parse_exc:
                logger.warning(f"Trade analysis failed: {parse_exc}")
                return trade

        except Exception as e:
            logger.warning(f"Trade analysis failed: {e}")
            return trade

    def _synthesize_memories(self, similar_trades: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to synthesize retrieved memories into actionable insights."""
        try:
            if not similar_trades:
                return {"insights": [], "patterns": [], "recommendations": []}

            prompt = f"""Synthesize these similar trades into actionable insights:

Similar Trades: {similar_trades}
Current Context: {context}

Provide synthesis in JSON format:
{{
    "key_patterns": ["list", "of", "patterns"],
    "success_strategies": ["list", "of", "strategies"],
    "risk_warnings": ["list", "of", "warnings"],
    "market_insights": ["list", "of", "insights"],
    "recommended_actions": ["list", "of", "actions"],
    "confidence_level": "high/medium/low",
    "applicability_score": 0.0-1.0
}}"""

            response = openai_manager.chat_completion([
                {"role": "system", "content": "You are a memory synthesis expert. Extract actionable insights from historical data."},
                {"role": "user", "content": prompt}
            ], temperature=0.3)

            try:
                import json
                synthesis = json.loads(response["content"] or "{}")
                return synthesis
            except Exception as parse_exc:
                logger.warning(f"Memory synthesis failed: {parse_exc}")
                return {"insights": [], "patterns": [], "recommendations": []}

        except Exception as e:
            logger.warning(f"Memory synthesis failed: {e}")
            return {"insights": [], "patterns": [], "recommendations": []}

    # ------------------------------------------------------------------
    @staticmethod
    def _trade_to_text(trade: Dict[str, Any]) -> str:
        base_text = f"{trade.get('action')} {trade.get('symbol')} reasoning: {trade.get('reasoning')} outcome: {trade.get('outcome')}"
        
        # Include AI analysis if available
        if "ai_analysis" in trade:
            ai_analysis = trade["ai_analysis"]
            base_text += f" lessons: {ai_analysis.get('key_lessons', [])} success_factors: {ai_analysis.get('success_factors', [])}"
        
        return base_text

    @staticmethod
    def _context_to_text(ctx: Dict[str, Any]) -> str:
        return f"sentiment {ctx.get('sentiment')} top_symbol {ctx.get('symbol')}"

    # ------------------------------------------------------------------
    def store_research(self, memo: Dict[str, Any]) -> None:
        memo_id = f"research_{datetime.utcnow().timestamp()}"
        
        # AI-powered research analysis
        enhanced_memo = self._analyze_research_for_storage(memo)
        
        # Sanitize metadata – Chroma allows only str/int/float/bool, no None
        clean_meta: Dict[str, Any] = {}
        for k, v in enhanced_memo.items():
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
        logger.info("RAG | stored research memo with AI analysis")

    def _analyze_research_for_storage(self, memo: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to analyze and enhance research data before storage."""
        try:
            prompt = f"""Analyze this research memo for enhanced storage and future retrieval:

Research Memo: {memo}

Provide enhanced analysis in JSON format:
{{
    "key_findings": ["list", "of", "key", "findings"],
    "trading_implications": ["list", "of", "implications"],
    "confidence_level": "high/medium/low",
    "time_relevance": "short/medium/long",
    "risk_factors": ["list", "of", "risks"],
    "opportunity_signals": ["list", "of", "signals"],
    "follow_up_actions": ["list", "of", "actions"],
    "quality_score": 0.0-1.0
}}"""

            response = openai_manager.chat_completion([
                {"role": "system", "content": "You are a research analysis expert. Be thorough and objective."},
                {"role": "user", "content": prompt}
            ], temperature=0.2)

            try:
                import json
                analysis = json.loads(response["content"] or "{}")
                return {**memo, "ai_analysis": analysis}
            except Exception as parse_exc:
                logger.warning(f"Research analysis failed: {parse_exc}")
                return memo

        except Exception as e:
            logger.warning(f"Research analysis failed: {e}")
            return memo


# singleton instance for easy import
rag_agent = RAGPlaybookAgent() 