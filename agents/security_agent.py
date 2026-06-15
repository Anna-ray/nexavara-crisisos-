"""SecurityAgent: AI-enhanced security incident analysis and containment strategies."""

import logging
from typing import Optional, Any

from messages import AgentRequest, AgentResponse
from .ai_enhanced_agent import AIEnhancedAgent
from services.enhanced_ai_client import EnhancedAIClient

logger = logging.getLogger(__name__)


class SecurityAgent(AIEnhancedAgent):
    """
    AI-enhanced security incident analysis agent.
    
    Analyzes security incidents using AI/ML services for:
    - Intelligent threat assessment
    - Root cause analysis
    - Contextual containment strategies
    - Adaptive response recommendations
    """

    def __init__(self, coordinator: Optional[Any] = None, ai_client: Optional[EnhancedAIClient] = None):
        super().__init__(role="SecurityAgent", coordinator=coordinator, ai_client=ai_client)

    def analyze(self, request: AgentRequest) -> AgentResponse:
        """Analyze security incident using AI/ML enhancement."""
        incident_type = request.context.get("type", "unknown").lower()
        severity = request.context.get("severity", 5)
        description = f"Security incident: {incident_type}. Severity level: {severity}/10"
        
        # Get AI-powered analysis
        ai_analysis = self.get_ai_analysis(description, request.context)
        
        # Combine AI insights with input severity and security best practices
        ai_level = int(ai_analysis.get("severity_level", "Level 3").split()[-1])
        # Blend AI level with input severity for more accurate risk score
        combined_severity = (ai_level + (severity / 2)) / 2
        base_score = int(combined_severity * 17)  # Scale to 0-100
        confidence = ai_analysis.get("confidence_score", 0.75)
        
        # Build AI-informed analysis
        analysis = (
            f"SECURITY ASSESSMENT (AI-Enhanced): {incident_type.capitalize()} incident. "
            f"Root cause hypothesis: {ai_analysis.get('root_cause', 'Analysis pending')}. "
            f"Recommended immediate actions: {', '.join(ai_analysis.get('recommended_actions', [])[:2])}"
        )
        
        # Security-specific actions based on AI output
        base_actions = [
            "Document incident timeline with timestamps",
            "Preserve forensic evidence (logs, memory, disk snapshots)",
            "Alert security operations center"
        ]
        
        if severity >= 8:
            critical_actions = [
                "Isolate affected systems from network immediately",
                "Initiate live forensic imaging of compromised systems",
                "Block C&C communications at perimeter",
                "Activate full incident response team"
            ]
            actions = critical_actions + base_actions
        elif severity >= 5:
            medium_actions = [
                "Segment affected systems from production network",
                "Collect forensic evidence from compromised systems",
                "Monitor for lateral movement indicators"
            ]
            actions = medium_actions + base_actions
        else:
            actions = [
                "Deploy enhanced logging on affected systems",
                "Monitor for escalation indicators"
            ] + base_actions

        return AgentResponse(
            agent_role=self.role,
            analysis=analysis,
            risk_score=min(100, max(base_score, 85 if severity >= 8 else (60 if severity >= 5 else 40))),  # Ensure severity thresholds
            confidence=min(1.0, confidence),
            recommended_actions=actions
        )
