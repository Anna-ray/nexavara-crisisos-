from datetime import datetime, timezone

import pytest
from messages import AgentRequest, AgentResponse, FinalDecision, IncidentEvent


def test_incident_event_validation():
    event = IncidentEvent(
        id="INC-0001",
        type="ransomware",
        severity=8,
        description="Ransomware attack on hospital system",
        timestamp=datetime.now(timezone.utc),
    )

    assert event.id == "INC-0001"
    assert event.severity == 8


def test_agent_request_validation():
    request = AgentRequest(
        incident_id="INC-0001",
        context={"incident_type": "ransomware", "systems_affected": ["ehr"]},
        agent_role="SecurityAgent",
    )

    assert request.agent_role == "SecurityAgent"
    assert request.context["incident_type"] == "ransomware"


def test_agent_response_validation():
    response = AgentResponse(
        agent_role="FinanceAgent",
        analysis="Identified financial exposure and cash reserve impact.",
        risk_score=70,
        confidence=0.88,
        recommended_actions=["isolate impacted billing systems", "engage finance crisis team"],
    )

    assert response.risk_score == 70
    assert response.confidence == 0.88
    assert len(response.recommended_actions) == 2


def test_final_decision_validation():
    final = FinalDecision(
        case_id="INC-TEST-001",
        summary="Consolidated response plan for ransomware attack.",
        aggregated_risk=82.5,
        final_action_plan=["execute incident response playbook", "notify regulators"],
        reasoning="Risk aggregated across security, operations, legal, and finance analyses.",
    )

    assert final.aggregated_risk == 82.5
    assert "regulators" in final.final_action_plan[1]


def test_empty_agent_response_recommended_actions_raises():
    with pytest.raises(ValueError):
        AgentResponse(
            agent_role="LegalAgent",
            analysis="Legal review of data breach requirements.",
            risk_score=45,
            confidence=0.7,
            recommended_actions=[],
        )
