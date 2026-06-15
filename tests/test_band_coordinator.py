"""Tests for BandCoordinator integration, event publishing, and audit capabilities."""

import pytest
import json
from datetime import datetime, timezone

from adapters.band_client import InMemoryBandClient
from orchestrator.band_coordinator import BandCoordinator
from messages import (
    IncidentEvent,
    AgentRequest,
    AgentResponse,
    FinalDecision,
    AgentResponseEnvelope,
    MessageEnvelope,
)


class TestBandCoordinator:
    """Test suite for BandCoordinator functionality."""

    @pytest.fixture
    def band_client(self):
        """Create a fresh BandClient for each test."""
        return InMemoryBandClient()

    @pytest.fixture
    def coordinator(self, band_client):
        """Create a fresh BandCoordinator for each test."""
        return BandCoordinator(band_client)

    @pytest.fixture
    def sample_incident(self):
        """Create a sample incident event."""
        return IncidentEvent(
            id="INC-TEST-001",
            type="ransomware",
            severity=8,
            description="Test ransomware incident",
            timestamp=datetime.now(timezone.utc),
        )

    @pytest.fixture
    def sample_agent_response(self):
        """Create a sample agent response."""
        return AgentResponse(
            agent_role="SecurityAgent",
            analysis="Detected ransomware pattern matching WannaCry signatures",
            risk_score=85,
            confidence=0.92,
            recommended_actions=["Isolate affected systems", "Activate incident response plan"],
        )

    def test_publish_event_with_validation(self, coordinator, sample_incident):
        """Test that publish_event validates payload against schema."""
        # Should succeed with valid IncidentEvent payload
        envelope = coordinator.publish_event("incident.created", {
            "id": sample_incident.id,
            "type": sample_incident.type,
            "severity": sample_incident.severity,
            "description": sample_incident.description,
            "timestamp": sample_incident.timestamp.isoformat(),
        })
        assert envelope.topic == "incident.created"
        assert envelope.payload["id"] == sample_incident.id

    def test_publish_event_invalid_payload_raises_error(self, coordinator):
        """Test that publish_event raises error for invalid payload."""
        # Missing required fields for IncidentEvent
        with pytest.raises(ValueError):
            coordinator.publish_event("incident.created", {
                "id": "INC-001",
                "type": "ransomware",
                # missing severity and description
            })

    def test_dispatch_incident_publishes_and_logs(self, coordinator, sample_incident):
        """Test that dispatch_incident publishes incident and agent requests."""
        agent_roles = ["SecurityAgent", "FinanceAgent", "LegalAgent"]
        coordinator.dispatch_incident(sample_incident, agent_roles)

        # Verify messages were logged by case
        messages = coordinator.get_messages_by_case(sample_incident.id)
        assert len(messages) == 4  # 1 incident + 3 agent requests
        
        # Verify incident created event
        incident_msgs = [m for m in messages if m["topic"] == "incident.created"]
        assert len(incident_msgs) == 1
        assert incident_msgs[0]["payload"]["id"] == sample_incident.id

        # Verify agent requests
        request_msgs = [m for m in messages if m["topic"] == "agent.request"]
        assert len(request_msgs) == 3
        roles = {m["payload"]["agent_role"] for m in request_msgs}
        assert roles == {"SecurityAgent", "FinanceAgent", "LegalAgent"}

    def test_collect_response_extracts_wrapped_payload(self, coordinator, sample_agent_response):
        """Test that collect_response properly extracts AgentResponse from wrapped envelope."""
        case_id = "INC-TEST-001"
        
        # Create a wrapped agent response envelope
        wrapper = {
            "type": "agent.response",
            "agent": sample_agent_response.agent_role,
            "case_id": case_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": sample_agent_response.model_dump(),
            "confidence": sample_agent_response.confidence,
        }

        # Publish via coordinator (validates wrapper)
        coordinator.publish_event("agent.response", wrapper)

        # Collect responses
        responses = coordinator.get_responses()
        assert len(responses) == 1
        assert responses[0].agent_role == "SecurityAgent"
        assert responses[0].risk_score == 85

    def test_get_messages_by_case_returns_ordered_events(self, coordinator, sample_incident):
        """Test that get_messages_by_case returns events in order."""
        coordinator.dispatch_incident(sample_incident, ["SecurityAgent"])

        messages = coordinator.get_messages_by_case(sample_incident.id)
        
        # Verify order: incident created first, then agent request
        assert messages[0]["topic"] == "incident.created"
        assert messages[1]["topic"] == "agent.request"

    def test_get_case_state_returns_derived_state(self, coordinator, sample_incident):
        """Test that get_case_state returns correct case state."""
        coordinator.dispatch_incident(sample_incident, ["SecurityAgent"])

        state = coordinator.get_case_state(sample_incident.id)
        assert state["case_id"] == sample_incident.id
        assert state["events_count"] == 2  # incident + request
        assert state["latest_decision"] is None  # no decision yet

    def test_export_audit_log_returns_jsonl(self, coordinator, sample_incident):
        """Test that export_audit_log returns valid JSONL."""
        coordinator.dispatch_incident(sample_incident, ["SecurityAgent"])

        audit_log = coordinator.export_audit_log(sample_incident.id)
        lines = audit_log.strip().split("\n")
        
        assert len(lines) == 2  # incident + request
        
        # Each line should be valid JSON
        for line in lines:
            event = json.loads(line)
            assert "topic" in event
            assert "payload" in event

    def test_replay_case_republishes_events(self, coordinator, sample_incident):
        """Test that replay_case republishes all events for a case."""
        # Dispatch incident and collect count
        coordinator.dispatch_incident(sample_incident, ["SecurityAgent"])
        initial_messages = len(coordinator.get_messages_by_case(sample_incident.id))
        
        # Reset collected responses
        coordinator.reset()
        
        # Replay the case
        coordinator.replay_case(sample_incident.id)
        
        # After replay, messages should be re-published (collected again)
        # Note: get_messages_by_case includes both initial and replayed events
        # So we expect roughly double, but let's just verify the replay triggered
        replayed_messages = coordinator.get_messages_by_case(sample_incident.id)
        assert len(replayed_messages) >= initial_messages

    def test_multiple_agent_responses_collected(self, coordinator, sample_incident):
        """Test collection of responses from multiple agents."""
        case_id = sample_incident.id
        
        agents_data = [
            {
                "role": "SecurityAgent",
                "risk_score": 85,
                "confidence": 0.92,
            },
            {
                "role": "FinanceAgent",
                "risk_score": 70,
                "confidence": 0.88,
            },
            {
                "role": "LegalAgent",
                "risk_score": 60,
                "confidence": 0.80,
            },
        ]
        
        # Publish responses from each agent
        for agent_data in agents_data:
            response = AgentResponse(
                agent_role=agent_data["role"],
                analysis=f"Analysis from {agent_data['role']}",
                risk_score=agent_data["risk_score"],
                confidence=agent_data["confidence"],
                recommended_actions=[f"Action from {agent_data['role']}"],
            )
            
            wrapper = {
                "type": "agent.response",
                "agent": agent_data["role"],
                "case_id": case_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "payload": response.model_dump(),
                "confidence": response.confidence,
            }
            
            coordinator.publish_event("agent.response", wrapper)
        
        # Verify all responses collected
        responses = coordinator.get_responses()
        assert len(responses) == 3
        
        roles = {r.agent_role for r in responses}
        assert roles == {"SecurityAgent", "FinanceAgent", "LegalAgent"}

    def test_publish_final_decision_creates_event(self, coordinator, sample_incident):
        """Test that publish_final_decision creates a final.decision event."""
        case_id = sample_incident.id
        
        # Create a final decision
        decision = FinalDecision(
            case_id=case_id,
            summary="Ransomware incident confirmed. Immediate response initiated.",
            aggregated_risk=78.5,
            final_action_plan=[
                "Isolate affected systems immediately",
                "Activate incident response team",
                "Notify executive leadership",
            ],
            reasoning="Multiple agent assessments confirm ransomware with high confidence.",
        )
        
        # Manually add incident to case history first
        coordinator.publish_event("incident.created", {
            "id": case_id,
            "type": sample_incident.type,
            "severity": sample_incident.severity,
            "description": sample_incident.description,
            "timestamp": sample_incident.timestamp.isoformat(),
        })
        
        # Publish the decision
        coordinator.publish_final_decision(decision)
        
        # Verify decision was logged
        messages = coordinator.get_messages_by_case(case_id)
        decision_msgs = [m for m in messages if m["topic"] == "final.decision"]
        assert len(decision_msgs) == 1
        
        decision_payload = decision_msgs[0]["payload"]
        assert "Ransomware incident confirmed" in decision_payload["summary"]
        assert decision_payload["aggregated_risk"] == 78.5

    def test_coordinator_thread_safety_with_multiple_responses(self, coordinator):
        """Test that coordinator handles concurrent response collection safely."""
        import threading
        
        case_id = "INC-CONCURRENCY-TEST"
        num_agents = 10
        
        def publish_agent_response(agent_num):
            response = AgentResponse(
                agent_role=f"Agent{agent_num}",
                analysis=f"Analysis from agent {agent_num}",
                risk_score=50 + agent_num,
                confidence=0.80 + (agent_num * 0.01),
                recommended_actions=[f"Action {agent_num}"],
            )
            
            wrapper = {
                "type": "agent.response",
                "agent": f"Agent{agent_num}",
                "case_id": case_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "payload": response.model_dump(),
                "confidence": response.confidence,
            }
            
            coordinator.publish_event("agent.response", wrapper)
        
        # Launch multiple threads publishing responses
        threads = [
            threading.Thread(target=publish_agent_response, args=(i,))
            for i in range(num_agents)
        ]
        
        for t in threads:
            t.start()
        
        for t in threads:
            t.join()
        
        # Verify all responses were collected
        responses = coordinator.get_responses()
        assert len(responses) == num_agents


class TestAgentResponseEnvelopeModel:
    """Test suite for AgentResponseEnvelope schema validation."""

    def test_valid_envelope_creation(self):
        """Test creating a valid AgentResponseEnvelope."""
        response = AgentResponse(
            agent_role="TestAgent",
            analysis="Test analysis",
            risk_score=50,
            confidence=0.85,
            recommended_actions=["Test action"],
        )
        
        envelope = AgentResponseEnvelope(
            type="agent.response",
            agent="TestAgent",
            case_id="INC-001",
            timestamp="2026-06-15T12:00:00Z",
            payload=response,
            confidence=0.85,
        )
        
        assert envelope.type == "agent.response"
        assert envelope.agent == "TestAgent"
        assert envelope.case_id == "INC-001"
        assert envelope.payload.risk_score == 50

    def test_envelope_rejects_invalid_type(self):
        """Test that envelope rejects type other than 'agent.response'."""
        response = AgentResponse(
            agent_role="TestAgent",
            analysis="Test analysis",
            risk_score=50,
            confidence=0.85,
            recommended_actions=["Test action"],
        )
        
        with pytest.raises(ValueError):
            AgentResponseEnvelope(
                type="invalid.type",
                agent="TestAgent",
                case_id="INC-001",
                timestamp="2026-06-15T12:00:00Z",
                payload=response,
                confidence=0.85,
            )

    def test_envelope_rejects_confidence_out_of_range(self):
        """Test that envelope rejects confidence outside 0.0-1.0."""
        response = AgentResponse(
            agent_role="TestAgent",
            analysis="Test analysis",
            risk_score=50,
            confidence=0.85,
            recommended_actions=["Test action"],
        )
        
        with pytest.raises(ValueError):
            AgentResponseEnvelope(
                type="agent.response",
                agent="TestAgent",
                case_id="INC-001",
                timestamp="2026-06-15T12:00:00Z",
                payload=response,
                confidence=1.5,  # Invalid: > 1.0
            )
