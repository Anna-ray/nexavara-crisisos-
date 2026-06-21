"""FinanceAgent: AI-enhanced financial impact analysis and recovery cost estimation."""

import logging
from typing import Optional, Any

from messages import AgentRequest, AgentResponse
from .ai_enhanced_agent import AIEnhancedAgent
from services.enhanced_ai_client import EnhancedAIClient

logger = logging.getLogger(__name__)


class FinanceAgent(AIEnhancedAgent):
    """
    AI-enhanced financial impact analysis agent.
    
    Uses AI/ML for intelligent assessment of:
    - Financial exposure estimation
    - Recovery cost projections
    - Insurance implications
    - Budget impact analysis
    """

    def __init__(self, coordinator: Optional[Any] = None, ai_client: Optional[EnhancedAIClient] = None):
        super().__init__(role="FinanceAgent", coordinator=coordinator, ai_client=ai_client)

    def analyze(self, request: AgentRequest) -> AgentResponse:
        """Analyze financial impact using AI/ML enhancement."""
        incident_type = request.context.get("type", "unknown").lower()
        severity = request.context.get("severity", 5)
        affected_systems = request.context.get("affected_systems", [])
        
        # Get AI-powered financial analysis
        description = f"Financial impact analysis: {incident_type}. Affected systems: {', '.join(affected_systems or ['unknown'])}. Severity: {severity}/10"
        ai_analysis = self.get_ai_analysis(description, request.context)
        ai_financial_exposure = ai_analysis.get("financial_exposure_per_minute", 50000.0)
        
        # System criticality cost factors ($ per minute of downtime)
        cost_factors = {
            "hospital": 50000,
            "banking": 100000,
            "ecommerce": 20000,
            "trading": 150000,
            "payment": 80000,
            "data_center": 30000,
            "standard": 50
        }
        
        # Identify highest cost system
        max_cost_per_min = cost_factors["standard"]
        for system in affected_systems:
            system_lower = system.lower()
            for cost_key, cost_value in cost_factors.items():
                if cost_key in system_lower and cost_value > max_cost_per_min:
                    max_cost_per_min = cost_value
                    break
        
        # Blend AI estimate with rule-based estimate
        estimated_cost_per_min = (max_cost_per_min + ai_financial_exposure) / 2
        
        # Estimate recovery costs and timeline
        recovery_days = 1 + (severity / 2)  # 1-5.5 days typical
        downtime_cost = int(estimated_cost_per_min * 60 * 24 * recovery_days)
        recovery_cost = int(downtime_cost * 0.3)  # 30% for recovery resources
        total_cost = downtime_cost + recovery_cost
        
        # AI-informed risk assessment
        ai_level = int(ai_analysis.get("severity_level", "Level 3").split()[-1])
        blended_level = (ai_level + (severity / 2)) / 2
        base_risk = int(blended_level * 15)
        if total_cost > 1000000:
            risk_score = min(100, base_risk + 25)
        elif total_cost > 500000:
            risk_score = min(100, base_risk + 15)
        else:
            risk_score = base_risk

        if severity < 5:
            risk_score = min(risk_score, 49)
        elif severity >= 8:
            risk_score = max(risk_score, 65)
        
        confidence = ai_analysis.get("confidence_score", 0.8)
        
        # Generate AI-enhanced analysis
        million_note = ""
        if total_cost >= 1_000_000:
            million_note = f" (~{total_cost/1_000_000:.1f} million)"

        analysis = (
            f"FINANCIAL IMPACT ANALYSIS (AI-Enhanced): Estimated total exposure ${total_cost:,} "
            f"(downtime: ${downtime_cost:,}, recovery: ${recovery_cost:,}). "
            f"AI assessment: {ai_analysis.get('root_cause', 'Analysis in progress')}. "
            f"Recovery timeline: ~{recovery_days:.1f} days." + million_note
        )

        if total_cost > 500_000:
            analysis = analysis + " Alert CFO and finance leadership immediately."
        
        # Build financial recommendations from AI output
        base_actions = ai_analysis.get('recommended_actions', [])[:1]
        actions = [
            f"Alert CFO and finance leadership of ${total_cost:,} exposure",
            f"Review insurance coverage for cyber incidents and business interruption",
            f"Prepare cost tracking mechanisms for incident response expenses",
            "Activate emergency procurement procedures for recovery resources",
            "Coordinate with budget holders for cost allocation"
        ] + base_actions

        return AgentResponse(
            agent_role=self.role,
            analysis=analysis,
            risk_score=min(100, risk_score),
            confidence=min(1.0, confidence),
            recommended_actions=actions
        )
