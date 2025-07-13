from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
import json

from core.openai_manager import openai_manager
from core.structured_order import StructuredOrder, RiskLevel
from agents.risk_assessor import RiskAssessorAgent
from core.central_event_bus import central_event_bus, EventType, EventPriority, create_event
from core.notification_aggregator import notification_aggregator
from utils.logger import logger


class ApprovalDecision(Enum):
    """Trade approval decisions"""
    AUTO_APPROVE = "auto_approve"
    AUTO_REJECT = "auto_reject"
    REQUEST_PERMISSION = "request_permission"


class RiskRewardProfile(Enum):
    """Risk-reward profiles"""
    LOW_RISK_LOW_REWARD = "low_risk_low_reward"
    LOW_RISK_HIGH_REWARD = "low_risk_high_reward"
    HIGH_RISK_LOW_REWARD = "high_risk_low_reward"
    HIGH_RISK_HIGH_REWARD = "high_risk_high_reward"


@dataclass
class ApprovalAnalysis:
    """Analysis result for trade approval"""
    decision: ApprovalDecision
    risk_reward_profile: RiskRewardProfile
    confidence_score: float
    risk_score: float
    reward_potential: float
    reasoning: str
    risk_assessment_history: List[Dict[str, Any]]
    similar_trades_performance: List[Dict[str, Any]]
    approval_thresholds: Dict[str, Any]
    requires_email: bool = False
    email_subject: Optional[str] = None
    email_body: Optional[str] = None


class TradeApprovalAgent:
    """Intelligent agent that filters alpha opportunities based on risk assessment history"""
    
    def __init__(self):
        self.risk_assessor = RiskAssessorAgent()
        
        # Approval thresholds (configurable)
        self.thresholds = {
            # Risk thresholds
            "max_acceptable_risk": 0.7,  # 70% max risk
            "high_risk_threshold": 0.5,  # 50% considered high risk
            "extreme_risk_threshold": 0.8,  # 80% considered extreme risk
            
            # Reward thresholds
            "min_reward_potential": 0.15,  # 15% minimum reward potential
            "high_reward_threshold": 0.25,  # 25% considered high reward
            "exceptional_reward_threshold": 0.4,  # 40% considered exceptional
            
            # Confidence thresholds
            "min_confidence": 0.6,  # 60% minimum confidence
            "high_confidence_threshold": 0.8,  # 80% high confidence
            
            # Historical performance thresholds
            "min_win_rate": 0.55,  # 55% minimum win rate for similar trades
            "min_avg_return": 0.05,  # 5% minimum average return
            
            # Position size thresholds
            "max_position_size": 100,  # Maximum shares
            "large_position_threshold": 50,  # Large position threshold
        }
        
        # Decision history for learning
        self.decision_history: List[Dict[str, Any]] = []
        
    async def analyze_trade_for_approval(self, 
                                       structured_order: StructuredOrder,
                                       market_data: Dict[str, Any],
                                       alpha_insights: Dict[str, Any]) -> ApprovalAnalysis:
        """Analyze a trade and determine approval decision"""
        
        logger.info(f"🔍 Analyzing trade {structured_order.order_id} for approval")
        
        # Step 1: Get comprehensive risk assessment
        risk_assessment = await self._get_comprehensive_risk_assessment(
            structured_order, market_data, alpha_insights
        )
        
        # Step 2: Analyze risk-reward profile
        risk_reward_profile = self._analyze_risk_reward_profile(
            structured_order, risk_assessment
        )
        
        # Step 3: Get historical performance data
        historical_data = await self._get_historical_performance_data(
            structured_order, risk_assessment
        )
        
        # Step 4: Calculate reward potential
        reward_potential = self._calculate_reward_potential(
            structured_order, alpha_insights, market_data
        )
        
        # Step 5: Make approval decision
        decision, reasoning = self._make_approval_decision(
            structured_order, risk_assessment, risk_reward_profile, 
            historical_data, reward_potential
        )
        
        # Step 6: Generate email if permission needed
        email_subject, email_body = None, None
        if decision == ApprovalDecision.REQUEST_PERMISSION:
            email_subject, email_body = self._generate_approval_email(
                structured_order, risk_assessment, alpha_insights, 
                risk_reward_profile, reward_potential
            )
        
        # Step 7: Log decision
        await self._log_approval_decision(
            structured_order, decision, risk_assessment, 
            risk_reward_profile, reward_potential, reasoning
        )
        
        return ApprovalAnalysis(
            decision=decision,
            risk_reward_profile=risk_reward_profile,
            confidence_score=structured_order.confidence_score,
            risk_score=risk_assessment.get("overall_risk_score", 0.5),
            reward_potential=reward_potential,
            reasoning=reasoning,
            risk_assessment_history=historical_data.get("risk_history", []),
            similar_trades_performance=historical_data.get("similar_trades", []),
            approval_thresholds=self.thresholds,
            requires_email=decision == ApprovalDecision.REQUEST_PERMISSION,
            email_subject=email_subject,
            email_body=email_body
        )
    
    async def _get_comprehensive_risk_assessment(self, 
                                               structured_order: StructuredOrder,
                                               market_data: Dict[str, Any],
                                               alpha_insights: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive risk assessment using the risk assessor agent"""
        
        # Prepare data for risk assessment
        risk_data = {
            "symbol": structured_order.symbol,
            "side": structured_order.side,
            "quantity": structured_order.quantity,
            "order_type": structured_order.order_type.value,
            "market_data": market_data,
            "alpha_insights": alpha_insights,
            "play_details": structured_order.play.to_dict(),
            "stop_conditions": structured_order.stop_conditions.to_dict(),
            "confidence_score": structured_order.confidence_score,
            "priority": structured_order.priority
        }
        
        # Get risk assessment from the risk assessor agent
        risk_assessment = self.risk_assessor.assess_risk(
            symbol=risk_data["symbol"],
            quantity=risk_data["quantity"],
            current_price=risk_data["market_data"].get("price", 0),
            market_data=risk_data["market_data"],
            historical_data=risk_data["market_data"].get("historical_data"),
            sector_data=risk_data.get("sector_data"),
            market_context=risk_data.get("market_context")
        )
        
        # Enhance with structured order's risk assessment
        enhanced_assessment = {
            "risk_assessment": risk_assessment,
            "structured_order_risk": {
                "risk_level": structured_order.risk_assessment.risk_level.value,
                "overall_risk_score": structured_order.risk_assessment.overall_risk_score,
                "max_loss_amount": structured_order.risk_assessment.max_loss_amount,
                "max_loss_percentage": structured_order.risk_assessment.max_loss_percentage,
                "var_95": structured_order.risk_assessment.var_95,
                "volatility": structured_order.risk_assessment.volatility,
                "liquidity_risk": structured_order.risk_assessment.liquidity_risk,
                "market_timing_risk": structured_order.risk_assessment.market_timing_risk
            },
            "swot_analysis": structured_order.swot_analysis.to_dict(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return enhanced_assessment
    
    def _analyze_risk_reward_profile(self, 
                                   structured_order: StructuredOrder,
                                   risk_assessment: Dict[str, Any]) -> RiskRewardProfile:
        """Analyze the risk-reward profile of the trade"""
        
        risk_score = risk_assessment.get("overall_risk_score", 0.5)
        swot_score = structured_order.swot_analysis.overall_score
        
        # Determine risk level
        if risk_score <= self.thresholds["high_risk_threshold"]:
            risk_level = "low"
        elif risk_score <= self.thresholds["extreme_risk_threshold"]:
            risk_level = "high"
        else:
            risk_level = "extreme"
        
        # Determine reward potential (based on SWOT score and confidence)
        confidence = structured_order.confidence_score
        reward_potential = (swot_score + confidence) / 2
        
        if reward_potential >= self.thresholds["high_reward_threshold"]:
            reward_level = "high"
        elif reward_potential >= self.thresholds["min_reward_potential"]:
            reward_level = "medium"
        else:
            reward_level = "low"
        
        # Map to risk-reward profile
        if risk_level == "low" and reward_level == "low":
            return RiskRewardProfile.LOW_RISK_LOW_REWARD
        elif risk_level == "low" and reward_level in ["medium", "high"]:
            return RiskRewardProfile.LOW_RISK_HIGH_REWARD
        elif risk_level in ["high", "extreme"] and reward_level == "low":
            return RiskRewardProfile.HIGH_RISK_LOW_REWARD
        else:  # high/extreme risk + medium/high reward
            return RiskRewardProfile.HIGH_RISK_HIGH_REWARD
    
    async def _get_historical_performance_data(self, 
                                             structured_order: StructuredOrder,
                                             risk_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Get historical performance data for similar trades"""
        
        # Get recent risk assessments for this symbol
        recent_events = central_event_bus.get_events_from_db(
            limit=50,
            event_types=['risk_assessment', 'trade_executed', 'trade_result']
        )
        
        risk_history = []
        similar_trades = []
        
        for event in recent_events:
            event_data = event.get('data') or event.get('metadata', {})
            
            # Collect risk assessments
            if event.get('event_type') == 'risk_assessment' and event_data.get('symbol') == structured_order.symbol:
                risk_history.append({
                    'timestamp': event.get('timestamp'),
                    'risk_score': event_data.get('overall_risk_score'),
                    'risk_level': event_data.get('risk_level'),
                    'outcome': event_data.get('outcome')
                })
            
            # Collect similar trades
            if event.get('event_type') in ['trade_executed', 'trade_result']:
                if (event_data.get('symbol') == structured_order.symbol and 
                    event_data.get('side') == structured_order.side):
                    similar_trades.append({
                        'timestamp': event.get('timestamp'),
                        'quantity': event_data.get('quantity'),
                        'confidence': event_data.get('confidence_score'),
                        'pnl': event_data.get('realized_pnl'),
                        'risk_score': event_data.get('risk_score'),
                        'success': event_data.get('pnl', 0) > 0
                    })
        
        # Calculate performance metrics
        if similar_trades:
            win_rate = sum(1 for trade in similar_trades if trade['success']) / len(similar_trades)
            avg_return = sum(trade.get('pnl', 0) for trade in similar_trades) / len(similar_trades)
        else:
            win_rate = 0.5  # Default to 50%
            avg_return = 0.0
        
        return {
            'risk_history': risk_history[-10:],  # Last 10 risk assessments
            'similar_trades': similar_trades[-20:],  # Last 20 similar trades
            'win_rate': win_rate,
            'avg_return': avg_return,
            'total_similar_trades': len(similar_trades)
        }
    
    def _calculate_reward_potential(self, 
                                  structured_order: StructuredOrder,
                                  alpha_insights: Dict[str, Any],
                                  market_data: Dict[str, Any]) -> float:
        """Calculate the potential reward for the trade"""
        
        # Base reward from SWOT analysis
        base_reward = structured_order.swot_analysis.overall_score
        
        # Alpha insights boost
        alpha_confidence = alpha_insights.get('confidence', 0.5)
        alpha_strength = alpha_insights.get('strength', 0.5)
        
        # Market conditions factor
        market_volatility = market_data.get('volatility', 0.2)
        market_trend = market_data.get('trend', 'neutral')
        
        # Calculate reward potential
        reward_potential = (
            base_reward * 0.4 +  # SWOT analysis
            alpha_confidence * 0.3 +  # Alpha confidence
            alpha_strength * 0.2 +  # Alpha strength
            (0.1 if market_trend == 'favorable' else 0.0)  # Market trend
        )
        
        # Adjust for volatility (higher volatility can mean higher potential)
        if market_volatility > 0.3:
            reward_potential *= 1.2  # 20% boost for high volatility
        
        return min(reward_potential, 1.0)  # Cap at 100%
    
    def _make_approval_decision(self, 
                              structured_order: StructuredOrder,
                              risk_assessment: Dict[str, Any],
                              risk_reward_profile: RiskRewardProfile,
                              historical_data: Dict[str, Any],
                              reward_potential: float) -> Tuple[ApprovalDecision, str]:
        """Make the final approval decision"""
        
        risk_score = risk_assessment.get("overall_risk_score", 0.5)
        confidence = structured_order.confidence_score
        win_rate = historical_data.get('win_rate', 0.5)
        avg_return = historical_data.get('avg_return', 0.0)
        
        # Auto-reject conditions
        if (risk_score > self.thresholds["max_acceptable_risk"] or
            confidence < self.thresholds["min_confidence"] or
            reward_potential < self.thresholds["min_reward_potential"] or
            (risk_reward_profile == RiskRewardProfile.HIGH_RISK_LOW_REWARD) or
            (win_rate < self.thresholds["min_win_rate"] and risk_score > 0.6)):
            
            reasoning = f"Auto-rejected: Risk={risk_score:.2f}, Confidence={confidence:.2f}, Reward={reward_potential:.2f}, Profile={risk_reward_profile.value}"
            return ApprovalDecision.AUTO_REJECT, reasoning
        
        # Auto-approve conditions
        if (risk_score <= self.thresholds["high_risk_threshold"] and
            confidence >= self.thresholds["high_confidence_threshold"] and
            reward_potential >= self.thresholds["min_reward_potential"] and
            win_rate >= self.thresholds["min_win_rate"]):
            
            reasoning = f"Auto-approved: Low risk ({risk_score:.2f}), High confidence ({confidence:.2f}), Good reward ({reward_potential:.2f})"
            return ApprovalDecision.AUTO_APPROVE, reasoning
        
        # Request permission for high risk + high reward scenarios
        if (risk_reward_profile == RiskRewardProfile.HIGH_RISK_HIGH_REWARD and
            reward_potential >= self.thresholds["high_reward_threshold"]):
            
            reasoning = f"Permission requested: High risk ({risk_score:.2f}) but high reward potential ({reward_potential:.2f})"
            return ApprovalDecision.REQUEST_PERMISSION, reasoning
        
        # Default to auto-reject for unclear cases
        reasoning = f"Auto-rejected: Unclear risk-reward profile ({risk_reward_profile.value})"
        return ApprovalDecision.AUTO_REJECT, reasoning
    
    def _generate_approval_email(self, 
                               structured_order: StructuredOrder,
                               risk_assessment: Dict[str, Any],
                               alpha_insights: Dict[str, Any],
                               risk_reward_profile: RiskRewardProfile,
                               reward_potential: float) -> Tuple[str, str]:
        """Generate approval email for high-risk, high-reward trades"""
        
        subject = f"🚀 RoboInvest Trade Approval Request: {structured_order.symbol} {structured_order.side.upper()}"
        
        body = f"""
🚀 RoboInvest Trade Approval Request

TRADE DETAILS:
Symbol: {structured_order.symbol}
Side: {structured_order.side.upper()}
Quantity: {structured_order.quantity} shares
Order ID: {structured_order.order_id}
Confidence Score: {structured_order.confidence_score:.2f}

PLAY INFORMATION:
Title: {structured_order.play.title}
Description: {structured_order.play.description}
Thesis: {structured_order.play.thesis}
Timeframe: {structured_order.play.timeframe}

RISK ASSESSMENT:
Overall Risk Score: {risk_assessment.get('overall_risk_score', 0):.2f}
Risk Level: {structured_order.risk_assessment.risk_level.value.upper()}
Max Loss Amount: ${structured_order.risk_assessment.max_loss_amount:.2f}
Max Loss Percentage: {structured_order.risk_assessment.max_loss_percentage:.1f}%
Value at Risk (95%): ${structured_order.risk_assessment.var_95:.2f}

REWARD ANALYSIS:
Reward Potential: {reward_potential:.1%}
Risk-Reward Profile: {risk_reward_profile.value.replace('_', ' ').title()}
SWOT Overall Score: {structured_order.swot_analysis.overall_score:.2f}

ALPHA INSIGHTS:
{json.dumps(alpha_insights, indent=2)}

STOP CONDITIONS:
Stop Loss: {structured_order.stop_conditions.stop_loss_percentage:.1f}%
Take Profit: {structured_order.stop_conditions.take_profit_percentage:.1f}%
Trailing Stop: {structured_order.stop_conditions.trailing_stop_percentage or 'None'}%

HISTORICAL PERFORMANCE:
Similar Trades Win Rate: {risk_assessment.get('historical_win_rate', 'N/A')}
Average Return: {risk_assessment.get('historical_avg_return', 'N/A')}

STRENGTHS:
{chr(10).join(f"• {strength}" for strength in structured_order.swot_analysis.strengths)}

WEAKNESSES:
{chr(10).join(f"• {weakness}" for weakness in structured_order.swot_analysis.weaknesses)}

OPPORTUNITIES:
{chr(10).join(f"• {opportunity}" for opportunity in structured_order.swot_analysis.opportunities)}

THREATS:
{chr(10).join(f"• {threat}" for threat in structured_order.swot_analysis.threats)}

DECISION REQUIRED:
This trade has been identified as HIGH RISK but with HIGH REWARD POTENTIAL.
Your approval is required before execution.

TO APPROVE: Reply with "APPROVE {structured_order.order_id}"
TO REJECT: Reply with "REJECT {structured_order.order_id}"

This approval request will expire in 2 hours.
"""
        
        return subject, body
    
    async def _log_approval_decision(self, 
                                   structured_order: StructuredOrder,
                                   decision: ApprovalDecision,
                                   risk_assessment: Dict[str, Any],
                                   risk_reward_profile: RiskRewardProfile,
                                   reward_potential: float,
                                   reasoning: str):
        """Log the approval decision for future learning"""
        
        decision_record = {
            'order_id': structured_order.order_id,
            'symbol': structured_order.symbol,
            'side': structured_order.side,
            'decision': decision.value,
            'risk_reward_profile': risk_reward_profile.value,
            'risk_score': risk_assessment.get('overall_risk_score', 0.5),
            'confidence_score': structured_order.confidence_score,
            'reward_potential': reward_potential,
            'reasoning': reasoning,
            'timestamp': datetime.utcnow().isoformat(),
            'play_title': structured_order.play.title
        }
        
        self.decision_history.append(decision_record)
        
        # Emit event to central event bus
        central_event_bus.emit_event(
            create_event(
                event_type=EventType.META_AGENT,
                source="trade_approval_agent",
                title=f"Trade Approval Decision: {decision.value.upper()}",
                message=f"{structured_order.symbol} {structured_order.side.upper()} - {reasoning}",
                priority=EventPriority.HIGH if decision == ApprovalDecision.REQUEST_PERMISSION else EventPriority.MEDIUM,
                metadata=decision_record
            )
        )
        
        logger.info(f"📋 Trade approval decision logged: {decision.value} for {structured_order.order_id}")
    
    async def send_approval_email(self, analysis: ApprovalAnalysis, order_id: str) -> bool:
        """Send approval email if permission is required"""
        
        if not analysis.requires_email or not analysis.email_subject or not analysis.email_body:
            return False
        
        try:
            # Send via notification aggregator
            notification_aggregator.add_alert(
                alert_type="trade_approval_request",
                message=analysis.email_subject,
                context={
                    "email_body": analysis.email_body,
                    "analysis": analysis.__dict__,
                    "approval_url": f"http://localhost:8081/api/trade-approval/approve/{order_id}",
                    "reject_url": f"http://localhost:8081/api/trade-approval/reject/{order_id}"
                }
            )
            
            logger.info(f"📧 Approval email sent for trade {order_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending approval email: {e}")
            return False
    
    def get_approval_statistics(self) -> Dict[str, Any]:
        """Get statistics about approval decisions"""
        
        if not self.decision_history:
            return {"total_decisions": 0}
        
        total = len(self.decision_history)
        decisions = [d['decision'] for d in self.decision_history]
        
        return {
            "total_decisions": total,
            "auto_approve_count": decisions.count("auto_approve"),
            "auto_reject_count": decisions.count("auto_reject"),
            "permission_requested_count": decisions.count("request_permission"),
            "auto_approve_rate": decisions.count("auto_approve") / total,
            "auto_reject_rate": decisions.count("auto_reject") / total,
            "permission_request_rate": decisions.count("request_permission") / total,
            "recent_decisions": self.decision_history[-10:]  # Last 10 decisions
        }


# Global instance
trade_approval_agent = TradeApprovalAgent() 