from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Literal, List
from pydantic import BaseModel, Field, field_validator
import uuid
import hashlib
import json


# Core envelope model used at the Band boundary
class MessageEnvelope(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str
    topic: str
    payload: Dict[str, Any]


# Domain message models (typed payloads)
class EscalationCreated(BaseModel):
    escalation_id: str
    source: str
    content: str
    urgency: Dict[str, Any]  # e.g. {"level": "high", "score": 0.95}


class EscalationTask(BaseModel):
    escalation_id: str
    action: str
    assigned_to: str
    urgency: Literal["low", "medium", "high", "critical"] | str


class AnalysisCompleted(BaseModel):
    escalation_id: str
    root_cause: str
    confidence: float
    evidence: list[str] = []
    ai_analysis: Optional[Dict[str, Any]] = None


class DecisionRequest(BaseModel):
    escalation_id: str
    context: Dict[str, Any]
    request: str


class DecisionMade(BaseModel):
    escalation_id: str
    recommendation: str
    rationale: str
    confidence: float
    analyses_count: int


# ============================================================================
# PQC (Post-Quantum Cryptographic) Crisis Scenario Models
# ============================================================================


class PQCIncidentDetected(BaseModel):
    """
    Initial incident detection payload for PQC cryptographic crisis.
    
    Represents the first alert when a quantum-related cryptographic
    vulnerability or incident is detected in the system.
    """
    incident_id: str
    source: str = Field(..., description="Source system, e.g., 'HSM-Monitor'")
    description: str = Field(..., description="Full incident description")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    severity_initial: str = Field(
        default="unknown",
        description="Initial severity assessment: unknown, low, medium, high, critical"
    )


class PQCAnalysisResult(BaseModel):
    """
    Analysis agent output for PQC incident assessment.
    
    Contains detailed technical analysis, severity classification,
    and financial impact estimation for the cryptographic incident.
    """
    incident_id: str
    severity_level: Literal["Level 1", "Level 2", "Level 3", "Level 4", "Level 5"]
    root_cause_hypothesis: str
    financial_exposure_per_minute: float = Field(
        ...,
        description="Estimated financial exposure in dollars per minute"
    )
    technical_details: Dict[str, Any]
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")


class PQCCoordinationState(BaseModel):
    """
    Coordination agent output for crisis management state.
    
    Tracks the initialization and status of crisis response channels,
    stakeholder notifications, and overall coordination state.
    """
    incident_id: str
    crisis_room_id: str = Field(..., description="Crisis room identifier, e.g., 'PQC-CRISIS-ROOM-HSM-01'")
    channels_initialized: List[str] = Field(
        default_factory=list,
        description="List of initialized channels, e.g., ['Network', 'Security', 'Infrastructure']"
    )
    coordination_status: Literal["initializing", "active", "escalated", "resolved"]
    stakeholders_notified: List[str] = Field(default_factory=list)


class PQCExecutiveDecision(BaseModel):
    """
    Decision agent output for executive-level crisis decisions.
    
    Provides actionable recommendations, risk assessment, and
    priority classification for executive decision-making.
    """
    incident_id: str
    recommendation: str = Field(..., description="Actionable directive for crisis response")
    risk_matrix: Dict[str, Any] = Field(
        ...,
        description="Risk assessment including: immediate_action, fallback_mechanism, compliance_risks, regulatory_impact"
    )
    estimated_downtime_minutes: Optional[int] = None
    approval_required: bool
    priority: Literal["P0", "P1", "P2", "P3"]


class PQCAuditRecord(BaseModel):
    """
    Audit agent output for forensic record-keeping.
    
    Creates immutable audit trail with cryptographic hash for
    compliance and post-incident analysis.
    """
    audit_id: str
    incident_id: str
    event_type: str
    agent_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payload_snapshot: Dict[str, Any]
    forensic_hash: str = Field(..., description="SHA-256 hash of the record for immutability")
    
    @field_validator('forensic_hash')
    @classmethod
    def validate_hash_format(cls, v: str) -> str:
        """Validate that forensic_hash is a valid SHA-256 hex string."""
        if len(v) != 64 or not all(c in '0123456789abcdef' for c in v.lower()):
            raise ValueError('forensic_hash must be a valid SHA-256 hex string (64 characters)')
        return v.lower()
    
    @classmethod
    def create_with_hash(cls, **kwargs) -> 'PQCAuditRecord':
        """
        Factory method to create an audit record with auto-generated forensic hash.
        
        The hash is computed from the serialized payload_snapshot for immutability.
        """
        if 'forensic_hash' not in kwargs and 'payload_snapshot' in kwargs:
            payload_json = json.dumps(kwargs['payload_snapshot'], sort_keys=True)
            kwargs['forensic_hash'] = hashlib.sha256(payload_json.encode()).hexdigest()
        return cls(**kwargs)


class IncidentEvent(BaseModel):
    id: str = Field(..., min_length=1, description="Unique incident identifier")
    type: str = Field(..., min_length=1, description="Incident classification type")
    severity: int = Field(..., ge=1, le=10, description="Severity rating from 1 to 10")
    description: str = Field(..., min_length=1, description="Incident description")
    timestamp: datetime = Field(..., description="Time when the incident was created")

    model_config = {
        "extra": "forbid"
    }

    @field_validator("id")
    @classmethod
    def validate_id(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("id must be a non-empty string")
        return value


class AgentRequest(BaseModel):
    incident_id: str = Field(..., min_length=1, description="Identifier of the incident being requested")
    context: Dict[str, Any] = Field(..., description="Current incident context for agent analysis")
    agent_role: str = Field(..., min_length=1, description="Role of the agent receiving the request")

    model_config = {
        "extra": "forbid"
    }

    @field_validator("incident_id", "agent_role")
    @classmethod
    def validate_non_empty_string(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("value must be a non-empty string")
        return value


class AgentResponse(BaseModel):
    agent_role: str = Field(..., min_length=1, description="Agent role generating the response")
    analysis: str = Field(..., min_length=1, description="Structured analysis summary")
    risk_score: int = Field(..., ge=0, le=100, description="Risk score from 0 to 100")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence level from 0.0 to 1.0")
    recommended_actions: list[str] = Field(..., description="List of recommended actions from the agent")

    model_config = {
        "extra": "forbid"
    }

    @field_validator("agent_role", "analysis")
    @classmethod
    def validate_non_empty_string(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("value must be a non-empty string")
        return value

    @field_validator("recommended_actions")
    @classmethod
    def validate_recommended_actions(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("recommended_actions must contain at least one action")
        return value


class FinalDecision(BaseModel):
    case_id: str = Field(..., min_length=1, description="Case/incident ID this decision applies to")
    summary: str = Field(..., min_length=1, description="Executive summary of the final decision")
    aggregated_risk: float = Field(..., ge=0.0, le=100.0, description="Aggregated risk score from all agent inputs")
    final_action_plan: list[str] = Field(..., description="Final approved action plan items")
    reasoning: str = Field(..., min_length=1, description="Executive reasoning behind the final decision")

    model_config = {
        "extra": "forbid"
    }

    @field_validator("summary", "reasoning")
    @classmethod
    def validate_non_empty_string(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("value must be a non-empty string")
        return value

    @field_validator("final_action_plan")
    @classmethod
    def validate_final_action_plan(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("final_action_plan must contain at least one action")
        return value


class AgentResponseEnvelope(BaseModel):
    """Wrapper envelope for agent response events published on the event bus.
    
    Includes metadata (type, agent, case_id, timestamp, confidence) along with
    the structured AgentResponse payload for audit and coordination purposes.
    """
    type: str = Field(..., description="Event type, always 'agent.response'")
    agent: str = Field(..., min_length=1, description="Agent role that produced this response")
    case_id: str = Field(..., min_length=1, description="Case/incident ID for this response")
    timestamp: str = Field(..., description="ISO 8601 timestamp when the response was generated")
    payload: AgentResponse = Field(..., description="The structured agent response payload")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Overall confidence level for the response")

    model_config = {
        "extra": "forbid"
    }

    @field_validator("type")
    @classmethod
    def validate_type(cls, value: str) -> str:
        if value != "agent.response":
            raise ValueError("type must be 'agent.response'")
        return value


# Topic -> payload model mapping used by the BandClient validator
TOPIC_PAYLOAD_MODELS: Dict[str, type] = {
    # Customer support escalation topics
    "escalation.created": EscalationCreated,
    "escalation.task": EscalationTask,
    "analysis.completed": AnalysisCompleted,
    "decision.request": DecisionRequest,
    "decision.made": DecisionMade,
    
    # PQC (Post-Quantum Cryptographic) crisis topics
    "pqc.incident.detected": PQCIncidentDetected,
    "pqc.analysis.completed": PQCAnalysisResult,
    "pqc.coordination.updated": PQCCoordinationState,
    "pqc.decision.made": PQCExecutiveDecision,
    "pqc.audit.recorded": PQCAuditRecord,
    "incident.created": IncidentEvent,
    "agent.request": AgentRequest,
    "agent.response": AgentResponseEnvelope,
    "final.decision": FinalDecision,
}
