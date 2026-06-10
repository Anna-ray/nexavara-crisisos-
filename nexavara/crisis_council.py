"""
NEXAVARA CrisisOS - AI Crisis Council

The 8 Director Agents that form the autonomous crisis intelligence council.
Each agent has independent reasoning, memory, and decision-making capabilities.
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
import json

from .core_models import (
    DirectorAgentType,
    AgentStatus,
    AgentState,
    AgentPersonality,
    AgentPosition,
    AgentTrustMetrics,
    CrisisContext,
    Evidence,
    Finding,
    IncidentSeverity,
)


# ============================================================================
# BASE DIRECTOR AGENT
# ============================================================================

class BaseDirectorAgent:
    """Base class for all Director Agents in the Crisis Council"""
    
    def __init__(
        self,
        agent_type: DirectorAgentType,
        personality: AgentPersonality,
        ai_client: Optional[Any] = None
    ):
        self.agent_type = agent_type
        self.personality = personality
        self.ai_client = ai_client
        
        # Initialize state
        self.state = AgentState(
            agent_id=f"{agent_type.value}-001",
            agent_type=agent_type,
            status=AgentStatus.IDLE,
            personality=personality,
        )
        
        # Initialize trust metrics
        self.trust_metrics = AgentTrustMetrics(agent=agent_type)
        
        # Memory
        self.memory: List[Dict[str, Any]] = []
        self.current_context: Optional[CrisisContext] = None
    
    def get_role_description(self) -> str:
        """Get the role description for this agent"""
        raise NotImplementedError("Subclasses must implement get_role_description")
    
    def get_key_questions(self) -> List[str]:
        """Get the key questions this agent asks"""
        raise NotImplementedError("Subclasses must implement get_key_questions")
    
    def get_decision_bias(self) -> str:
        """Get the decision bias for this agent"""
        raise NotImplementedError("Subclasses must implement get_decision_bias")
    
    def analyze_crisis(self, context: CrisisContext) -> Finding:
        """Analyze a crisis and produce a finding"""
        self.current_context = context
        self.state.status = AgentStatus.ANALYZING
        
        # Use AI if available, otherwise use heuristics
        if self.ai_client:
            finding = self._analyze_with_ai(context)
        else:
            finding = self._analyze_with_heuristics(context)
        
        self.state.status = AgentStatus.IDLE
        self.state.current_position = finding.description
        self.state.current_confidence = finding.confidence
        
        # Store in memory
        self.memory.append({
            "timestamp": datetime.utcnow(),
            "action": "analysis",
            "context": context.incident_id,
            "finding": finding.dict(),
        })
        
        return finding
    
    def _analyze_with_ai(self, context: CrisisContext) -> Finding:
        """Analyze using AI (to be implemented with actual AI client)"""
        # This will be implemented with actual AI integration
        return self._analyze_with_heuristics(context)
    
    def _analyze_with_heuristics(self, context: CrisisContext) -> Finding:
        """Analyze using rule-based heuristics"""
        raise NotImplementedError("Subclasses must implement _analyze_with_heuristics")
    
    def form_position(self, topic: str, context: CrisisContext) -> AgentPosition:
        """Form a position on a specific topic"""
        self.state.status = AgentStatus.ANALYZING
        
        # Use AI if available
        if self.ai_client:
            position = self._form_position_with_ai(topic, context)
        else:
            position = self._form_position_with_heuristics(topic, context)
        
        self.state.status = AgentStatus.IDLE
        return position
    
    def _form_position_with_ai(self, topic: str, context: CrisisContext) -> AgentPosition:
        """Form position using AI (to be implemented with actual AI client)"""
        # This will be implemented with actual AI integration
        return self._form_position_with_heuristics(topic, context)
    
    def _form_position_with_heuristics(self, topic: str, context: CrisisContext) -> AgentPosition:
        """Form position using heuristics"""
        raise NotImplementedError("Subclasses must implement _form_position_with_heuristics")
    
    def update_trust_metrics(self, correct: bool):
        """Update trust metrics based on prediction outcome"""
        self.trust_metrics.total_predictions += 1
        if correct:
            self.trust_metrics.correct_predictions += 1
        
        # Recalculate accuracy
        self.trust_metrics.accuracy_rate = (
            self.trust_metrics.correct_predictions / self.trust_metrics.total_predictions
        )
        
        # Update overall trust score (weighted average)
        self.trust_metrics.overall_trust_score = (
            0.4 * self.trust_metrics.accuracy_rate +
            0.3 * self.trust_metrics.decision_reliability +
            0.3 * self.trust_metrics.evidence_quality
        )
        
        # Determine trend
        if self.trust_metrics.accuracy_rate > 0.85:
            self.trust_metrics.trust_trend = "improving"
        elif self.trust_metrics.accuracy_rate < 0.70:
            self.trust_metrics.trust_trend = "declining"
        else:
            self.trust_metrics.trust_trend = "stable"


# ============================================================================
# THREAT DIRECTOR AGENT
# ============================================================================

class ThreatDirectorAgent(BaseDirectorAgent):
    """
    Chief Threat Intelligence Officer
    
    Focus: Attack vectors, threat actors, technical containment
    Personality: Aggressive, security-first, technical
    Decision Bias: Favor immediate containment over cost
    """
    
    def __init__(self, ai_client: Optional[Any] = None):
        personality = AgentPersonality(
            risk_tolerance=0.2,  # Risk-averse
            cost_sensitivity=0.3,  # Less cost-sensitive
            speed_preference=0.9,  # Fast action
            compliance_strictness=0.7,
            customer_focus=0.4,
        )
        super().__init__(DirectorAgentType.THREAT, personality, ai_client)
    
    def get_role_description(self) -> str:
        return "Chief Threat Intelligence Officer - Focuses on attack vectors, threat actors, and technical containment"
    
    def get_key_questions(self) -> List[str]:
        return [
            "What is the attack vector?",
            "Who is the threat actor?",
            "How do we contain immediately?",
            "What's the technical severity?",
        ]
    
    def get_decision_bias(self) -> str:
        return "Favor immediate containment over cost"
    
    def _analyze_with_heuristics(self, context: CrisisContext) -> Finding:
        """Analyze threat using heuristics"""
        
        # Assess severity based on keywords and context
        severity = context.severity
        confidence = 0.85
        
        # Look for threat indicators
        threat_keywords = ["compromise", "breach", "attack", "malware", "ransomware", "exploit"]
        description_lower = context.description.lower()
        
        threat_level = sum(1 for keyword in threat_keywords if keyword in description_lower)
        
        if threat_level >= 3:
            severity = IncidentSeverity.CATASTROPHIC
            confidence = 0.95
            recommendation = "IMMEDIATE CONTAINMENT REQUIRED"
        elif threat_level >= 2:
            severity = IncidentSeverity.CRITICAL
            confidence = 0.90
            recommendation = "Urgent containment within 15 minutes"
        else:
            recommendation = "Investigate and prepare containment"
        
        evidence = [
            Evidence(
                source="ThreatDirector",
                content=f"Threat indicators detected: {threat_level}/6",
                confidence=confidence,
                evidence_type="intelligence",
            )
        ]
        
        return Finding(
            agent=self.agent_type,
            title="Threat Assessment",
            description=f"{recommendation}. Severity: {severity.name}",
            severity=severity,
            confidence=confidence,
            evidence=evidence,
            tags=["threat", "containment", "security"],
        )
    
    def _form_position_with_heuristics(self, topic: str, context: CrisisContext) -> AgentPosition:
        """Form position on containment strategy"""
        
        if "contain" in topic.lower() or "isolate" in topic.lower():
            position = "Recommend immediate containment to prevent spread"
            confidence = 0.95
            reasoning = "Security-first approach: contain now, investigate later"
        elif "cost" in topic.lower():
            position = "Security takes precedence over cost considerations"
            confidence = 0.90
            reasoning = "Breach expansion costs exceed containment costs"
        else:
            position = "Prioritize threat elimination"
            confidence = 0.85
            reasoning = "Technical security is paramount"
        
        return AgentPosition(
            agent=self.agent_type,
            position=position,
            reasoning=reasoning,
            confidence=confidence,
        )


# ============================================================================
# RISK DIRECTOR AGENT
# ============================================================================

class RiskDirectorAgent(BaseDirectorAgent):
    """
    Chief Risk Officer
    
    Focus: Quantitative risk, probability, exposure calculation
    Personality: Analytical, data-driven, probabilistic
    Decision Bias: Favor quantifiable metrics
    """
    
    def __init__(self, ai_client: Optional[Any] = None):
        personality = AgentPersonality(
            risk_tolerance=0.5,  # Balanced
            cost_sensitivity=0.8,  # Cost-aware
            speed_preference=0.5,  # Deliberate
            compliance_strictness=0.6,
            customer_focus=0.5,
        )
        super().__init__(DirectorAgentType.RISK, personality, ai_client)
    
    def get_role_description(self) -> str:
        return "Chief Risk Officer - Focuses on quantitative risk, probability, and exposure calculation"
    
    def get_key_questions(self) -> List[str]:
        return [
            "What's the financial exposure?",
            "What's the probability of escalation?",
            "What's the expected loss?",
            "What's the risk-adjusted decision?",
        ]
    
    def get_decision_bias(self) -> str:
        return "Favor quantifiable metrics"
    
    def _analyze_with_heuristics(self, context: CrisisContext) -> Finding:
        """Calculate risk exposure"""
        
        # Calculate exposure based on severity and affected entities
        base_exposure = {
            IncidentSeverity.LOW: 100_000,
            IncidentSeverity.MODERATE: 500_000,
            IncidentSeverity.HIGH: 2_000_000,
            IncidentSeverity.CRITICAL: 10_000_000,
            IncidentSeverity.CATASTROPHIC: 50_000_000,
        }
        
        exposure = base_exposure.get(context.severity, 1_000_000)
        
        # Adjust for affected entities
        entity_multiplier = 1 + (len(context.affected_entities) * 0.1)
        exposure *= entity_multiplier
        
        confidence = 0.75  # Initial estimate
        
        evidence = [
            Evidence(
                source="RiskDirector",
                content=f"Estimated exposure: ${exposure:,.0f}",
                confidence=confidence,
                evidence_type="metric",
                metadata={"exposure_usd": exposure},
            )
        ]
        
        return Finding(
            agent=self.agent_type,
            title="Risk Assessment",
            description=f"Estimated financial exposure: ${exposure:,.0f}. Confidence: {confidence:.0%}",
            severity=context.severity,
            confidence=confidence,
            evidence=evidence,
            tags=["risk", "financial", "exposure"],
        )
    
    def _form_position_with_heuristics(self, topic: str, context: CrisisContext) -> AgentPosition:
        """Form position on risk-adjusted decisions"""
        
        # Calculate expected loss
        exposure = 5_000_000  # Default estimate
        probability = 0.6
        expected_loss = exposure * probability
        
        if "cost" in topic.lower():
            position = f"Expected loss: ${expected_loss:,.0f}. Cost-benefit analysis required."
            confidence = 0.78
            reasoning = "Risk-adjusted decision based on probability and exposure"
        else:
            position = f"Quantified risk: ${exposure:,.0f} at {probability:.0%} probability"
            confidence = 0.75
            reasoning = "Data-driven risk assessment"
        
        return AgentPosition(
            agent=self.agent_type,
            position=position,
            reasoning=reasoning,
            confidence=confidence,
        )


# ============================================================================
# COMPLIANCE DIRECTOR AGENT
# ============================================================================

class ComplianceDirectorAgent(BaseDirectorAgent):
    """
    Chief Compliance Officer
    
    Focus: Regulatory requirements, legal obligations, reporting
    Personality: Conservative, rule-based, documentation-focused
    Decision Bias: Favor regulatory compliance over speed
    """
    
    def __init__(self, ai_client: Optional[Any] = None):
        personality = AgentPersonality(
            risk_tolerance=0.2,  # Risk-averse
            cost_sensitivity=0.4,
            speed_preference=0.3,  # Deliberate
            compliance_strictness=0.95,  # Very strict
            customer_focus=0.6,
        )
        super().__init__(DirectorAgentType.COMPLIANCE, personality, ai_client)
    
    def get_role_description(self) -> str:
        return "Chief Compliance Officer - Focuses on regulatory requirements, legal obligations, and reporting"
    
    def get_key_questions(self) -> List[str]:
        return [
            "What are our regulatory obligations?",
            "What must we report and when?",
            "What are the compliance penalties?",
            "Are we meeting legal requirements?",
        ]
    
    def get_decision_bias(self) -> str:
        return "Favor regulatory compliance over speed"
    
    def _analyze_with_heuristics(self, context: CrisisContext) -> Finding:
        """Assess compliance requirements"""
        
        # Check for data breach indicators
        data_breach_keywords = ["data", "customer", "records", "pii", "breach", "exposure"]
        description_lower = context.description.lower()
        
        is_data_breach = any(keyword in description_lower for keyword in data_breach_keywords)
        
        if is_data_breach:
            severity = IncidentSeverity.CRITICAL
            confidence = 0.92
            description = "GDPR/CCPA breach notification required within 72 hours. Potential fines: $20M+"
        elif context.severity >= IncidentSeverity.HIGH:
            severity = context.severity
            confidence = 0.85
            description = "Regulatory reporting may be required. Document all actions."
        else:
            severity = context.severity
            confidence = 0.80
            description = "Monitor for compliance implications. Maintain audit trail."
        
        evidence = [
            Evidence(
                source="ComplianceDirector",
                content=f"Regulatory assessment: {description}",
                confidence=confidence,
                evidence_type="intelligence",
            )
        ]
        
        return Finding(
            agent=self.agent_type,
            title="Compliance Assessment",
            description=description,
            severity=severity,
            confidence=confidence,
            evidence=evidence,
            tags=["compliance", "regulatory", "legal"],
        )
    
    def _form_position_with_heuristics(self, topic: str, context: CrisisContext) -> AgentPosition:
        """Form position on compliance requirements"""
        
        if "delay" in topic.lower() or "wait" in topic.lower():
            position = "Delaying action increases regulatory exposure and potential fines"
            confidence = 0.92
            reasoning = "GDPR requires immediate action on security incidents"
        elif "cost" in topic.lower():
            position = "Compliance fines exceed operational costs. Regulatory compliance is mandatory."
            confidence = 0.90
            reasoning = "Non-compliance penalties are severe and non-negotiable"
        else:
            position = "Ensure all actions meet regulatory requirements"
            confidence = 0.88
            reasoning = "Compliance is a legal obligation, not optional"
        
        return AgentPosition(
            agent=self.agent_type,
            position=position,
            reasoning=reasoning,
            confidence=confidence,
        )


# ============================================================================
# FINANCE DIRECTOR AGENT
# ============================================================================

class FinanceDirectorAgent(BaseDirectorAgent):
    """
    Chief Financial Officer
    
    Focus: Cost optimization, budget impact, ROI
    Personality: Cost-conscious, ROI-focused, pragmatic
    Decision Bias: Favor cost efficiency
    """
    
    def __init__(self, ai_client: Optional[Any] = None):
        personality = AgentPersonality(
            risk_tolerance=0.6,  # Moderate risk tolerance
            cost_sensitivity=0.95,  # Very cost-sensitive
            speed_preference=0.4,
            compliance_strictness=0.5,
            customer_focus=0.5,
        )
        super().__init__(DirectorAgentType.FINANCE, personality, ai_client)
    
    def get_role_description(self) -> str:
        return "Chief Financial Officer - Focuses on cost optimization, budget impact, and ROI"
    
    def get_key_questions(self) -> List[str]:
        return [
            "What does this cost?",
            "What's the cheapest safe option?",
            "Can we defer expenses?",
            "What's the budget impact?",
        ]
    
    def get_decision_bias(self) -> str:
        return "Favor cost efficiency"
    
    def _analyze_with_heuristics(self, context: CrisisContext) -> Finding:
        """Calculate financial impact"""
        
        # Estimate costs based on severity
        response_costs = {
            IncidentSeverity.LOW: 50_000,
            IncidentSeverity.MODERATE: 200_000,
            IncidentSeverity.HIGH: 500_000,
            IncidentSeverity.CRITICAL: 2_000_000,
            IncidentSeverity.CATASTROPHIC: 10_000_000,
        }
        
        cost = response_costs.get(context.severity, 500_000)
        confidence = 0.70
        
        evidence = [
            Evidence(
                source="FinanceDirector",
                content=f"Estimated response cost: ${cost:,.0f}",
                confidence=confidence,
                evidence_type="metric",
                metadata={"cost_usd": cost},
            )
        ]
        
        return Finding(
            agent=self.agent_type,
            title="Financial Impact Assessment",
            description=f"Estimated response cost: ${cost:,.0f}. Budget impact: {context.severity.name}",
            severity=context.severity,
            confidence=confidence,
            evidence=evidence,
            tags=["finance", "cost", "budget"],
        )
    
    def _form_position_with_heuristics(self, topic: str, context: CrisisContext) -> AgentPosition:
        """Form position on cost optimization"""
        
        containment_cost = 500_000
        potential_loss = 5_000_000
        
        if "contain" in topic.lower() and "cost" in topic.lower():
            if potential_loss > containment_cost * 2:
                position = f"Containment cost (${containment_cost:,.0f}) justified by risk reduction (${potential_loss:,.0f})"
                confidence = 0.89
                reasoning = "ROI positive: preventing loss exceeds containment cost"
            else:
                position = f"Containment cost (${containment_cost:,.0f}) exceeds current projected loss"
                confidence = 0.85
                reasoning = "Cost-benefit analysis suggests delayed action"
        else:
            position = "Optimize for cost-effective response"
            confidence = 0.80
            reasoning = "Balance security needs with budget constraints"
        
        return AgentPosition(
            agent=self.agent_type,
            position=position,
            reasoning=reasoning,
            confidence=confidence,
        )


# ============================================================================
# OPERATIONS DIRECTOR AGENT
# ============================================================================

class OperationsDirectorAgent(BaseDirectorAgent):
    """
    Chief Operations Officer
    
    Focus: Business continuity, service availability, customer impact
    Personality: Customer-focused, availability-driven, practical
    Decision Bias: Favor business continuity
    """
    
    def __init__(self, ai_client: Optional[Any] = None):
        personality = AgentPersonality(
            risk_tolerance=0.5,
            cost_sensitivity=0.6,
            speed_preference=0.7,
            compliance_strictness=0.6,
            customer_focus=0.95,  # Very customer-focused
        )
        super().__init__(DirectorAgentType.OPERATIONS, personality, ai_client)
    
    def get_role_description(self) -> str:
        return "Chief Operations Officer - Focuses on business continuity, service availability, and customer impact"
    
    def get_key_questions(self) -> List[str]:
        return [
            "What's the customer impact?",
            "Can we maintain operations?",
            "What's the downtime cost?",
            "How do we minimize disruption?",
        ]
    
    def get_decision_bias(self) -> str:
        return "Favor business continuity"
    
    def _analyze_with_heuristics(self, context: CrisisContext) -> Finding:
        """Assess operational impact"""
        
        # Estimate customer impact
        affected_users = len(context.affected_entities) * 10_000  # Rough estimate
        downtime_hours = context.severity.value * 2
        
        confidence = 0.82
        
        evidence = [
            Evidence(
                source="OperationsDirector",
                content=f"Estimated impact: {affected_users:,} users, {downtime_hours}h downtime",
                confidence=confidence,
                evidence_type="metric",
                metadata={
                    "affected_users": affected_users,
                    "downtime_hours": downtime_hours,
                },
            )
        ]
        
        return Finding(
            agent=self.agent_type,
            title="Operational Impact Assessment",
            description=f"Customer impact: {affected_users:,} users. Estimated downtime: {downtime_hours} hours",
            severity=context.severity,
            confidence=confidence,
            evidence=evidence,
            tags=["operations", "customers", "availability"],
        )
    
    def _form_position_with_heuristics(self, topic: str, context: CrisisContext) -> AgentPosition:
        """Form position on operational continuity"""
        
        if "downtime" in topic.lower() or "availability" in topic.lower():
            position = "Minimize customer-facing downtime. Prioritize service restoration."
            confidence = 0.91
            reasoning = "Customer experience is critical to business continuity"
        elif "contain" in topic.lower():
            position = "Support containment if it minimizes total customer impact"
            confidence = 0.87
            reasoning = "Short-term disruption acceptable to prevent larger outage"
        else:
            position = "Maintain operations while addressing security concerns"
            confidence = 0.85
            reasoning = "Balance security response with service availability"
        
        return AgentPosition(
            agent=self.agent_type,
            position=position,
            reasoning=reasoning,
            confidence=confidence,
        )


# ============================================================================
# LEGAL DIRECTOR AGENT
# ============================================================================

class LegalDirectorAgent(BaseDirectorAgent):
    """
    General Counsel
    
    Focus: Liability, litigation risk, evidence preservation
    Personality: Cautious, evidence-based, defensive
    Decision Bias: Favor evidence and defensibility
    """
    
    def __init__(self, ai_client: Optional[Any] = None):
        personality = AgentPersonality(
            risk_tolerance=0.3,  # Risk-averse
            cost_sensitivity=0.5,
            speed_preference=0.3,  # Deliberate
            compliance_strictness=0.85,
            customer_focus=0.4,
        )
        super().__init__(DirectorAgentType.LEGAL, personality, ai_client)
    
    def get_role_description(self) -> str:
        return "General Counsel - Focuses on liability, litigation risk, and evidence preservation"
    
    def get_key_questions(self) -> List[str]:
        return [
            "What's our legal exposure?",
            "Are we preserving evidence?",
            "What's the litigation risk?",
            "Do we have sufficient proof?",
        ]
    
    def get_decision_bias(self) -> str:
        return "Favor evidence and defensibility"
    
    def _analyze_with_heuristics(self, context: CrisisContext) -> Finding:
        """Assess legal implications"""
        
        # Assess litigation risk
        evidence_quality = len(context.evidence) / max(len(context.affected_entities), 1)
        
        if evidence_quality > 0.5:
            confidence = 0.88
            description = "Evidence preservation adequate. Litigation risk: MODERATE"
        else:
            confidence = 0.75
            description = "CRITICAL: Insufficient evidence. Increase documentation immediately."
        
        evidence = [
            Evidence(
                source="LegalDirector",
                content=f"Legal assessment: {description}",
                confidence=confidence,
                evidence_type="intelligence",
            )
        ]
        
        return Finding(
            agent=self.agent_type,
            title="Legal Risk Assessment",
            description=description,
            severity=context.severity,
            confidence=confidence,
            evidence=evidence,
            tags=["legal", "liability", "evidence"],
        )
    
    def _form_position_with_heuristics(self, topic: str, context: CrisisContext) -> AgentPosition:
        """Form position on legal defensibility"""
        
        if "evidence" in topic.lower() or "documentation" in topic.lower():
            position = "Ensure comprehensive documentation for legal defense"
            confidence = 0.91
            reasoning = "Evidence quality determines litigation outcomes"
        elif "immediate" in topic.lower():
            position = "Support action if evidence preservation is maintained"
            confidence = 0.85
            reasoning = "Due diligence requires documented decision-making"
        else:
            position = "Minimize legal exposure through proper procedures"
            confidence = 0.88
            reasoning = "Legal defensibility requires process compliance"
        
        return AgentPosition(
            agent=self.agent_type,
            position=position,
            reasoning=reasoning,
            confidence=confidence,
        )


# ============================================================================
# REPUTATION DIRECTOR AGENT
# ============================================================================

class ReputationDirectorAgent(BaseDirectorAgent):
    """
    Chief Communications Officer
    
    Focus: Brand impact, public perception, stakeholder trust
    Personality: PR-focused, perception-aware, strategic
    Decision Bias: Favor reputation protection
    """
    
    def __init__(self, ai_client: Optional[Any] = None):
        personality = AgentPersonality(
            risk_tolerance=0.4,
            cost_sensitivity=0.5,
            speed_preference=0.6,
            compliance_strictness=0.7,
            customer_focus=0.9,
        )
        super().__init__(DirectorAgentType.REPUTATION, personality, ai_client)
    
    def get_role_description(self) -> str:
        return "Chief Communications Officer - Focuses on brand impact, public perception, and stakeholder trust"
    
    def get_key_questions(self) -> List[str]:
        return [
            "How does this affect our brand?",
            "What's the public perception?",
            "How do we communicate this?",
            "What's the trust impact?",
        ]
    
    def get_decision_bias(self) -> str:
        return "Favor reputation protection"
    
    def _analyze_with_heuristics(self, context: CrisisContext) -> Finding:
        """Assess reputation impact"""
        
        # Assess public visibility
        public_facing = any(
            keyword in context.description.lower()
            for keyword in ["customer", "public", "breach", "data", "exposure"]
        )
        
        if public_facing:
            severity = max(context.severity, IncidentSeverity.HIGH)
            confidence = 0.85
            description = "HIGH public visibility. Proactive communication strategy required."
        else:
            severity = context.severity
            confidence = 0.80
            description = "Moderate reputation risk. Monitor public sentiment."
        
        evidence = [
            Evidence(
                source="ReputationDirector",
                content=f"Reputation assessment: {description}",
                confidence=confidence,
                evidence_type="intelligence",
            )
        ]
        
        return Finding(
            agent=self.agent_type,
            title="Reputation Impact Assessment",
            description=description,
            severity=severity,
            confidence=confidence,
            evidence=evidence,
            tags=["reputation", "brand", "communications"],
        )
    
    def _form_position_with_heuristics(self, topic: str, context: CrisisContext) -> AgentPosition:
        """Form position on reputation management"""
        
        if "communication" in topic.lower() or "public" in topic.lower():
            position = "Proactive, transparent communication protects brand trust"
            confidence = 0.88
            reasoning = "Transparency builds trust; silence breeds speculation"
        elif "immediate" in topic.lower():
            position = "Support swift action to demonstrate security commitment"
            confidence = 0.86
            reasoning = "Decisive response enhances reputation"
        else:
            position = "Protect brand reputation through responsible crisis management"
            confidence = 0.84
            reasoning = "Long-term trust depends on crisis response quality"
        
        return AgentPosition(
            agent=self.agent_type,
            position=position,
            reasoning=reasoning,
            confidence=confidence,
        )


# ============================================================================
# EXECUTIVE BRIEFING DIRECTOR AGENT
# ============================================================================

class ExecutiveBriefingDirectorAgent(BaseDirectorAgent):
    """
    Chief of Staff
    
    Focus: Synthesis, executive communication, decision clarity
    Personality: Synthesizer, communicator, decision-facilitator
    Decision Bias: Favor clarity and actionability
    """
    
    def __init__(self, ai_client: Optional[Any] = None):
        personality = AgentPersonality(
            risk_tolerance=0.5,
            cost_sensitivity=0.5,
            speed_preference=0.7,
            compliance_strictness=0.7,
            customer_focus=0.7,
        )
        super().__init__(DirectorAgentType.EXECUTIVE, personality, ai_client)
    
    def get_role_description(self) -> str:
        return "Chief of Staff - Focuses on synthesis, executive communication, and decision clarity"
    
    def get_key_questions(self) -> List[str]:
        return [
            "What does the board need to know?",
            "What's the executive summary?",
            "What are the decision options?",
            "What's the recommended action?",
        ]
    
    def get_decision_bias(self) -> str:
        return "Favor clarity and actionability"
    
    def _analyze_with_heuristics(self, context: CrisisContext) -> Finding:
        """Synthesize executive perspective"""
        
        confidence = 0.90
        description = f"Executive Summary: {context.severity.name} incident affecting {len(context.affected_entities)} systems. Immediate attention required."
        
        evidence = [
            Evidence(
                source="ExecutiveDirector",
                content=description,
                confidence=confidence,
                evidence_type="intelligence",
            )
        ]
        
        return Finding(
            agent=self.agent_type,
            title="Executive Briefing",
            description=description,
            severity=context.severity,
            confidence=confidence,
            evidence=evidence,
            tags=["executive", "briefing", "summary"],
        )
    
    def _form_position_with_heuristics(self, topic: str, context: CrisisContext) -> AgentPosition:
        """Form synthesized executive position"""
        
        position = "Synthesize council recommendations into clear executive decision"
        confidence = 0.90
        reasoning = "Executive clarity enables decisive action"
        
        return AgentPosition(
            agent=self.agent_type,
            position=position,
            reasoning=reasoning,
            confidence=confidence,
        )
    
    def synthesize_council_findings(self, findings: List[Finding]) -> str:
        """Synthesize multiple findings into executive summary"""
        
        if not findings:
            return "No findings to synthesize"
        
        # Extract key points
        severity_counts = {}
        for finding in findings:
            severity_counts[finding.severity] = severity_counts.get(finding.severity, 0) + 1
        
        max_severity = max(severity_counts.keys(), key=lambda s: s.value)
        avg_confidence = sum(f.confidence for f in findings) / len(findings)
        
        summary = f"""
EXECUTIVE SUMMARY

Incident Status: {max_severity.name}
Council Confidence: {avg_confidence:.0%}
Findings: {len(findings)} from {len(set(f.agent for f in findings))} directors

Key Recommendations:
"""
        
        for finding in findings[:3]:  # Top 3 findings
            summary += f"\n• {finding.agent.value}: {finding.description}"
        
        return summary


# ============================================================================
# CRISIS COUNCIL
# ============================================================================

class CrisisCouncil:
    """The complete AI Crisis Council with all 8 Director Agents"""
    
    def __init__(self, ai_client: Optional[Any] = None):
        self.ai_client = ai_client
        
        # Initialize all 8 directors
        self.threat_director = ThreatDirectorAgent(ai_client)
        self.risk_director = RiskDirectorAgent(ai_client)
        self.compliance_director = ComplianceDirectorAgent(ai_client)
        self.finance_director = FinanceDirectorAgent(ai_client)
        self.operations_director = OperationsDirectorAgent(ai_client)
        self.legal_director = LegalDirectorAgent(ai_client)
        self.reputation_director = ReputationDirectorAgent(ai_client)
        self.executive_director = ExecutiveBriefingDirectorAgent(ai_client)
        
        # Council registry
        self.directors: Dict[DirectorAgentType, BaseDirectorAgent] = {
            DirectorAgentType.THREAT: self.threat_director,
            DirectorAgentType.RISK: self.risk_director,
            DirectorAgentType.COMPLIANCE: self.compliance_director,
            DirectorAgentType.FINANCE: self.finance_director,
            DirectorAgentType.OPERATIONS: self.operations_director,
            DirectorAgentType.LEGAL: self.legal_director,
            DirectorAgentType.REPUTATION: self.reputation_director,
            DirectorAgentType.EXECUTIVE: self.executive_director,
        }
    
    def analyze_crisis(self, context: CrisisContext) -> List[Finding]:
        """Have all directors analyze the crisis"""
        findings = []
        
        for director in self.directors.values():
            finding = director.analyze_crisis(context)
            findings.append(finding)
        
        return findings
    
    def get_council_status(self) -> Dict[str, Any]:
        """Get current status of all council members"""
        return {
            agent_type.value: {
                "status": director.state.status.value,
                "confidence": director.state.current_confidence,
                "trust_score": director.trust_metrics.overall_trust_score,
            }
            for agent_type, director in self.directors.items()
        }
    
    def get_director(self, agent_type: DirectorAgentType) -> BaseDirectorAgent:
        """Get a specific director"""
        return self.directors[agent_type]

# Made with Bob
