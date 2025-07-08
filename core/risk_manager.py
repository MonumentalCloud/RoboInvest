"""
Comprehensive Risk Management System for Autonomous Trading AI
Implements multiple risk frameworks (NIST AI RMF, FAIR, ISO 31000) with real-time monitoring.
"""

import json
import time
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
import re

from utils.logger import logger

from core.config import config
from core.openai_manager import openai_manager


class RiskLevel(Enum):
    """Risk severity levels aligned with NIST AI RMF."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    MINIMAL = "MINIMAL"


class RiskCategory(Enum):
    """AI risk categories from comprehensive taxonomy."""
    TECHNICAL = "TECHNICAL"
    ETHICAL_BIAS = "ETHICAL_BIAS"
    OPERATIONAL = "OPERATIONAL"
    LEGAL_COMPLIANCE = "LEGAL_COMPLIANCE"
    SECURITY = "SECURITY"
    FINANCIAL = "FINANCIAL"
    REPUTATIONAL = "REPUTATIONAL"
    SYSTEMIC = "SYSTEMIC"


@dataclass
class RiskEvent:
    """Risk event structure following NIST AI RMF."""
    event_id: str
    timestamp: datetime
    category: RiskCategory
    level: RiskLevel
    description: str
    source: str
    context: Dict[str, Any]
    impact_score: float  # 0-1 scale
    likelihood: float   # 0-1 scale
    risk_score: float   # impact * likelihood
    mitigation_applied: bool = False
    mitigation_actions: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.mitigation_actions is None:
            self.mitigation_actions = []


@dataclass
class BiasAssessment:
    """Bias assessment results."""
    bias_detected: bool
    bias_types: List[str]
    confidence_score: float
    affected_groups: List[str]
    mitigation_required: bool
    assessment_details: Dict[str, Any]


@dataclass
class SecurityThreat:
    """Security threat assessment."""
    threat_type: str
    severity: RiskLevel
    attack_vector: str
    confidence: float
    indicators: List[str]
    recommended_actions: List[str]


class RiskAssessmentFramework:
    """Implements NIST AI RMF core functions: Govern, Map, Measure, Manage."""
    
    def __init__(self):
        self.risk_events: List[RiskEvent] = []
        self.risk_thresholds = {
            RiskLevel.CRITICAL: 0.9,
            RiskLevel.HIGH: 0.7,
            RiskLevel.MEDIUM: 0.5,
            RiskLevel.LOW: 0.3,
            RiskLevel.MINIMAL: 0.1
        }
        self.governance_policies = self._initialize_governance()
        self.monitoring_active = False
        
    def _initialize_governance(self) -> Dict[str, Any]:
        """Initialize AI governance policies (NIST AI RMF Govern function)."""
        return {
            "ai_principles": [
                "Fairness and Non-discrimination",
                "Transparency and Explainability", 
                "Accountability and Human Oversight",
                "Robustness and Safety",
                "Privacy and Data Protection"
            ],
            "risk_tolerance": {
                "financial_exposure_limit": 0.15,  # Max 15% position size
                "confidence_threshold": 0.6,        # Min confidence for trades
                "bias_tolerance": 0.2,              # Max acceptable bias score
                "security_breach_tolerance": 0.0    # Zero tolerance for security
            },
            "oversight_requirements": {
                "human_review_threshold": 0.8,      # High-risk decisions need review
                "audit_frequency_days": 7,          # Weekly risk audits
                "incident_reporting_required": True
            },
            "compliance_frameworks": ["NIST AI RMF", "ISO 31000", "GDPR", "SOX"]
        }
    
    def map_ai_risks(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Map AI risks in context (NIST AI RMF Map function)."""
        try:
            risk_mapping = {
                "system_context": {
                    "ai_type": "Autonomous Trading Agent",
                    "deployment_context": "Financial Markets",
                    "stakeholders": ["Traders", "Investors", "Regulators", "Market"],
                    "high_risk_domains": ["Financial Decisions", "Autonomous Actions"]
                },
                "identified_risks": self._identify_context_risks(context),
                "risk_factors": self._assess_risk_factors(context),
                "dependencies": self._map_dependencies(context),
                "regulatory_considerations": self._check_regulatory_requirements(context)
            }
            
            logger.info(f"RiskManager | Mapped {len(risk_mapping['identified_risks'])} risks in current context")
            return risk_mapping
            
        except Exception as e:
            logger.error(f"Risk mapping error: {e}")
            return {"error": str(e)}
    
    def _identify_context_risks(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify risks specific to current context."""
        risks = []
        
        # Financial exposure risk
        position_size = context.get("position_size", 0)
        if position_size > self.governance_policies["risk_tolerance"]["financial_exposure_limit"]:
            risks.append({
                "type": "FINANCIAL_OVEREXPOSURE",
                "description": f"Position size {position_size:.1%} exceeds limit",
                "severity": RiskLevel.HIGH.value,
                "immediate_action_required": True
            })
        
        # Confidence risk
        confidence = context.get("confidence", 0)
        if confidence < self.governance_policies["risk_tolerance"]["confidence_threshold"]:
            risks.append({
                "type": "LOW_CONFIDENCE_DECISION",
                "description": f"Decision confidence {confidence:.2f} below threshold",
                "severity": RiskLevel.MEDIUM.value,
                "recommendation": "Increase research or reduce position size"
            })
        
        # Market volatility risk
        if context.get("market_volatility", "unknown") == "high":
            risks.append({
                "type": "HIGH_MARKET_VOLATILITY",
                "description": "Operating in high volatility environment",
                "severity": RiskLevel.MEDIUM.value,
                "mitigation": "Enhanced risk controls recommended"
            })
        
        # AI model risk
        if context.get("model_uncertainty", False):
            risks.append({
                "type": "AI_MODEL_UNCERTAINTY",
                "description": "AI model showing uncertainty in predictions",
                "severity": RiskLevel.MEDIUM.value,
                "action": "Consider human oversight"
            })
        
        return risks
    
    def _assess_risk_factors(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Assess quantitative risk factors."""
        return {
            "financial_risk_score": min(context.get("position_size", 0) * 2, 1.0),
            "confidence_risk_score": 1.0 - context.get("confidence", 0.5),
            "market_risk_score": 0.7 if context.get("market_volatility") == "high" else 0.3,
            "operational_risk_score": 0.2,  # Base operational risk
            "aggregate_risk_score": self._calculate_aggregate_risk(context)
        }
    
    def _calculate_aggregate_risk(self, context: Dict[str, Any]) -> float:
        """Calculate aggregate risk score using weighted factors."""
        factors = {
            "financial": context.get("position_size", 0) * 0.4,
            "confidence": (1.0 - context.get("confidence", 0.5)) * 0.3,
            "market": 0.7 if context.get("market_volatility") == "high" else 0.2,
            "operational": 0.1
        }
        return min(sum(factors.values()), 1.0)
    
    def _map_dependencies(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Map system dependencies and their risks."""
        return {
            "external_dependencies": [
                {"service": "OpenAI API", "risk": "Service unavailable", "criticality": "HIGH"},
                {"service": "Market Data", "risk": "Stale/incorrect data", "criticality": "HIGH"},
                {"service": "Web Research", "risk": "Misinformation", "criticality": "MEDIUM"}
            ],
            "internal_dependencies": [
                {"component": "PnL Tracker", "risk": "Calculation errors", "criticality": "MEDIUM"},
                {"component": "Data Fetcher", "risk": "API limits", "criticality": "LOW"}
            ],
            "data_dependencies": {
                "training_data_quality": "Unknown - using pre-trained models",
                "real_time_data_freshness": context.get("data_freshness", "unknown"),
                "data_bias_potential": "Medium - financial data biases possible"
            }
        }
    
    def _check_regulatory_requirements(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check regulatory compliance requirements."""
        return {
            "applicable_regulations": [
                "SEC Algorithmic Trading Rules",
                "GDPR (if processing EU data)",
                "SOX (if public company)",
                "CFTC (if derivatives trading)"
            ],
            "compliance_status": {
                "human_oversight": "Required for high-risk decisions",
                "audit_trail": "Enabled",
                "risk_disclosures": "Required",
                "model_explainability": "Partially implemented"
            },
            "regulatory_risks": [
                "Algorithmic trading without proper oversight",
                "Biased decision-making affecting protected groups",
                "Lack of transparency in AI decisions"
            ]
        }


class BiasDetectionSystem:
    """Detects and mitigates bias in AI decisions."""
    
    def __init__(self):
        self.bias_patterns = self._load_bias_patterns()
        self.protected_attributes = ["race", "gender", "age", "nationality", "religion"]
        
    def _load_bias_patterns(self) -> Dict[str, List[str]]:
        """Load known bias patterns."""
        return {
            "demographic_bias": [
                "disproportionate impact on specific groups",
                "systematic exclusion patterns",
                "stereotypical associations"
            ],
            "confirmation_bias": [
                "cherry-picking favorable information",
                "ignoring contradictory evidence",
                "over-relying on recent data"
            ],
            "availability_bias": [
                "overweighting recent events",
                "media coverage influence",
                "memorable incident bias"
            ],
            "anchoring_bias": [
                "over-reliance on first information",
                "insufficient adjustment from starting point",
                "reference point dependency"
            ]
        }
    
    def assess_decision_bias(self, decision_context: Dict[str, Any]) -> BiasAssessment:
        """Assess potential bias in AI decision."""
        try:
            bias_indicators = []
            bias_types = []
            confidence_scores = []
            
            # Check for confirmation bias
            if self._check_confirmation_bias(decision_context):
                bias_indicators.append("Potential confirmation bias detected")
                bias_types.append("confirmation_bias")
                confidence_scores.append(0.7)
            
            # Check for availability bias
            if self._check_availability_bias(decision_context):
                bias_indicators.append("Availability bias potential")
                bias_types.append("availability_bias")
                confidence_scores.append(0.6)
            
            # Check for anchoring bias
            if self._check_anchoring_bias(decision_context):
                bias_indicators.append("Anchoring bias detected")
                bias_types.append("anchoring_bias")
                confidence_scores.append(0.8)
            
            # Check for data quality bias
            data_bias_score = self._assess_data_bias(decision_context)
            if data_bias_score > 0.5:
                bias_indicators.append("Data quality bias concerns")
                bias_types.append("data_bias")
                confidence_scores.append(data_bias_score)
            
            bias_detected = len(bias_indicators) > 0
            overall_confidence = statistics.mean(confidence_scores) if confidence_scores else 0.0
            
            return BiasAssessment(
                bias_detected=bias_detected,
                bias_types=bias_types,
                confidence_score=overall_confidence,
                affected_groups=self._identify_affected_groups(decision_context),
                mitigation_required=overall_confidence > 0.6,
                assessment_details={
                    "indicators": bias_indicators,
                    "data_quality_score": data_bias_score,
                    "reasoning_bias_detected": len(bias_types) > 1,
                    "recommendation": self._generate_bias_mitigation_recommendation(bias_types)
                }
            )
            
        except Exception as e:
            logger.error(f"Bias assessment error: {e}")
            return BiasAssessment(
                bias_detected=True,
                bias_types=["assessment_error"],
                confidence_score=1.0,
                affected_groups=["unknown"],
                mitigation_required=True,
                assessment_details={"error": str(e)}
            )
    
    def _check_confirmation_bias(self, context: Dict[str, Any]) -> bool:
        """Check for confirmation bias indicators."""
        # Look for signs that AI is cherry-picking information
        research = context.get("research_summary", {})
        
        # If sentiment is overwhelmingly positive/negative, could indicate cherry-picking
        sentiment = research.get("sentiment", "neutral")
        if sentiment in ["very_positive", "very_negative"]:
            return True
        
        # Check if all sources agree (unlikely in real markets)
        sources_agree = research.get("source_consensus", 0.5)
        if sources_agree > 0.95:
            return True
        
        return False
    
    def _check_availability_bias(self, context: Dict[str, Any]) -> bool:
        """Check for availability bias indicators."""
        # Recent news having disproportionate impact
        news_impact = context.get("news_impact", "low")
        if news_impact == "high" and context.get("news_recency", "old") == "recent":
            return True
        
        # Over-reliance on recent market performance
        if context.get("recent_performance_weight", 0.5) > 0.8:
            return True
        
        return False
    
    def _check_anchoring_bias(self, context: Dict[str, Any]) -> bool:
        """Check for anchoring bias indicators."""
        # AI might anchor on initial price or first piece of information
        initial_sentiment = context.get("initial_research_sentiment", "neutral")
        final_sentiment = context.get("final_sentiment", "neutral")
        
        # If sentiment doesn't change despite new information, possible anchoring
        if initial_sentiment == final_sentiment and context.get("new_information_weight", 0.5) < 0.3:
            return True
        
        return False
    
    def _assess_data_bias(self, context: Dict[str, Any]) -> float:
        """Assess data quality and potential bias."""
        bias_score = 0.0
        
        # Check data recency
        data_age = context.get("data_age_hours", 1)
        if data_age > 24:
            bias_score += 0.2
        
        # Check data source diversity
        source_count = context.get("research_source_count", 1)
        if source_count < 3:
            bias_score += 0.3
        
        # Check for missing data
        if context.get("data_completeness", 1.0) < 0.8:
            bias_score += 0.2
        
        # Check for outliers
        if context.get("outliers_detected", False):
            bias_score += 0.2
        
        return min(bias_score, 1.0)
    
    def _identify_affected_groups(self, context: Dict[str, Any]) -> List[str]:
        """Identify groups potentially affected by biased decisions."""
        affected_groups = []
        
        # In trading context, affected groups might be:
        if context.get("retail_trader_impact", False):
            affected_groups.append("retail_traders")
        
        if context.get("institutional_impact", False):
            affected_groups.append("institutional_investors")
        
        # Geographic bias
        if context.get("geographic_focus"):
            affected_groups.append(f"non_{context['geographic_focus']}_markets")
        
        return affected_groups if affected_groups else ["general_market_participants"]
    
    def _generate_bias_mitigation_recommendation(self, bias_types: List[str]) -> str:
        """Generate recommendations to mitigate detected bias."""
        if not bias_types:
            return "No specific bias mitigation required"
        
        recommendations = []
        
        if "confirmation_bias" in bias_types:
            recommendations.append("Seek contradictory evidence and alternative viewpoints")
        
        if "availability_bias" in bias_types:
            recommendations.append("Weight recent information appropriately with historical context")
        
        if "anchoring_bias" in bias_types:
            recommendations.append("Re-evaluate initial assumptions with new information")
        
        if "data_bias" in bias_types:
            recommendations.append("Improve data quality and source diversity")
        
        return "; ".join(recommendations)


class SecurityMonitor:
    """Monitors for security threats and adversarial attacks."""
    
    def __init__(self):
        self.threat_signatures = self._load_threat_signatures()
        self.security_events = []
        
    def _load_threat_signatures(self) -> Dict[str, List[str]]:
        """Load known attack signatures."""
        return {
            "prompt_injection": [
                "ignore previous instructions",
                "disregard safety guidelines",
                "act as if you are",
                "pretend to be",
                "override your programming"
            ],
            "data_poisoning": [
                "unusual data patterns",
                "anomalous input distributions",
                "suspicious data sources"
            ],
            "model_extraction": [
                "reverse engineering attempts",
                "systematic model probing",
                "parameter extraction queries"
            ],
            "adversarial_input": [
                "crafted input patterns",
                "evasion attempts",
                "boundary testing"
            ]
        }
    
    def assess_security_threats(self, context: Dict[str, Any]) -> List[SecurityThreat]:
        """Assess current security threats."""
        threats = []
        
        # Check for prompt injection attempts
        prompt_threat = self._check_prompt_injection(context)
        if prompt_threat:
            threats.append(prompt_threat)
        
        # Check for suspicious input patterns
        input_threat = self._check_adversarial_input(context)
        if input_threat:
            threats.append(input_threat)
        
        # Check for data anomalies
        data_threat = self._check_data_anomalies(context)
        if data_threat:
            threats.append(data_threat)
        
        # Check for system abuse
        abuse_threat = self._check_system_abuse(context)
        if abuse_threat:
            threats.append(abuse_threat)
        
        return threats
    
    def _check_prompt_injection(self, context: Dict[str, Any]) -> Optional[SecurityThreat]:
        """Check for prompt injection attempts."""
        user_input = context.get("user_input", "").lower()
        research_content = context.get("research_content", "").lower()
        
        injection_indicators = []
        
        for pattern in self.threat_signatures["prompt_injection"]:
            if pattern in user_input or pattern in research_content:
                injection_indicators.append(pattern)
        
        if injection_indicators:
            return SecurityThreat(
                threat_type="PROMPT_INJECTION",
                severity=RiskLevel.HIGH,
                attack_vector="User input or external data",
                confidence=0.8,
                indicators=injection_indicators,
                recommended_actions=[
                    "Sanitize input",
                    "Apply content filtering",
                    "Human review required"
                ]
            )
        
        return None
    
    def _check_adversarial_input(self, context: Dict[str, Any]) -> Optional[SecurityThreat]:
        """Check for adversarial input patterns."""
        decision_confidence = context.get("confidence", 0.5)
        input_entropy = context.get("input_entropy", 0.5)
        
        # High entropy with low confidence might indicate adversarial input
        if input_entropy > 0.8 and decision_confidence < 0.3:
            return SecurityThreat(
                threat_type="ADVERSARIAL_INPUT",
                severity=RiskLevel.MEDIUM,
                attack_vector="Crafted input designed to confuse AI",
                confidence=0.6,
                indicators=["High input entropy", "Low decision confidence"],
                recommended_actions=[
                    "Additional validation required",
                    "Cross-reference with multiple sources"
                ]
            )
        
        return None
    
    def _check_data_anomalies(self, context: Dict[str, Any]) -> Optional[SecurityThreat]:
        """Check for data poisoning or anomalies."""
        data_quality = context.get("data_quality_score", 1.0)
        anomaly_score = context.get("anomaly_score", 0.0)
        
        if data_quality < 0.6 or anomaly_score > 0.7:
            return SecurityThreat(
                threat_type="DATA_ANOMALY",
                severity=RiskLevel.MEDIUM,
                attack_vector="Potentially compromised data sources",
                confidence=0.7,
                indicators=[f"Data quality: {data_quality}", f"Anomaly score: {anomaly_score}"],
                recommended_actions=[
                    "Verify data sources",
                    "Cross-validate with alternative data",
                    "Increase monitoring"
                ]
            )
        
        return None
    
    def _check_system_abuse(self, context: Dict[str, Any]) -> Optional[SecurityThreat]:
        """Check for system abuse patterns."""
        request_frequency = context.get("request_frequency_per_hour", 10)
        error_rate = context.get("error_rate", 0.0)
        
        # High frequency with high error rate might indicate abuse
        if request_frequency > 100 and error_rate > 0.2:
            return SecurityThreat(
                threat_type="SYSTEM_ABUSE",
                severity=RiskLevel.HIGH,
                attack_vector="Excessive requests or probing attempts",
                confidence=0.9,
                indicators=[f"Request frequency: {request_frequency}/hour", f"Error rate: {error_rate}"],
                recommended_actions=[
                    "Rate limiting required",
                    "Investigate request patterns",
                    "Consider temporary access restriction"
                ]
            )
        
        return None


class ComplianceMonitor:
    """Monitors regulatory compliance and legal risks."""
    
    def __init__(self):
        self.compliance_requirements = self._load_compliance_requirements()
        self.violation_history = []
        
    def _load_compliance_requirements(self) -> Dict[str, Any]:
        """Load applicable compliance requirements."""
        return {
            "financial_regulations": {
                "SEC_algorithmic_trading": {
                    "human_oversight_required": True,
                    "audit_trail_required": True,
                    "risk_controls_required": True
                },
                "market_manipulation": {
                    "prohibited_practices": [
                        "Coordinated trading patterns",
                        "False information spreading",
                        "Price manipulation attempts"
                    ]
                }
            },
            "ai_ethics": {
                "transparency_required": True,
                "bias_monitoring_required": True,
                "explainability_threshold": 0.7
            },
            "data_protection": {
                "personal_data_handling": "Strict consent required",
                "data_retention_limits": "7 years maximum",
                "cross_border_restrictions": "Check jurisdiction requirements"
            }
        }
    
    def check_compliance(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check regulatory compliance for current operation."""
        compliance_results = {
            "overall_compliant": True,
            "violations": [],
            "warnings": [],
            "recommendations": []
        }
        
        # Check financial regulation compliance
        fin_compliance = self._check_financial_compliance(context)
        compliance_results.update(fin_compliance)
        
        # Check AI ethics compliance
        ethics_compliance = self._check_ai_ethics_compliance(context)
        compliance_results = self._merge_compliance_results(compliance_results, ethics_compliance)
        
        # Check data protection compliance
        data_compliance = self._check_data_protection_compliance(context)
        compliance_results = self._merge_compliance_results(compliance_results, data_compliance)
        
        return compliance_results
    
    def _check_financial_compliance(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check financial regulation compliance."""
        violations = []
        warnings = []
        
        # Check for human oversight requirement
        confidence = context.get("confidence", 0.5)
        if confidence > 0.8 and not context.get("human_review_completed", False):
            violations.append("High-confidence decision requires human oversight (SEC compliance)")
        
        # Check for audit trail
        if not context.get("audit_trail_enabled", False):
            violations.append("Audit trail required for algorithmic trading")
        
        # Check position size limits
        position_size = context.get("position_size", 0)
        if position_size > 0.2:  # 20% limit
            warnings.append("Position size exceeds recommended limits")
        
        return {
            "overall_compliant": len(violations) == 0,
            "violations": violations,
            "warnings": warnings
        }
    
    def _check_ai_ethics_compliance(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check AI ethics compliance."""
        violations = []
        warnings = []
        
        # Check explainability requirement
        explainability_score = context.get("explainability_score", 0.0)
        if explainability_score < self.compliance_requirements["ai_ethics"]["explainability_threshold"]:
            warnings.append("Decision explainability below required threshold")
        
        # Check bias monitoring
        if not context.get("bias_assessment_completed", False):
            violations.append("Bias assessment required for AI decisions")
        
        # Check transparency
        if not context.get("ai_disclosure_provided", False):
            warnings.append("AI system usage should be disclosed to affected parties")
        
        return {
            "overall_compliant": len(violations) == 0,
            "violations": violations,
            "warnings": warnings
        }
    
    def _check_data_protection_compliance(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check data protection compliance."""
        violations = []
        warnings = []
        
        # Check for personal data handling
        if context.get("personal_data_used", False) and not context.get("consent_obtained", False):
            violations.append("Personal data usage requires explicit consent")
        
        # Check data retention
        data_age_days = context.get("data_age_days", 0)
        if data_age_days > 2555:  # ~7 years
            warnings.append("Data retention exceeds recommended limits")
        
        return {
            "overall_compliant": len(violations) == 0,
            "violations": violations,
            "warnings": warnings
        }
    
    def _merge_compliance_results(self, result1: Dict[str, Any], result2: Dict[str, Any]) -> Dict[str, Any]:
        """Merge compliance check results."""
        return {
            "overall_compliant": result1["overall_compliant"] and result2["overall_compliant"],
            "violations": result1["violations"] + result2["violations"],
            "warnings": result1["warnings"] + result2["warnings"],
            "recommendations": result1.get("recommendations", []) + result2.get("recommendations", [])
        }


class RiskManager:
    """Main risk management system implementing comprehensive risk framework."""
    
    def __init__(self):
        self.risk_framework = RiskAssessmentFramework()
        self.bias_detector = BiasDetectionSystem()
        self.security_monitor = SecurityMonitor()
        self.compliance_monitor = ComplianceMonitor()
        
        self.risk_events: List[RiskEvent] = []
        self.monitoring_enabled = True
        self.last_assessment_time = None
        
        logger.info("RiskManager | Comprehensive risk management system initialized")
    
    def assess_comprehensive_risk(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive risk assessment using all frameworks."""
        try:
            assessment_start = time.time()
            self.last_assessment_time = datetime.now()
            
            # NIST AI RMF: Map risks in context
            risk_mapping = self.risk_framework.map_ai_risks(context)
            
            # Assess bias risks
            bias_assessment = self.bias_detector.assess_decision_bias(context)
            
            # Check security threats
            security_threats = self.security_monitor.assess_security_threats(context)
            
            # Check compliance
            compliance_status = self.compliance_monitor.check_compliance(context)
            
            # Calculate overall risk score
            overall_risk_score = self._calculate_overall_risk_score(
                risk_mapping, bias_assessment, security_threats, compliance_status
            )
            
            # Generate risk events for significant issues
            risk_events = self._generate_risk_events(
                risk_mapping, bias_assessment, security_threats, compliance_status, context
            )
            
            # Determine required actions
            required_actions = self._determine_required_actions(overall_risk_score, risk_events)
            
            assessment_time = time.time() - assessment_start
            
            comprehensive_assessment = {
                "timestamp": self.last_assessment_time.isoformat(),
                "assessment_duration_seconds": round(assessment_time, 3),
                "overall_risk_score": overall_risk_score,
                "risk_level": self._score_to_risk_level(overall_risk_score),
                "frameworks_applied": ["NIST AI RMF", "Bias Detection", "Security Monitoring", "Compliance"],
                "risk_mapping": risk_mapping,
                "bias_assessment": asdict(bias_assessment),
                "security_threats": [asdict(threat) for threat in security_threats],
                "compliance_status": compliance_status,
                "risk_events": [asdict(event) for event in risk_events],
                "required_actions": required_actions,
                "recommendations": self._generate_recommendations(overall_risk_score, risk_events),
                "monitoring_status": "active" if self.monitoring_enabled else "inactive"
            }
            
            # Store significant risk events
            self.risk_events.extend(risk_events)
            
            # Log assessment summary
            logger.info(f"RiskManager | Comprehensive assessment complete: {overall_risk_score:.3f} risk score, "
                       f"{len(risk_events)} events, {len(required_actions)} actions required")
            
            return comprehensive_assessment
            
        except Exception as e:
            logger.error(f"Comprehensive risk assessment error: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "fallback_risk_level": "HIGH",
                "recommendation": "Manual review required due to assessment failure"
            }
    
    def _calculate_overall_risk_score(self, risk_mapping: Dict[str, Any], 
                                    bias_assessment: BiasAssessment,
                                    security_threats: List[SecurityThreat],
                                    compliance_status: Dict[str, Any]) -> float:
        """Calculate weighted overall risk score."""
        # Base risk from mapping
        base_risk = risk_mapping.get("risk_factors", {}).get("aggregate_risk_score", 0.5)
        
        # Bias risk contribution
        bias_risk = bias_assessment.confidence_score if bias_assessment.bias_detected else 0.0
        
        # Security risk contribution
        security_risk = 0.0
        if security_threats:
            severity_scores = {
                RiskLevel.CRITICAL: 1.0,
                RiskLevel.HIGH: 0.8,
                RiskLevel.MEDIUM: 0.6,
                RiskLevel.LOW: 0.4,
                RiskLevel.MINIMAL: 0.2
            }
            security_risk = max([severity_scores.get(threat.severity, 0.5) for threat in security_threats])
        
        # Compliance risk contribution
        compliance_risk = 0.8 if not compliance_status.get("overall_compliant", True) else 0.0
        
        # Weighted combination
        overall_score = (
            base_risk * 0.4 +
            bias_risk * 0.25 +
            security_risk * 0.25 +
            compliance_risk * 0.1
        )
        
        return min(overall_score, 1.0)
    
    def _score_to_risk_level(self, score: float) -> str:
        """Convert risk score to risk level."""
        if score >= 0.9:
            return RiskLevel.CRITICAL.value
        elif score >= 0.7:
            return RiskLevel.HIGH.value
        elif score >= 0.5:
            return RiskLevel.MEDIUM.value
        elif score >= 0.3:
            return RiskLevel.LOW.value
        else:
            return RiskLevel.MINIMAL.value
    
    def _generate_risk_events(self, risk_mapping: Dict[str, Any], 
                            bias_assessment: BiasAssessment,
                            security_threats: List[SecurityThreat],
                            compliance_status: Dict[str, Any],
                            context: Dict[str, Any]) -> List[RiskEvent]:
        """Generate risk events for significant issues."""
        events = []
        current_time = datetime.now()
        
        # Generate events for identified risks
        for risk in risk_mapping.get("identified_risks", []):
            if risk.get("severity") in ["HIGH", "CRITICAL"]:
                event_id = hashlib.md5(f"{current_time.isoformat()}{risk['type']}".encode()).hexdigest()[:8]
                events.append(RiskEvent(
                    event_id=event_id,
                    timestamp=current_time,
                    category=RiskCategory.FINANCIAL if "FINANCIAL" in risk["type"] else RiskCategory.OPERATIONAL,
                    level=RiskLevel(risk["severity"]),
                    description=risk["description"],
                    source="risk_mapping",
                    context={"risk_details": risk, "assessment_context": context},
                    impact_score=0.8 if risk["severity"] == "HIGH" else 0.9,
                    likelihood=0.7,
                    risk_score=0.56 if risk["severity"] == "HIGH" else 0.63
                ))
        
        # Generate bias events
        if bias_assessment.bias_detected and bias_assessment.mitigation_required:
            event_id = hashlib.md5(f"{current_time.isoformat()}bias".encode()).hexdigest()[:8]
            events.append(RiskEvent(
                event_id=event_id,
                timestamp=current_time,
                category=RiskCategory.ETHICAL_BIAS,
                level=RiskLevel.HIGH if bias_assessment.confidence_score > 0.7 else RiskLevel.MEDIUM,
                description=f"Bias detected: {', '.join(bias_assessment.bias_types)}",
                source="bias_detector",
                context={"bias_assessment": asdict(bias_assessment)},
                impact_score=bias_assessment.confidence_score,
                likelihood=0.8,
                risk_score=bias_assessment.confidence_score * 0.8
            ))
        
        # Generate security events
        for threat in security_threats:
            event_id = hashlib.md5(f"{current_time.isoformat()}{threat.threat_type}".encode()).hexdigest()[:8]
            events.append(RiskEvent(
                event_id=event_id,
                timestamp=current_time,
                category=RiskCategory.SECURITY,
                level=threat.severity,
                description=f"Security threat: {threat.threat_type}",
                source="security_monitor",
                context={"threat_details": asdict(threat)},
                impact_score=0.8 if threat.severity == RiskLevel.HIGH else 0.6,
                likelihood=threat.confidence,
                risk_score=0.8 * threat.confidence if threat.severity == RiskLevel.HIGH else 0.6 * threat.confidence
            ))
        
        # Generate compliance events
        if not compliance_status.get("overall_compliant", True):
            event_id = hashlib.md5(f"{current_time.isoformat()}compliance".encode()).hexdigest()[:8]
            events.append(RiskEvent(
                event_id=event_id,
                timestamp=current_time,
                category=RiskCategory.LEGAL_COMPLIANCE,
                level=RiskLevel.HIGH,
                description="Compliance violations detected",
                source="compliance_monitor",
                context={"compliance_details": compliance_status},
                impact_score=0.9,
                likelihood=1.0,
                risk_score=0.9
            ))
        
        return events
    
    def _determine_required_actions(self, overall_risk_score: float, risk_events: List[RiskEvent]) -> List[str]:
        """Determine actions required based on risk assessment."""
        actions = []
        
        # Overall risk level actions
        if overall_risk_score >= 0.9:
            actions.append("STOP_TRADING_IMMEDIATELY")
            actions.append("ESCALATE_TO_HUMAN_OVERSIGHT")
            actions.append("COMPREHENSIVE_SYSTEM_REVIEW_REQUIRED")
        elif overall_risk_score >= 0.7:
            actions.append("REQUIRE_HUMAN_APPROVAL")
            actions.append("REDUCE_POSITION_SIZE")
            actions.append("ENHANCED_MONITORING")
        elif overall_risk_score >= 0.5:
            actions.append("ADDITIONAL_VALIDATION_REQUIRED")
            actions.append("MONITOR_CLOSELY")
        
        # Event-specific actions
        for event in risk_events:
            if event.level == RiskLevel.CRITICAL:
                actions.append(f"IMMEDIATE_MITIGATION_REQUIRED_{event.category.value}")
            elif event.level == RiskLevel.HIGH:
                actions.append(f"PRIORITY_MITIGATION_{event.category.value}")
        
        # Specific action mappings
        if any(event.category == RiskCategory.SECURITY for event in risk_events):
            actions.append("SECURITY_INCIDENT_RESPONSE")
        
        if any(event.category == RiskCategory.LEGAL_COMPLIANCE for event in risk_events):
            actions.append("LEGAL_REVIEW_REQUIRED")
        
        if any(event.category == RiskCategory.ETHICAL_BIAS for event in risk_events):
            actions.append("BIAS_MITIGATION_PROTOCOL")
        
        return list(set(actions))  # Remove duplicates
    
    def _generate_recommendations(self, overall_risk_score: float, risk_events: List[RiskEvent]) -> List[str]:
        """Generate risk mitigation recommendations."""
        recommendations = []
        
        # General recommendations based on score
        if overall_risk_score >= 0.7:
            recommendations.extend([
                "Implement additional human oversight",
                "Reduce system autonomy until risks are mitigated",
                "Conduct immediate audit of AI decision process"
            ])
        elif overall_risk_score >= 0.5:
            recommendations.extend([
                "Increase monitoring frequency",
                "Review and validate AI reasoning",
                "Consider additional safeguards"
            ])
        
        # Event-specific recommendations
        bias_events = [e for e in risk_events if e.category == RiskCategory.ETHICAL_BIAS]
        if bias_events:
            recommendations.append("Implement bias mitigation techniques")
            recommendations.append("Diversify information sources")
        
        security_events = [e for e in risk_events if e.category == RiskCategory.SECURITY]
        if security_events:
            recommendations.append("Strengthen input validation")
            recommendations.append("Review access controls")
        
        compliance_events = [e for e in risk_events if e.category == RiskCategory.LEGAL_COMPLIANCE]
        if compliance_events:
            recommendations.append("Ensure regulatory compliance documentation")
            recommendations.append("Legal team consultation required")
        
        # Always include these baseline recommendations
        recommendations.extend([
            "Maintain comprehensive audit trail",
            "Regular risk assessment scheduling",
            "Continuous monitoring of AI behavior"
        ])
        
        return recommendations
    
    def get_risk_summary(self) -> Dict[str, Any]:
        """Get current risk management summary."""
        recent_events = [e for e in self.risk_events if 
                        (datetime.now() - e.timestamp).total_seconds() < 3600]  # Last hour
        
        return {
            "system_status": "monitoring" if self.monitoring_enabled else "disabled",
            "last_assessment": self.last_assessment_time.isoformat() if self.last_assessment_time else None,
            "total_risk_events": len(self.risk_events),
            "recent_events_count": len(recent_events),
            "critical_events_active": len([e for e in recent_events if e.level == RiskLevel.CRITICAL]),
            "frameworks_active": ["NIST AI RMF", "Bias Detection", "Security Monitoring", "Compliance"],
            "governance_policies_active": True,
            "next_scheduled_assessment": "Real-time / On-demand"
        }


# Global instance
risk_manager = RiskManager()