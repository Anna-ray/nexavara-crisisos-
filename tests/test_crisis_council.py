from nexavara.crisis_council import ThreatDirectorAgent, RiskDirectorAgent, BaseDirectorAgent
from nexavara.core_models import CrisisContext, IncidentSeverity


def make_crisis_context(description: str, severity: IncidentSeverity = IncidentSeverity.HIGH):
    return CrisisContext(
        incident_type="post_quantum_failure",
        severity=severity,
        description=description,
        affected_entities=["HSM", "Clearing Gateway"]
    )


def test_threat_director_analysis_and_trust_metrics():
    agent = ThreatDirectorAgent()
    context = make_crisis_context("Detected HSM entropy depletion and handshake failures during PQC key exchange.")
    finding = agent.analyze_crisis(context)

    assert finding.agent == agent.agent_type
    assert finding.severity in [IncidentSeverity.CRITICAL, IncidentSeverity.CATASTROPHIC, IncidentSeverity.HIGH]
    assert agent.current_context == context
    assert agent.memory[-1]["finding"]["agent"] == agent.agent_type
    assert "Threat Assessment" in agent.memory[-1]["finding"]["title"]

    agent.update_trust_metrics(correct=True)
    assert agent.trust_metrics.total_predictions == 1
    assert agent.trust_metrics.correct_predictions == 1
    assert agent.trust_metrics.trust_trend in ["improving", "stable"]


def test_risk_director_position_and_role_description():
    agent = RiskDirectorAgent()
    assert "Risk" in agent.get_role_description()
    assert len(agent.get_key_questions()) > 0

    context = make_crisis_context("Key exchange performance issue due to HSM entropy drains.")
    position = agent.form_position("risk assessment", context)

    assert position.agent == agent.agent_type
    assert position.confidence >= 0.0
    assert isinstance(position.position, str)
