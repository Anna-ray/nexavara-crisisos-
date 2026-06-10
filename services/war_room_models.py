"""
War Room Data Models - Core data structures for agent collaboration
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from enum import Enum
import uuid
from pydantic import BaseModel, Field


class SeverityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AgentType(str, Enum):
    DETECTION = "detection"
    THREAT_INTELLIGENCE = "threat_intelligence"
    RISK_ASSESSMENT = "risk_assessment"
    COMPLIANCE = "compliance"
    RESPONSE = "response"
    EXECUTIVE = "executive"


class AgentStatus(str, Enum):
    IDLE = "idle"
    ANALYZING = "analyzing"
    WAITING = "waiting"
    ACTIVE = "active"
    COMPLETE = "complete"


class DecisionStatus(str, Enum):
    PROPOSED = "proposed"
    DEBATED = "debated"
    CONSENSUS = "consensus"
    HUMAN_REVIEW = "human_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"


# ============================================================================
# AGENT COMMUNICATION MODELS
# ============================================================================

class Evidence(BaseModel):
    """Evidence supporting a finding"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source: str  # e.g., "HSM telemetry", "Log aggregation", "Threat feed"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metric_name: str
    value: Any
    threshold: Optional[Any] = None
    severity: SeverityLevel
    confidence: float = Field(ge=0.0, le=1.0)
    raw_data: Optional[Dict[str, Any]] = None


class Finding(BaseModel):
    """A finding discovered or refined by an agent"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_type: AgentType
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    content: str  # What was found
    confidence: float = Field(ge=0.0, le=1.0)
    severity: SeverityLevel
    evidence_ids: List[str] = Field(default_factory=list)
    reasoning: str  # Why the agent believes this
    refinements: List[str] = Field(default_factory=list)  # IDs of refined versions


class AgentMessage(BaseModel):
    """Message from an agent to the war room"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_type: AgentType
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    content: str
    message_type: str  # "analysis", "challenge", "question", "proposal", "acknowledgment"
    confidence: float = Field(ge=0.0, le=1.0)
    referenced_findings: List[str] = Field(default_factory=list)
    targets_agent: Optional[AgentType] = None  # If challenging/questioning another agent


class Debate(BaseModel):
    """A debate between agents on a topic"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    initiated_by: AgentType
    challenged_agent: Optional[AgentType]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    topic: str  # What's being debated
    initial_position: str
    challenge_reason: str
    messages: List[AgentMessage] = Field(default_factory=list)
    resolution: Optional[str] = None
    status: DecisionStatus = DecisionStatus.PROPOSED
    disagreement_level: float = Field(ge=0.0, le=1.0)  # 0=agreement, 1=total disagreement


# ============================================================================
# INCIDENT & ANALYSIS MODELS
# ============================================================================

class IncidentType(str, Enum):
    RANSOMWARE = "ransomware"
    NATION_STATE = "nation_state"
    CLOUD_BREACH = "cloud_breach"
    SUPPLY_CHAIN = "supply_chain"
    POST_QUANTUM_FAILURE = "post_quantum_failure"
    IDENTITY_COMPROMISE = "identity_compromise"


class Incident(BaseModel):
    """Cyber incident being analyzed"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    incident_type: IncidentType
    detected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    title: str
    description: str
    severity: SeverityLevel = SeverityLevel.MEDIUM
    
    # Tracking
    finding_ids: List[str] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)
    decision_ids: List[str] = Field(default_factory=list)
    debate_ids: List[str] = Field(default_factory=list)
    
    # Analysis status
    detection_complete: bool = False
    threat_analysis_complete: bool = False
    risk_analysis_complete: bool = False
    compliance_analysis_complete: bool = False
    response_plan_complete: bool = False
    executive_briefing_complete: bool = False


class BusinessImpactAnalysis(BaseModel):
    """Quantified business impact"""
    financial_exposure: float  # In dollars
    affected_systems: int
    affected_customers: int
    revenue_at_risk_per_hour: float
    estimated_downtime_hours: float
    regulatory_fines_potential: float
    customer_churn_percentage: float
    reputational_damage_percentage: float
    
    # Totals
    total_financial_impact: float
    confidence: float = Field(ge=0.0, le=1.0)


class ComplianceAnalysis(BaseModel):
    """Regulatory and compliance implications"""
    regulations_affected: List[str]  # e.g., ["GDPR", "HIPAA", "SOC2"]
    notification_requirements: List[str]
    notification_timeline_hours: int
    regulatory_fines_potential: float
    legal_exposure_level: str  # LOW, MEDIUM, HIGH
    required_actions: List[str]
    confidence: float = Field(ge=0.0, le=1.0)


class ThreatAnalysis(BaseModel):
    """Threat intelligence analysis"""
    root_cause: str
    threat_actor_classification: str  # e.g., "state_sponsored", "criminal", "hacktivist"
    attack_vector: str
    attack_motive: str
    persistence_mechanisms: List[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)


class ResponseAction(BaseModel):
    """Proposed remediation action"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sequence: int
    action_name: str
    priority: str  # IMMEDIATE, HIGH, MEDIUM, LOW
    description: str
    estimated_duration_minutes: int
    required_approvals: List[str] = Field(default_factory=list)
    affected_systems: List[str] = Field(default_factory=list)
    risk_if_delayed: str


class ResponsePlan(BaseModel):
    """Complete response plan from Response Agent"""
    actions: List[ResponseAction]
    estimated_total_duration_minutes: int
    critical_path_actions: List[str]
    parallel_actions: List[List[str]]  # Actions that can run in parallel
    approval_required: bool
    confidence: float = Field(ge=0.0, le=1.0)


# ============================================================================
# DECISION & APPROVAL MODELS
# ============================================================================

class Decision(BaseModel):
    """A decision made by the war room"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    incident_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    decision_type: str  # "containment", "remediation", "communication", "investigation"
    proposed_by: List[AgentType]
    description: str
    reasoning: str
    affected_systems: List[str]
    
    # Debate
    debate_id: Optional[str] = None
    disagreement_level: float = Field(ge=0.0, le=1.0)
    
    # Confidence
    consensus_confidence: float = Field(ge=0.0, le=1.0)
    requires_human_approval: bool = False
    
    # Status
    status: DecisionStatus = DecisionStatus.PROPOSED
    human_approved_at: Optional[datetime] = None
    executed_at: Optional[datetime] = None


class ExecutiveBriefing(BaseModel):
    """Executive summary for leadership"""
    incident_id: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Key metrics
    current_severity: SeverityLevel
    current_status: str
    time_since_detection_minutes: int
    
    # Impact
    financial_exposure: float
    affected_systems: int
    affected_customers: int
    regulatory_risk_level: str
    
    # Actions
    immediate_actions: List[str]
    recommended_next_steps: List[str]
    
    # Narrative
    executive_summary: str
    key_talking_points: List[str]
    recommended_disclosure: str
    
    # Evidence
    confidence: float = Field(ge=0.0, le=1.0)
    supporting_evidence_count: int


# ============================================================================
# SHARED MEMORY MODELS
# ============================================================================

class MemoryGraph(BaseModel):
    """Shared knowledge graph accessible to all agents"""
    findings: List[Finding] = Field(default_factory=list)
    evidence: List[Evidence] = Field(default_factory=list)
    decisions: List[Decision] = Field(default_factory=list)
    debates: List[Debate] = Field(default_factory=list)
    messages: List[AgentMessage] = Field(default_factory=list)
    
    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    def get_findings_by_agent(self, agent_type: AgentType) -> List[Finding]:
        """Get all findings from a specific agent"""
        return [f for f in self.findings if f.agent_type == agent_type]
    
    def get_active_debates(self) -> List[Debate]:
        """Get unresolved debates"""
        return [d for d in self.debates if d.status in [DecisionStatus.PROPOSED, DecisionStatus.DEBATED]]
    
    def get_average_confidence(self) -> float:
        """Calculate average confidence across all findings"""
        if not self.findings:
            return 0.0
        return sum(f.confidence for f in self.findings) / len(self.findings)


# ============================================================================
# AGENT STATUS MODELS
# ============================================================================

class AgentStateSnapshot(BaseModel):
    """Current state of an agent"""
    agent_type: AgentType
    status: AgentStatus
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    current_task: Optional[str] = None
    findings_generated: int = 0
    debates_involved: int = 0
    last_message_at: Optional[datetime] = None
    confidence_average: float = Field(ge=0.0, le=1.0)


class WarRoomState(BaseModel):
    """Overall state of the war room"""
    incident_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Agents
    agent_states: Dict[AgentType, AgentStateSnapshot] = Field(default_factory=dict)
    
    # Incident progress
    overall_severity: SeverityLevel
    overall_confidence: float = Field(ge=0.0, le=1.0)
    analysis_progress_percentage: int = Field(ge=0, le=100)
    
    # Active debates
    active_debates_count: int = 0
    disagreement_level: float = Field(ge=0.0, le=1.0)
    
    # Decisions
    pending_decisions_count: int = 0
    decisions_approved_count: int = 0
    
    # Memory
    memory_graph: MemoryGraph = Field(default_factory=MemoryGraph)


# ============================================================================
# SIMULATION SCENARIO MODELS
# ============================================================================

class SimulationScenario(BaseModel):
    """Pre-defined incident scenario for testing"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    incident_type: IncidentType
    initial_evidence: List[Evidence]
    expected_severity: SeverityLevel
    expected_financial_impact: float
    expected_regulatory_impact: str
    
    # Progression
    progression_steps: List[Dict[str, Any]] = Field(default_factory=list)
    duration_minutes: int


class SimulationRunMetrics(BaseModel):
    """Metrics from a simulation run"""
    scenario_id: str
    run_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    
    # Detection
    detection_time_seconds: Optional[int] = None
    
    # Analysis
    threat_analysis_quality: float = Field(ge=0.0, le=1.0)
    risk_analysis_accuracy: float = Field(ge=0.0, le=1.0)
    compliance_analysis_completeness: float = Field(ge=0.0, le=1.0)
    
    # Decisions
    decision_quality: float = Field(ge=0.0, le=1.0)
    decision_time_minutes: int
    
    # Collaboration
    agent_debate_count: int
    average_debate_resolution_time_seconds: int
    agent_disagreement_resolution_rate: float = Field(ge=0.0, le=1.0)
    
    # Overall
    scenario_completion_percentage: int = Field(ge=0, le=100)
    judge_score: Optional[int] = None
