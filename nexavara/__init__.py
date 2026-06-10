"""
NEXAVARA CrisisOS - Crisis Intelligence Operating System

The world's first autonomous crisis intelligence operating system.
"""

__version__ = "1.0.0"
__author__ = "NEXAVARA Team"

from .core_models import (
    # Enums
    DirectorAgentType,
    AgentStatus,
    IncidentSeverity,
    EntityType,
    ImpactDimension,
    TimeHorizon,
    DebateStatus,
    CapitalType,
    
    # Core Models
    CrisisContext,
    Evidence,
    Finding,
    
    # Agent Models
    AgentState,
    AgentPosition,
    AgentTrustMetrics,
    AgentPrediction,
    
    # Debate Models
    AgentDebate,
    DebateChallenge,
    
    # Future Models
    CrisisFuture,
    ImpactAssessment,
    PropagationNode,
    
    # Decision Models
    CrisisDecision,
    AgentVote,
    BoardApprovalSimulation,
    
    # Digital Twin
    OrganizationalEntity,
    DigitalTwin,
    
    # Capital
    CrisisCapital,
    CapitalMetric,
    
    # Executive Interface
    ExecutiveQuestion,
    CouncilResponse,
    ExecutiveBriefing,
    
    # Oversight
    OversightReport,
    OversightChallenge,
    
    # System State
    CrisisOSState,
)

__all__ = [
    # Enums
    "DirectorAgentType",
    "AgentStatus",
    "IncidentSeverity",
    "EntityType",
    "ImpactDimension",
    "TimeHorizon",
    "DebateStatus",
    "CapitalType",
    
    # Core Models
    "CrisisContext",
    "Evidence",
    "Finding",
    
    # Agent Models
    "AgentState",
    "AgentPosition",
    "AgentTrustMetrics",
    "AgentPrediction",
    
    # Debate Models
    "AgentDebate",
    "DebateChallenge",
    
    # Future Models
    "CrisisFuture",
    "ImpactAssessment",
    "PropagationNode",
    
    # Decision Models
    "CrisisDecision",
    "AgentVote",
    "BoardApprovalSimulation",
    
    # Digital Twin
    "OrganizationalEntity",
    "DigitalTwin",
    
    # Capital
    "CrisisCapital",
    "CapitalMetric",
    
    # Executive Interface
    "ExecutiveQuestion",
    "CouncilResponse",
    "ExecutiveBriefing",
    
    # Oversight
    "OversightReport",
    "OversightChallenge",
    
    # System State
    "CrisisOSState",
]

# Made with Bob
