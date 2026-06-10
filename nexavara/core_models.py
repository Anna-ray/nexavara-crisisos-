"""
NEXAVARA CrisisOS - Core Data Models

The foundational data structures for the Crisis Intelligence Operating System.
These models define the contracts between all system components.
"""

from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
import uuid


# ============================================================================
# ENUMERATIONS
# ============================================================================

class DirectorAgentType(str, Enum):
    """The 8 Director Agents in the Crisis Council"""
    THREAT = "threat_director"
    RISK = "risk_director"
    COMPLIANCE = "compliance_director"
    FINANCE = "finance_director"
    OPERATIONS = "operations_director"
    LEGAL = "legal_director"
    REPUTATION = "reputation_director"
    EXECUTIVE = "executive_director"


class AgentStatus(str, Enum):
    """Current status of an agent"""
    IDLE = "idle"
    ANALYZING = "analyzing"
    DEBATING = "debating"
    SYNTHESIZING = "synthesizing"
    WAITING = "waiting"


class IncidentSeverity(int, Enum):
    """Incident severity levels"""
    LOW = 1
    MODERATE = 2
    HIGH = 3
    CRITICAL = 4
    CATASTROPHIC = 5


class EntityType(str, Enum):
    """Types of organizational entities in the Digital Twin"""
    IDENTITY_SYSTEM = "identity"
    CLOUD_INFRASTRUCTURE = "cloud"
    EMPLOYEE_GROUP = "employees"
    CUSTOMER_SEGMENT = "customers"
    FINANCIAL_SYSTEM = "finance"
    VENDOR = "vendor"
    APPLICATION = "application"
    DATA_STORE = "data"
    NETWORK = "network"
    REGULATOR = "regulator"
    EXECUTIVE = "executive"


class ImpactDimension(str, Enum):
    """Dimensions of crisis impact"""
    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    REGULATORY = "regulatory"
    CUSTOMER = "customer"
    REPUTATION = "reputation"


class TimeHorizon(str, Enum):
    """Time horizons for future scenarios"""
    IMMEDIATE = "immediate"
    ONE_HOUR = "1h"
    SIX_HOURS = "6h"
    TWENTY_FOUR_HOURS = "24h"
    NO_ACTION = "no_action"


class DebateStatus(str, Enum):
    """Status of an agent debate"""
    INITIATED = "initiated"
    IN_PROGRESS = "in_progress"
    CONSENSUS_REACHED = "consensus_reached"
    ESCALATED = "escalated"
    RESOLVED = "resolved"


class CapitalType(str, Enum):
    """Types of organizational capital"""
    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    TRUST = "trust"
    REGULATORY = "regulatory"
    CYBER_RESILIENCE = "cyber_resilience"


# ============================================================================
# EVIDENCE & FINDINGS
# ============================================================================

class Evidence(BaseModel):
    """A piece of evidence supporting a finding or decision"""
    evidence_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source: str
    content: str
    confidence: float = Field(ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    evidence_type: str  # "log", "alert", "forensic", "intelligence", "metric"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Finding(BaseModel):
    """A finding from an agent's analysis"""
    finding_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent: DirectorAgentType
    title: str
    description: str
    severity: IncidentSeverity
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: List[Evidence] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    tags: List[str] = Field(default_factory=list)


# ============================================================================
# CRISIS CONTEXT
# ============================================================================

class CrisisContext(BaseModel):
    """The complete context of a crisis incident"""
    incident_id: str = Field(default_factory=lambda: f"INC-{uuid.uuid4().hex[:8].upper()}")
    incident_type: str
    severity: IncidentSeverity
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    description: str
    affected_entities: List[str] = Field(default_factory=list)
    evidence: List[Evidence] = Field(default_factory=list)
    findings: List[Finding] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Status tracking
    status: str = "active"  # "active", "contained", "resolved", "escalated"
    last_updated: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# AGENT MODELS
# ============================================================================

class AgentPersonality(BaseModel):
    """Personality traits that influence agent behavior"""
    risk_tolerance: float = Field(ge=0.0, le=1.0)  # 0=risk-averse, 1=risk-seeking
    cost_sensitivity: float = Field(ge=0.0, le=1.0)  # 0=cost-insensitive, 1=cost-focused
    speed_preference: float = Field(ge=0.0, le=1.0)  # 0=deliberate, 1=fast
    compliance_strictness: float = Field(ge=0.0, le=1.0)  # 0=flexible, 1=strict
    customer_focus: float = Field(ge=0.0, le=1.0)  # 0=internal, 1=customer-first


class AgentPosition(BaseModel):
    """An agent's position on a topic"""
    agent: DirectorAgentType
    position: str
    reasoning: str
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: List[Evidence] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AgentState(BaseModel):
    """Current state of a director agent"""
    agent_id: str
    agent_type: DirectorAgentType
    status: AgentStatus
    current_confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    current_position: Optional[str] = None
    trust_score: float = Field(ge=0.0, le=1.0, default=0.8)
    personality: AgentPersonality
    active_debates: List[str] = Field(default_factory=list)
    last_activity: datetime = Field(default_factory=datetime.utcnow)


class AgentTrustMetrics(BaseModel):
    """Trust metrics for an agent based on historical performance"""
    agent: DirectorAgentType
    
    # Historical Performance
    total_predictions: int = 0
    correct_predictions: int = 0
    accuracy_rate: float = Field(ge=0.0, le=1.0, default=0.8)
    
    # Reliability Metrics
    false_positive_rate: float = Field(ge=0.0, le=1.0, default=0.1)
    false_negative_rate: float = Field(ge=0.0, le=1.0, default=0.1)
    overconfidence_rate: float = Field(ge=0.0, le=1.0, default=0.15)
    
    # Decision Quality
    decision_reliability: float = Field(ge=0.0, le=1.0, default=0.85)
    prediction_accuracy: float = Field(ge=0.0, le=1.0, default=0.82)
    evidence_quality: float = Field(ge=0.0, le=1.0, default=0.88)
    
    # Trust Score
    overall_trust_score: float = Field(ge=0.0, le=1.0, default=0.85)
    
    # Trend
    trust_trend: str = "stable"  # "improving", "stable", "declining"
    last_updated: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# DEBATE SYSTEM
# ============================================================================

class DebateChallenge(BaseModel):
    """A challenge from one agent to another"""
    challenge_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    challenging_agent: DirectorAgentType
    challenged_agent: DirectorAgentType
    challenge_reason: str
    evidence: List[Evidence] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AgentDebate(BaseModel):
    """A debate between agents"""
    debate_id: str = Field(default_factory=lambda: f"DEBATE-{uuid.uuid4().hex[:8].upper()}")
    topic: str
    incident_id: str
    
    # Participants
    initiating_agent: DirectorAgentType
    challenged_agent: DirectorAgentType
    participating_agents: List[DirectorAgentType] = Field(default_factory=list)
    
    # Debate content
    challenge: DebateChallenge
    positions: List[AgentPosition] = Field(default_factory=list)
    
    # Status
    status: DebateStatus
    consensus_reached: bool = False
    consensus_confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    resolution: Optional[str] = None
    
    # Timestamps
    started_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None


# ============================================================================
# CRISIS FUTURES
# ============================================================================

class ImpactAssessment(BaseModel):
    """Assessment of impact in a specific dimension"""
    dimension: ImpactDimension
    severity: int = Field(ge=1, le=5)
    description: str
    quantified_value: Optional[float] = None  # e.g., dollar amount, hours, count
    unit: Optional[str] = None  # e.g., "USD", "hours", "users"
    confidence: float = Field(ge=0.0, le=1.0)


class PropagationNode(BaseModel):
    """A node in the crisis propagation path"""
    entity_id: str
    entity_name: str
    entity_type: EntityType
    impact_type: str
    impact_severity: int = Field(ge=1, le=5)
    time_to_impact: int  # minutes from incident start
    probability: float = Field(ge=0.0, le=1.0)
    mitigation_available: bool
    mitigation_cost: Optional[float] = None


class CrisisFuture(BaseModel):
    """A possible future scenario based on an action"""
    future_id: str = Field(default_factory=lambda: f"FUTURE-{uuid.uuid4().hex[:8].upper()}")
    scenario_name: str
    action: str
    time_horizon: TimeHorizon
    
    # Impact Dimensions
    financial_impact: ImpactAssessment
    operational_impact: ImpactAssessment
    regulatory_impact: ImpactAssessment
    customer_impact: ImpactAssessment
    reputation_impact: ImpactAssessment
    
    # Probability & Confidence
    probability: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    
    # Cascading Effects
    propagation_path: List[PropagationNode] = Field(default_factory=list)
    secondary_incidents: List[str] = Field(default_factory=list)
    
    # Metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    generated_by: List[DirectorAgentType] = Field(default_factory=list)


# ============================================================================
# PREDICTION MARKET
# ============================================================================

class AgentPrediction(BaseModel):
    """An agent's prediction about an action's outcome"""
    prediction_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent: DirectorAgentType
    action: str
    outcome_prediction: str
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    evidence: List[Evidence] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Trust-weighted confidence
    trust_weighted_confidence: Optional[float] = None


class PredictionMarket(BaseModel):
    """A prediction market for a specific action"""
    market_id: str = Field(default_factory=lambda: f"MARKET-{uuid.uuid4().hex[:8].upper()}")
    action: str
    incident_id: str
    predictions: List[AgentPrediction] = Field(default_factory=list)
    
    # Market consensus
    market_consensus: float = Field(ge=0.0, le=1.0, default=0.0)
    recommendation: str = "PENDING"  # "APPROVE", "REJECT", "PENDING"
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    closed_at: Optional[datetime] = None


# ============================================================================
# ORGANIZATIONAL DIGITAL TWIN
# ============================================================================

class OrganizationalEntity(BaseModel):
    """An entity in the organizational digital twin"""
    entity_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    entity_type: EntityType
    name: str
    description: str
    criticality: int = Field(ge=1, le=5)
    
    # Relationships
    dependencies: List[str] = Field(default_factory=list)  # entity_ids this depends on
    dependents: List[str] = Field(default_factory=list)    # entity_ids that depend on this
    
    # Metrics
    availability: float = Field(ge=0.0, le=1.0, default=1.0)
    health_score: float = Field(ge=0.0, le=1.0, default=1.0)
    
    # Business value
    revenue_impact: Optional[float] = None  # USD per day
    user_count: Optional[int] = None
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class DigitalTwin(BaseModel):
    """The complete organizational digital twin"""
    twin_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organization_name: str
    entities: Dict[str, OrganizationalEntity] = Field(default_factory=dict)
    
    # Graph metrics
    total_entities: int = 0
    critical_entities: int = 0
    total_dependencies: int = 0
    
    # Status
    last_updated: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# CRISIS CAPITAL
# ============================================================================

class CapitalMetric(BaseModel):
    """A metric for a specific type of capital"""
    capital_type: CapitalType
    current_value: float = Field(ge=0.0, le=100.0)
    baseline_value: float = Field(ge=0.0, le=100.0)
    change: float  # Can be negative
    change_percentage: float
    status: str  # "excellent", "strong", "moderate", "weak", "critical"


class CrisisCapital(BaseModel):
    """Organizational capital tracking during a crisis"""
    incident_id: str
    
    # Capital Metrics
    financial_capital: CapitalMetric
    operational_capital: CapitalMetric
    trust_capital: CapitalMetric
    regulatory_capital: CapitalMetric
    cyber_resilience_capital: CapitalMetric
    
    # Overall health
    overall_health: float = Field(ge=0.0, le=100.0)
    
    # Projections
    projected_recovery_time: int  # days
    projected_recovery_cost: float  # USD
    
    # Timestamps
    measured_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# DECISIONS
# ============================================================================

class AgentVote(BaseModel):
    """An agent's vote on a decision"""
    agent: DirectorAgentType
    vote: str  # "approve", "reject", "abstain"
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    conditions: List[str] = Field(default_factory=list)  # Conditions for approval


class BoardApprovalSimulation(BaseModel):
    """Simulation of board approval for an action"""
    action: str
    
    # Executive Personas
    ceo_approval_probability: float = Field(ge=0.0, le=1.0)
    cfo_approval_probability: float = Field(ge=0.0, le=1.0)
    cto_approval_probability: float = Field(ge=0.0, le=1.0)
    legal_approval_probability: float = Field(ge=0.0, le=1.0)
    board_approval_probability: float = Field(ge=0.0, le=1.0)
    
    # Concerns
    ceo_concerns: List[str] = Field(default_factory=list)
    cfo_concerns: List[str] = Field(default_factory=list)
    cto_concerns: List[str] = Field(default_factory=list)
    legal_concerns: List[str] = Field(default_factory=list)
    board_concerns: List[str] = Field(default_factory=list)
    
    # Overall
    overall_approval_probability: float = Field(ge=0.0, le=1.0)
    recommended_modifications: List[str] = Field(default_factory=list)


class CrisisDecision(BaseModel):
    """A decision made by the crisis council"""
    decision_id: str = Field(default_factory=lambda: f"DECISION-{uuid.uuid4().hex[:8].upper()}")
    incident_id: str
    action: str
    description: str
    
    # Council consensus
    council_consensus: float = Field(ge=0.0, le=1.0)
    agent_votes: Dict[str, AgentVote] = Field(default_factory=dict)
    
    # Analysis
    futures_analyzed: List[CrisisFuture] = Field(default_factory=list)
    board_approval_simulation: Optional[BoardApprovalSimulation] = None
    capital_impact: Optional[CrisisCapital] = None
    
    # Recommendation
    recommended: bool
    reasoning: str
    confidence: float = Field(ge=0.0, le=1.0)
    
    # Execution
    approved_by_human: Optional[bool] = None
    executed: bool = False
    execution_timestamp: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# EXECUTIVE INTERFACE
# ============================================================================

class ExecutiveQuestion(BaseModel):
    """A question from an executive to the crisis council"""
    question_id: str = Field(default_factory=lambda: f"Q-{uuid.uuid4().hex[:8].upper()}")
    question: str
    context: CrisisContext
    urgency: str = "normal"  # "immediate", "high", "normal"
    asked_by: str
    asked_at: datetime = Field(default_factory=datetime.utcnow)


class AgentResponse(BaseModel):
    """An agent's response to an executive question"""
    agent: DirectorAgentType
    response: str
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: List[Evidence] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class CouncilResponse(BaseModel):
    """The council's collective response to an executive question"""
    question: ExecutiveQuestion
    agent_responses: List[AgentResponse] = Field(default_factory=list)
    synthesized_answer: str
    confidence: float = Field(ge=0.0, le=1.0)
    supporting_evidence: List[Evidence] = Field(default_factory=list)
    dissenting_opinions: List[AgentResponse] = Field(default_factory=list)
    answered_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# EXECUTIVE BRIEFING
# ============================================================================

class ExecutiveBriefing(BaseModel):
    """Executive-level briefing on a crisis"""
    briefing_id: str = Field(default_factory=lambda: f"BRIEF-{uuid.uuid4().hex[:8].upper()}")
    incident_id: str
    
    # Summary
    title: str
    executive_summary: str
    current_status: str
    
    # Impact
    current_exposure: float  # USD
    affected_systems: int
    affected_customers: int
    regulatory_risk: str  # "low", "moderate", "high", "critical"
    
    # Recommendations
    recommended_actions: List[str] = Field(default_factory=list)
    confidence_level: float = Field(ge=0.0, le=1.0)
    estimated_time_to_recovery: str
    
    # Council consensus
    council_agreement: float = Field(ge=0.0, le=1.0)
    dissenting_views: List[str] = Field(default_factory=list)
    
    # Timestamps
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    generated_by: DirectorAgentType = DirectorAgentType.EXECUTIVE


# ============================================================================
# OVERSIGHT
# ============================================================================

class OversightChallenge(BaseModel):
    """A challenge from the oversight agent"""
    challenge_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    challenged_agent: DirectorAgentType
    challenged_claim: str
    challenge_reason: str
    severity: str  # "minor", "moderate", "major", "critical"
    evidence_quality: str  # "weak", "moderate", "strong"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class OversightReport(BaseModel):
    """Oversight agent's audit report"""
    report_id: str = Field(default_factory=lambda: f"OVERSIGHT-{uuid.uuid4().hex[:8].upper()}")
    decision_id: str
    
    # Audit results
    weak_reasoning_detected: List[str] = Field(default_factory=list)
    unsupported_claims: List[str] = Field(default_factory=list)
    invalid_assumptions: List[str] = Field(default_factory=list)
    missing_evidence: List[str] = Field(default_factory=list)
    logical_fallacies: List[str] = Field(default_factory=list)
    
    # Challenges issued
    challenges: List[OversightChallenge] = Field(default_factory=list)
    
    # Verdict
    verdict: str  # "approved", "approved_with_modifications", "rejected"
    modifications_required: List[str] = Field(default_factory=list)
    confidence_in_decision: float = Field(ge=0.0, le=1.0)
    
    # Timestamps
    audited_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# SYSTEM STATE
# ============================================================================

class CrisisOSState(BaseModel):
    """Overall state of the NEXAVARA CrisisOS"""
    system_id: str = Field(default_factory=lambda: "NEXAVARA-CRISISOS")
    
    # Active incidents
    active_incidents: List[str] = Field(default_factory=list)
    
    # Agent states
    agent_states: Dict[str, AgentState] = Field(default_factory=dict)
    
    # Active debates
    active_debates: List[str] = Field(default_factory=list)
    
    # Pending decisions
    pending_decisions: List[str] = Field(default_factory=list)
    
    # System health
    system_health: float = Field(ge=0.0, le=1.0, default=1.0)
    
    # Timestamps
    last_updated: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def calculate_trust_weighted_consensus(
    predictions: List[AgentPrediction],
    trust_metrics: Dict[DirectorAgentType, AgentTrustMetrics]
) -> float:
    """Calculate consensus weighted by agent trust scores"""
    if not predictions:
        return 0.0
    
    weighted_sum = 0.0
    total_weight = 0.0
    
    for prediction in predictions:
        trust = trust_metrics.get(prediction.agent)
        if trust:
            weight = prediction.confidence * trust.overall_trust_score
            weighted_sum += weight
            total_weight += trust.overall_trust_score
    
    return weighted_sum / total_weight if total_weight > 0 else 0.0


def calculate_capital_status(value: float) -> str:
    """Determine capital status from value"""
    if value >= 90:
        return "excellent"
    elif value >= 75:
        return "strong"
    elif value >= 60:
        return "moderate"
    elif value >= 40:
        return "weak"
    else:
        return "critical"

# Made with Bob
