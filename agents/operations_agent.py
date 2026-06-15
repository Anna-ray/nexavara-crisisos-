"""OperationsAgent: AI-enhanced operational disruption analysis."""

import logging
from typing import Optional, Any

from messages import AgentRequest, AgentResponse
from .ai_enhanced_agent import AIEnhancedAgent
from services.enhanced_ai_client import EnhancedAIClient

logger = logging.getLogger(__name__)


class OperationsAgent(AIEnhancedAgent):
    """
    AI-enhanced operational impact analysis agent.
    
    Uses AI/ML for intelligent assessment of:
    - Operational disruption impact
    - Service dependency analysis
    - Recovery complexity estimation
    - Resource allocation recommendations
    """

    def __init__(self, coordinator: Optional[Any] = None, ai_client: Optional[EnhancedAIClient] = None):
        super().__init__(role="OperationsAgent", coordinator=coordinator, ai_client=ai_client)

    def analyze(self, request: AgentRequest) -> AgentResponse:
        """Analyze operational impact using AI/ML enhancement."""
        incident_type = request.context.get("type", "unknown").lower()
        severity = request.context.get("severity", 5)
        affected_systems = request.context.get("affected_systems", [])
        
        # Get AI-powered analysis
        description = f"Operational impact analysis: {incident_type} affecting {', '.join(affected_systems or ['unknown systems'])}. Severity: {severity}/10"
        ai_analysis = self.get_ai_analysis(description, request.context)
        
        # Determine system criticality
        critical_systems = {
            "ehr", "hospital", "patient", "healthcare", "medical",
            "banking", "trading", "payment", "atm", "transaction",
            "power", "grid", "scada", "infrastructure"
        }
        
        critical_count = sum(1 for sys in affected_systems if any(
            crit in sys.lower() for crit in critical_systems
        ))
        
        # AI-informed risk calculation
        base_risk = int(ai_analysis.get("severity_level", "Level 3").split()[-1]) * 17
        critical_multiplier = 1.0 + (critical_count * 0.25)
        risk_score = min(100, int(base_risk * critical_multiplier))
        confidence = ai_analysis.get("confidence_score", 0.75)
        
        # AI-enhanced analysis text
        analysis = (
            f"OPERATIONAL IMPACT ANALYSIS (AI-Enhanced): {incident_type} incident. "
            f"Affected systems: {', '.join(affected_systems or ['TBD'])}. "
            f"AI-projected recovery strategy: {ai_analysis.get('recommended_actions', ['See AI output'])[0]}"
        )
        
        # Build operations-specific actions from AI output
        base_actions = ai_analysis.get('recommended_actions', [])[:2]
        
        if critical_count > 0:
            critical_actions = [
                f"Activate disaster recovery procedures for {critical_count} critical system(s)",
                "Establish alternative communication channels",
                "Prepare failover resources and standby systems"
            ]
            actions = critical_actions + base_actions
        else:
            standard_actions = [
                "Assess operational dependencies for affected systems",
                "Prepare system restoration procedures",
                "Coordinate with affected service owners"
            ]
            actions = standard_actions + base_actions

        return AgentResponse(
            agent_role=self.role,
            analysis=analysis,
            risk_score=risk_score,
            confidence=min(1.0, confidence),
            recommended_actions=actions
        )
