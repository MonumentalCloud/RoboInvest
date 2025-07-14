"""
AI Risk Monitor for Autonomous Trading System
Implements real-time risk assessment and mitigation using NIST AI RMF principles.
"""

import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum


class RiskLevel(Enum):
    """Risk severity levels."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    MINIMAL = "MINIMAL"


@dataclass
class RiskAssessment:
    """Risk assessment result."""
    overall_risk_score: float
    risk_level: RiskLevel
    financial_risk: float
    bias_risk: float
    security_risk: float
    compliance_risk: float
    recommendations: List[str]
    required_actions: List[str]
    timestamp: datetime


class AIRiskMonitor:
    """AI Risk Monitor implementing NIST AI RMF principles."""
    
    def __init__(self):
        self.risk_thresholds = {
            "financial_exposure_limit": 0.15,  # Max 15% position size
            "confidence_threshold": 0.6,       # Min confidence for trades
            "bias_tolerance": 0.3,             # Max acceptable bias indicators
            "security_alert_threshold": 0.7    # Security threat threshold
        }
        self.risk_history: List[RiskAssessment] = []
        print("AIRiskMonitor | Risk monitoring system initialized")
    
    def assess_trading_decision_risk(self, context: Dict[str, Any]) -> RiskAssessment:
        """Assess comprehensive risk for a trading decision."""
        try:
            # Financial risk assessment
            financial_risk = self._assess_financial_risk(context)
            
            # Bias risk assessment
            bias_risk = self._assess_bias_risk(context)
            
            # Security risk assessment
            security_risk = self._assess_security_risk(context)
            
            # Compliance risk assessment
            compliance_risk = self._assess_compliance_risk(context)
            
            # Calculate overall risk score (weighted average)
            overall_risk_score = (
                financial_risk * 0.4 +
                bias_risk * 0.25 +
                security_risk * 0.25 +
                compliance_risk * 0.1
            )
            
            # Determine risk level
            risk_level = self._score_to_risk_level(overall_risk_score)
            
            # Generate recommendations and actions
            recommendations = self._generate_recommendations(
                financial_risk, bias_risk, security_risk, compliance_risk
            )
            
            required_actions = self._determine_required_actions(overall_risk_score, context)
            
            assessment = RiskAssessment(
                overall_risk_score=overall_risk_score,
                risk_level=risk_level,
                financial_risk=financial_risk,
                bias_risk=bias_risk,
                security_risk=security_risk,
                compliance_risk=compliance_risk,
                recommendations=recommendations,
                required_actions=required_actions,
                timestamp=datetime.now()
            )
            
            # Store assessment
            self.risk_history.append(assessment)
            
            print(f"AIRiskMonitor | Risk assessment complete: {risk_level.value} "
                  f"(score: {overall_risk_score:.3f})")
            
            return assessment
            
        except Exception as e:
            print(f"AIRiskMonitor | Risk assessment error: {e}")
            # Return high-risk assessment on error
            return RiskAssessment(
                overall_risk_score=0.9,
                risk_level=RiskLevel.HIGH,
                financial_risk=0.9,
                bias_risk=0.9,
                security_risk=0.9,
                compliance_risk=0.9,
                recommendations=["Manual review required - assessment error"],
                required_actions=["STOP_TRADING", "HUMAN_REVIEW_REQUIRED"],
                timestamp=datetime.now()
            )
    
    def _assess_financial_risk(self, context: Dict[str, Any]) -> float:
        """Assess financial risk factors."""
        risk_score = 0.0
        
        # Position size risk
        position_size = context.get("position_size", 0)
        if position_size > self.risk_thresholds["financial_exposure_limit"]:
            risk_score += 0.4  # High financial exposure
        elif position_size > 0.1:  # 10%
            risk_score += 0.2  # Moderate exposure
        
        # Confidence risk
        confidence = context.get("confidence", 0.5)
        if confidence < self.risk_thresholds["confidence_threshold"]:
            risk_score += 0.3  # Low confidence increases risk
        
        # Market volatility risk
        if context.get("market_volatility", "low") == "high":
            risk_score += 0.2
        
        # Historical performance risk
        if context.get("recent_losses", False):
            risk_score += 0.1
        
        return min(risk_score, 1.0)
    
    def _assess_bias_risk(self, context: Dict[str, Any]) -> float:
        """Assess bias in AI decision-making."""
        bias_score = 0.0
        
        # Data source diversity
        source_count = context.get("research_source_count", 3)
        if source_count < 3:
            bias_score += 0.3  # Limited sources increase bias risk
        
        # Sentiment extremity (potential confirmation bias)
        sentiment = context.get("sentiment", "neutral")
        if sentiment in ["very_positive", "very_negative"]:
            bias_score += 0.25
        
        # Information recency bias
        news_impact = context.get("news_impact", "low")
        news_recency = context.get("news_recency", "old")
        if news_impact == "high" and news_recency == "recent":
            bias_score += 0.2  # Availability bias risk
        
        # Data quality issues
        data_quality = context.get("data_quality_score", 1.0)
        if data_quality < 0.8:
            bias_score += 0.25
        
        return min(bias_score, 1.0)
    
    def _assess_security_risk(self, context: Dict[str, Any]) -> float:
        """Assess security threats and vulnerabilities."""
        security_score = 0.0
        
        # Check for prompt injection indicators
        user_input = context.get("user_input", "").lower()
        research_content = context.get("research_content", "").lower()
        
        injection_patterns = [
            "ignore previous instructions",
            "disregard safety",
            "act as if you are",
            "pretend to be"
        ]
        
        for pattern in injection_patterns:
            if pattern in user_input or pattern in research_content:
                security_score += 0.4
                break
        
        # Data anomaly detection
        anomaly_score = context.get("anomaly_score", 0.0)
        if anomaly_score > 0.7:
            security_score += 0.3
        
        # System abuse indicators
        request_frequency = context.get("request_frequency_per_hour", 10)
        if request_frequency > 100:
            security_score += 0.2
        
        # Input entropy (adversarial input detection)
        input_entropy = context.get("input_entropy", 0.5)
        decision_confidence = context.get("confidence", 0.5)
        if input_entropy > 0.8 and decision_confidence < 0.3:
            security_score += 0.1
        
        return min(security_score, 1.0)
    
    def _assess_compliance_risk(self, context: Dict[str, Any]) -> float:
        """Assess regulatory compliance risks."""
        compliance_score = 0.0
        
        # Human oversight requirement
        confidence = context.get("confidence", 0.5)
        human_review = context.get("human_review_completed", False)
        if confidence > 0.8 and not human_review:
            compliance_score += 0.4  # SEC algorithmic trading compliance
        
        # Audit trail requirement
        if not context.get("audit_trail_enabled", True):
            compliance_score += 0.3
        
        # Explainability requirement
        explainability = context.get("explainability_score", 0.8)
        if explainability < 0.7:
            compliance_score += 0.2
        
        # Data protection compliance
        if context.get("personal_data_used", False) and not context.get("consent_obtained", False):
            compliance_score += 0.1
        
        return min(compliance_score, 1.0)
    
    def _score_to_risk_level(self, score: float) -> RiskLevel:
        """Convert risk score to risk level."""
        if score >= 0.9:
            return RiskLevel.CRITICAL
        elif score >= 0.7:
            return RiskLevel.HIGH
        elif score >= 0.5:
            return RiskLevel.MEDIUM
        elif score >= 0.3:
            return RiskLevel.LOW
        else:
            return RiskLevel.MINIMAL
    
    def _generate_recommendations(self, financial_risk: float, bias_risk: float, 
                                security_risk: float, compliance_risk: float) -> List[str]:
        """Generate risk mitigation recommendations."""
        recommendations = []
        
        if financial_risk > 0.6:
            recommendations.extend([
                "Reduce position size to limit financial exposure",
                "Implement additional risk controls",
                "Consider paper trading for high-risk strategies"
            ])
        
        if bias_risk > 0.6:
            recommendations.extend([
                "Diversify information sources",
                "Implement bias detection algorithms",
                "Add contradictory evidence analysis"
            ])
        
        if security_risk > 0.6:
            recommendations.extend([
                "Strengthen input validation",
                "Implement anomaly detection",
                "Review access controls and monitoring"
            ])
        
        if compliance_risk > 0.6:
            recommendations.extend([
                "Ensure human oversight for high-confidence decisions",
                "Maintain comprehensive audit trails",
                "Improve AI explainability mechanisms"
            ])
        
        # Always include baseline recommendations
        recommendations.append("Regular risk assessment monitoring")
        
        return recommendations
    
    def _determine_required_actions(self, overall_risk_score: float, context: Dict[str, Any]) -> List[str]:
        """Determine immediate actions required based on risk level."""
        actions = []
        
        if overall_risk_score >= 0.9:
            actions.extend([
                "STOP_TRADING_IMMEDIATELY",
                "ESCALATE_TO_HUMAN_OVERSIGHT",
                "COMPREHENSIVE_REVIEW_REQUIRED"
            ])
        elif overall_risk_score >= 0.7:
            actions.extend([
                "REQUIRE_HUMAN_APPROVAL",
                "REDUCE_POSITION_SIZE_50_PERCENT",
                "ENHANCED_MONITORING"
            ])
        elif overall_risk_score >= 0.5:
            actions.extend([
                "ADDITIONAL_VALIDATION_REQUIRED",
                "MONITOR_CLOSELY"
            ])
        
        # Specific contextual actions
        position_size = context.get("position_size", 0)
        if position_size > self.risk_thresholds["financial_exposure_limit"]:
            actions.append("FORCE_POSITION_SIZE_REDUCTION")
        
        confidence = context.get("confidence", 0.5)
        if confidence < self.risk_thresholds["confidence_threshold"]:
            actions.append("REQUIRE_ADDITIONAL_RESEARCH")
        
        return actions
    
    def check_trading_decision(self, decision_context: Dict[str, Any]) -> Dict[str, Any]:
        """Check if a trading decision meets risk requirements."""
        assessment = self.assess_trading_decision_risk(decision_context)
        
        # Determine if decision should proceed
        should_proceed = assessment.risk_level not in [RiskLevel.CRITICAL, RiskLevel.HIGH]
        
        # Apply risk mitigations
        mitigated_context = self._apply_risk_mitigations(decision_context, assessment)
        
        return {
            "assessment": asdict(assessment),
            "should_proceed": should_proceed,
            "mitigated_context": mitigated_context,
            "risk_summary": {
                "overall_score": assessment.overall_risk_score,
                "level": assessment.risk_level.value,
                "top_risks": self._identify_top_risks(assessment),
                "mitigation_applied": True
            }
        }
    
    def _apply_risk_mitigations(self, context: Dict[str, Any], assessment: RiskAssessment) -> Dict[str, Any]:
        """Apply risk mitigations to decision context."""
        mitigated_context = context.copy()
        
        # Financial risk mitigations
        if assessment.financial_risk > 0.6:
            current_position = mitigated_context.get("position_size", 0)
            mitigated_context["position_size"] = min(current_position * 0.5, 0.1)  # Reduce by 50% or cap at 10%
            mitigated_context["risk_mitigation_applied"] = "position_size_reduced"
        
        # Low confidence mitigation
        if context.get("confidence", 0.5) < self.risk_thresholds["confidence_threshold"]:
            mitigated_context["action"] = "HOLD"  # Force hold for low confidence
            mitigated_context["risk_mitigation_applied"] = "forced_hold_low_confidence"
        
        # High risk level mitigation
        if assessment.risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
            mitigated_context["action"] = "HOLD"
            mitigated_context["position_size"] = 0.0
            mitigated_context["human_review_required"] = True
        
        return mitigated_context
    
    def _identify_top_risks(self, assessment: RiskAssessment) -> List[str]:
        """Identify the top risk factors."""
        risks = [
            ("financial", assessment.financial_risk),
            ("bias", assessment.bias_risk),
            ("security", assessment.security_risk),
            ("compliance", assessment.compliance_risk)
        ]
        
        # Sort by risk score and return top risks
        sorted_risks = sorted(risks, key=lambda x: x[1], reverse=True)
        return [risk[0] for risk in sorted_risks if risk[1] > 0.4]
    
    def get_risk_summary(self) -> Dict[str, Any]:
        """Get current risk monitoring summary."""
        if not self.risk_history:
            return {
                "status": "No assessments completed",
                "recommendations": ["Perform initial risk assessment"]
            }
        
        latest_assessment = self.risk_history[-1]
        recent_assessments = [a for a in self.risk_history 
                            if (datetime.now() - a.timestamp).total_seconds() < 3600]
        
        return {
            "current_risk_level": latest_assessment.risk_level.value,
            "current_risk_score": latest_assessment.overall_risk_score,
            "assessments_last_hour": len(recent_assessments),
            "high_risk_events": len([a for a in recent_assessments 
                                  if a.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]]),
            "top_risk_factors": self._identify_top_risks(latest_assessment),
            "monitoring_status": "active",
            "last_assessment": latest_assessment.timestamp.isoformat()
        }


# Global instance
ai_risk_monitor = AIRiskMonitor()