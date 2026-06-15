"""ExecutiveAgent: Aggregates agent responses and makes final decisions."""

from messages import AgentRequest, AgentResponse, FinalDecision
from .crisis_base_agent import BaseAgent
from typing import Optional


ROLE_WEIGHTS = {
    "SecurityAgent": 0.4,
    "OperationsAgent": 0.2,
    "LegalAgent": 0.2,
    "FinanceAgent": 0.2,
}


class ExecutiveAgent(BaseAgent):
    """
    Aggregates responses from all specialized agents and produces
    a consolidated FinalDecision with executive-level recommendations.
    
    Responsibilities:
    - Receive AgentResponse objects from all agents
    - Calculate aggregated risk score
    - Synthesize action recommendations
    - Generate executive reasoning
    - Return FinalDecision
    """

    def __init__(self, coordinator: Optional[object] = None):
        super().__init__(role="ExecutiveAgent", coordinator=coordinator)

    def analyze(self, request: AgentRequest) -> AgentResponse:
        """
        ExecutiveAgent does not directly analyze incidents.
        
        Instead, use aggregate_responses() to synthesize agent responses.
        This method is included for interface compliance only.
        """
        # This is not the primary workflow for ExecutiveAgent
        raise NotImplementedError(
            "ExecutiveAgent.analyze() is not used directly. "
            "Call aggregate_responses(responses) instead."
        )

    def aggregate_responses(
        self, 
        incident_id: str,
        agent_responses: list[AgentResponse]
    ) -> FinalDecision:
        """
        Aggregate responses from all agents and produce final decision.
        
        Args:
            incident_id: The incident being analyzed
            agent_responses: List of AgentResponse objects from other agents
            
        Returns:
            FinalDecision with aggregated risk and action plan
        """
        if not agent_responses:
            raise ValueError("Must provide at least one agent response")
        
        # Calculate aggregated risk (weighted average with highest bias)
        risk_scores = [resp.risk_score for resp in agent_responses]
        confidences = [resp.confidence for resp in agent_responses]
        
        # Weighted average: higher weight to higher risk scores
        weighted_risk = sum(
            score * conf 
            for score, conf in zip(risk_scores, confidences)
        ) / sum(confidences) if sum(confidences) > 0 else sum(risk_scores) / len(risk_scores)
        
        # Ensure we bias toward higher risk in aggregation
        aggregated_risk = min(100.0, weighted_risk * 1.1)
        
        # Collect all recommended actions (deduplicate similar ones)
        all_actions = []
        for response in agent_responses:
            all_actions.extend(response.recommended_actions)
        
        # Remove duplicates while preserving order
        unique_actions = []
        seen = set()
        for action in all_actions:
            action_key = action.lower().strip()
            if action_key not in seen:
                seen.add(action_key)
                unique_actions.append(action)
        
        # Classify by risk level
        if aggregated_risk >= 80:
            severity_level = "CRITICAL"
            priority_actions = [a for a in unique_actions if any(
                word in a.lower() for word in ["isolate", "immediate", "activate", "emergency"]
            )]
            if not priority_actions:
                priority_actions = unique_actions[:3]
            else:
                priority_actions = priority_actions[:3]
        elif aggregated_risk >= 60:
            severity_level = "HIGH"
            priority_actions = unique_actions[:4]
        elif aggregated_risk >= 40:
            severity_level = "MEDIUM"
            priority_actions = unique_actions[:3]
        else:
            severity_level = "LOW"
            priority_actions = unique_actions[:2]
        
        # Ensure at least one action
        if not priority_actions:
            priority_actions = unique_actions[:1] if unique_actions else ["Continue monitoring"]
        
        # Build summary from agent analyses
        agent_summaries = [
            f"{resp.agent_role}: {resp.analysis}"
            for resp in agent_responses
        ]
        
        summary = (
            f"INCIDENT RESPONSE DECISION ({severity_level}): "
            f"Aggregated risk score {aggregated_risk:.1f}/100. "
            f"Executive decision: {len(priority_actions)} priority action(s) recommended. "
            f"Activate crisis response team immediately."
        )
        
        reasoning = (
            f"Analysis from {len(agent_responses)} specialized agents. "
            f"Risk factors: {', '.join([resp.agent_role for resp in agent_responses])}. "
            f"Highest risk score: {max(risk_scores)}. "
            f"Average confidence: {sum(confidences) / len(confidences):.2f}. "
            f"Recommendation: Execute priority actions within 15 minutes, "
            f"escalate to C-level leadership."
        )
        
        return FinalDecision(
            case_id=incident_id,
            summary=summary,
            aggregated_risk=aggregated_risk,
            final_action_plan=priority_actions,
            reasoning=reasoning
        )

    def decide_for_case(self, case_id: str) -> FinalDecision:
        """Read all agent.response events for a case from the coordinator,
        deterministically aggregate them and publish a final decision.
        """
        if not getattr(self, "coordinator", None):
            raise RuntimeError("ExecutiveAgent requires a coordinator to make decisions")

        msgs = self.coordinator.get_messages_by_case(case_id)
        # Filter agent.response events: payload shape varies, our coordinator stores payloads
        responses: list[AgentResponse] = []
        for m in msgs:
            if m.get("topic") == "agent.response":
                # payload may be AgentResponse dict or nested under payload
                payload = m.get("payload")
                try:
                    # payload may already be AgentResponse dict
                    resp = AgentResponse.model_validate(payload.get("payload") if payload.get("payload") else payload)
                except Exception:
                    try:
                        resp = AgentResponse.model_validate(payload)
                    except Exception:
                        continue
                responses.append(resp)

        if not responses:
            raise ValueError(f"No agent responses available for case {case_id}")

        # Deterministic aggregation using role weights and confidences
        num = 0.0
        den = 0.0
        for r in responses:
            w = ROLE_WEIGHTS.get(r.agent_role, 0.1)
            num += r.risk_score * w * r.confidence
            den += w * r.confidence

        aggregated_risk = float(num / den) if den > 0 else float(sum(r.risk_score for r in responses) / len(responses))

        # Build action list deterministically: unique in order
        all_actions = []
        for r in responses:
            all_actions.extend(r.recommended_actions)

        unique_actions = []
        seen = set()
        for a in all_actions:
            key = a.lower().strip()
            if key not in seen:
                seen.add(key)
                unique_actions.append(a)

        # Decision rules
        if aggregated_risk >= 75:
            final_status = "REJECTED"
        elif aggregated_risk >= 45:
            final_status = "APPROVED_WITH_CONDITIONS"
        else:
            final_status = "APPROVED"

        # Choose top 3 priority actions
        priority_actions = unique_actions[:3] if unique_actions else ["Continue monitoring"]

        summary = f"Decision {final_status}: aggregated risk {aggregated_risk:.1f}"
        reasoning = f"Aggregated from {len(responses)} agents; role weights applied; decision={final_status}."

        decision = FinalDecision(
            case_id=case_id,
            summary=summary,
            aggregated_risk=aggregated_risk,
            final_action_plan=priority_actions,
            reasoning=reasoning,
        )

        # Publish via coordinator
        self.coordinator.publish_final_decision(decision)

        return decision
