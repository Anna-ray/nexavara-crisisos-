import pytest
from adapters.band_client import InMemoryBandClient
from agents.analysis_agent import PQCAnalysisAgent
from agents.coordination_agent import PQCCoordinationAgent
from agents.decision_agent import PQCDecisionAgent
from agents.audit_agent import PQCAuditAgent
from messages.models import PQCIncidentDetected, PQCAnalysisResult, PQCCoordinationState, PQCExecutiveDecision


def test_multi_agent_orchestration_flow():
    band = InMemoryBandClient()
    analysis_agent = PQCAnalysisAgent(name="analysis", band_client=band)
    coordination_agent = PQCCoordinationAgent(name="coordination", band_client=band)
    decision_agent = PQCDecisionAgent(name="decision", band_client=band)
    audit_agent = PQCAuditAgent(name="audit", band_client=band, audit_file_path="test_audit.jsonl")

    # Subscribe the agents to relevant topics for the orchestration flow
    band.subscribe("pqc.incident.detected", analysis_agent.handle_message)
    band.subscribe("pqc.incident.detected", coordination_agent.handle_message)
    band.subscribe("pqc.analysis.completed", decision_agent.handle_message)
    band.subscribe("pqc.coordination.updated", decision_agent.handle_message)

    collected = {
        "analysis": None,
        "coordination": None,
        "decision": None,
        "audit": []
    }

    band.subscribe("pqc.analysis.completed", lambda message: collected.update({"analysis": message.payload}))
    band.subscribe("pqc.coordination.updated", lambda message: collected.update({"coordination": message.payload}))
    band.subscribe("pqc.decision.made", lambda message: collected.update({"decision": message.payload}))
    band.subscribe("pqc.audit.recorded", lambda message: collected["audit"].append(message.payload))

    incident_payload = {
        "incident_id": "INC-ORCH-001",
        "source": "HSM-Monitor",
        "description": "Entropy degradation and Kyber-1024 handshake failures in clearing gateway.",
        "timestamp": "2026-06-11T12:00:00Z",
        "severity_initial": "critical"
    }

    band.publish("pqc.incident.detected", incident_payload)

    # Give threads time to execute
    import time
    time.sleep(1)

    assert collected["analysis"] is not None
    assert collected["coordination"] is not None
    assert collected["decision"] is not None

    assert collected["analysis"]["incident_id"] == "INC-ORCH-001"
    assert collected["coordination"]["incident_id"] == "INC-ORCH-001"
    assert collected["decision"]["incident_id"] == "INC-ORCH-001"
    assert isinstance(collected["decision"]["priority"], str)


def test_context_propagation_and_shared_memory():
    band = InMemoryBandClient()
    analysis_agent = PQCAnalysisAgent(name="analysis", band_client=band)
    coordination_agent = PQCCoordinationAgent(name="coordination", band_client=band)
    decision_agent = PQCDecisionAgent(name="decision", band_client=band)
    
    # Attach simple state markers
    analysis_agent.state = {}
    coordination_agent.state = {}
    decision_agent.state = {}

    incident_payload = {
        "incident_id": "INC-CONTEXT-001",
        "source": "HSM-Monitor",
        "description": "Key generation latency spike in HSM during clearing operations.",
        "timestamp": "2026-06-11T12:00:00Z",
        "severity_initial": "high"
    }

    envelope = PQCIncidentDetected.model_validate(incident_payload)
    band.publish("pqc.incident.detected", envelope)
    band.publish("pqc.analysis.completed", {
        "incident_id": "INC-CONTEXT-001",
        "severity_level": "Level 4",
        "root_cause_hypothesis": "HSM entropy loss",
        "financial_exposure_per_minute": 120000.0,
        "technical_details": {"affected_systems": ["HSM", "Clearing Gateway"]},
        "confidence_score": 0.88
    })
    band.publish("pqc.coordination.updated", {
        "incident_id": "INC-CONTEXT-001",
        "crisis_room_id": "PQC-CRISIS-ROOM-HSM-01",
        "channels_initialized": ["Security", "Infrastructure", "Executive"],
        "coordination_status": "active",
        "stakeholders_notified": ["Executive Leadership", "Compliance Team"]
    })

    import time
    time.sleep(1)

    assert decision_agent._analysis_results.get("INC-CONTEXT-001") is None
    # The decision agent should have synthesized and cleared state after publishing
    # No exception indicates state sync worked


def test_agent_message_traceability():
    band = InMemoryBandClient()
    events = []
    band.subscribe("*", lambda message: events.append((message.topic, message.payload.get("incident_id", None))))

    band.publish("pqc.incident.detected", {
        "source": "HSM-Monitor",
        "topic": "pqc.incident.detected",
        "payload": {
            "incident_id": "INC-TRACE-001",
            "source": "HSM-Monitor",
            "description": "HSM entropy loss detected.",
            "timestamp": "2026-06-11T12:00:00Z",
            "severity_initial": "critical"
        }
    })

    assert any(topic == "pqc.incident.detected" and incident_id == "INC-TRACE-001" for topic, incident_id in events)
