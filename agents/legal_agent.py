"""LegalAgent: AI-enhanced legal and compliance analysis."""

import logging
from typing import Optional, Any

from messages import AgentRequest, AgentResponse
from .ai_enhanced_agent import AIEnhancedAgent
from services.enhanced_ai_client import EnhancedAIClient

logger = logging.getLogger(__name__)


class LegalAgent(AIEnhancedAgent):
    """
    AI-enhanced legal and compliance analysis agent.
    
    Uses AI/ML for intelligent assessment of:
    - Regulatory compliance obligations
    - Notification requirements
    - Liability exposure
    - Industry-specific regulations
    """

    def __init__(self, coordinator: Optional[Any] = None, ai_client: Optional[EnhancedAIClient] = None):
        super().__init__(role="LegalAgent", coordinator=coordinator, ai_client=ai_client)

    def analyze(self, request: AgentRequest) -> AgentResponse:
        """Analyze legal and compliance obligations using AI/ML."""
        incident_type = request.context.get("type", "unknown").lower()
        severity = request.context.get("severity", 5)
        affected_systems = request.context.get("affected_systems", [])
        
        # Get AI-powered compliance analysis
        description = f"Legal compliance analysis: {incident_type} incident. Affected systems: {', '.join(affected_systems or ['unknown'])}. Severity: {severity}/10"
        ai_analysis = self.get_ai_analysis(description, request.context)
        
        # Identify regulated industries (heuristic + AI)
        regulated_systems = {
            "healthcare": ["ehr", "patient", "medical", "hospital", "hipaa"],
            "financial": ["banking", "payment", "trading", "atm", "pci-dss"],
            "government": ["dod", "federal", "government", "compliance"],
            "data_privacy": ["gdpr", "ccpa", "pii", "personal_data"]
        }
        
        # Determine which regulations apply
        applicable_regs = []
        for industry, keywords in regulated_systems.items():
            if any(keyword in " ".join(affected_systems).lower() for keyword in keywords):
                applicable_regs.append(industry)
        
        # AI-informed risk assessment
        base_risk = int(ai_analysis.get("severity_level", "Level 3").split()[-1]) * 15
        reg_multiplier = 1.0 + (len(applicable_regs) * 0.2)
        risk_score = min(100, int(base_risk * reg_multiplier))
        confidence = ai_analysis.get("confidence_score", 0.75)
        
        # Generate AI-enhanced analysis and actions
        if applicable_regs:
            reg_text = ", ".join(applicable_regs).upper()
            analysis = (
                f"REGULATORY EXPOSURE (AI-Enhanced): {reg_text} compliance obligations triggered. "
                f"AI assessment: {ai_analysis.get('root_cause', 'Analysis pending')}. "
                f"Notification and reporting requirements likely mandatory."
            )
            base_actions = ai_analysis.get('recommended_actions', [])[:2]
            actions = [
                f"Initiate legal review for {', '.join(applicable_regs)} regulations",
                "Identify affected customer/patient count for notification threshold analysis",
                "Prepare notification templates required by applicable regulations",
                "Coordinate with compliance and legal teams"
            ] + base_actions
        else:
            analysis = (
                f"LEGAL REVIEW REQUIRED: Apply incident response standards. "
                f"AI-assisted assessment: {ai_analysis.get('root_cause', 'Analysis in progress')}. "
                f"Assess contractual obligations with customers and partners."
            )
            base_actions = ai_analysis.get('recommended_actions', [])[:2]
            actions = [
                "Conduct incident legal review",
                "Assess contractual breach notification requirements",
                "Review applicable company policies",
                "Document incident for potential litigation"
            ] + base_actions

        return AgentResponse(
            agent_role=self.role,
            analysis=analysis,
            risk_score=risk_score,
            confidence=min(1.0, confidence),
            recommended_actions=actions
        )
