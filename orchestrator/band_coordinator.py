from __future__ import annotations

from threading import Lock
from typing import Callable, Dict, Any, Optional, List
import json
from datetime import datetime, timezone

from adapters.band_client import BandClient
from messages import AgentRequest, AgentResponse, FinalDecision, IncidentEvent
from messages.models import MessageEnvelope, TOPIC_PAYLOAD_MODELS


class BandCoordinator:
    """
    Coordinates the incident request cycle and collects agent responses.

    This coordinator publishes incident creation events and dispatches
    agent-specific requests using the Band message bus. It collects all
    agent responses and publishes final decisions. All events are stored
    per-case for audit and replay.
    """

    def __init__(self, band_client: BandClient):
        self.band = band_client
        self._responses: Dict[str, list[AgentResponse]] = {}
        self._messages_by_case: Dict[str, list[dict[str, Any]]] = {}
        self._lock = Lock()
        self.subscribe_to_responses()

    def register_agent(self, handler: Callable[[MessageEnvelope], None]) -> None:
        """Register an agent handler for incoming agent requests.

        Agents should subscribe to the `agent.request` topic via this
        registration helper so the coordinator remains the single
        orchestration point.
        """
        self.band.subscribe("agent.request", handler)

    def dispatch_incident(
        self,
        incident: IncidentEvent,
        agent_roles: list[str],
        context: dict[str, Any] | None = None,
    ) -> None:
        """Publish incident creation and dispatch requests to all agents.

        This method uses `publish_event` to ensure all outgoing events
        are validated and logged.
        """
        incident_context = {
            "type": incident.type,
            "severity": incident.severity,
            "description": incident.description,
        }
        if context:
            incident_context.update(context)

        # Log and publish the incident created event
        self.publish_event("incident.created", {
            "id": incident.id,
            "type": incident.type,
            "severity": incident.severity,
            "description": incident.description,
            "timestamp": incident.timestamp.isoformat(),
        })

        # Create and publish an AgentRequest per role
        for role in agent_roles:
            request = AgentRequest(
                incident_id=incident.id,
                context=incident_context,
                agent_role=role,
            )
            # Use coordinator's publish to enforce schema and logging
            self.publish_event("agent.request", {
                "incident_id": request.incident_id,
                "context": request.context,
                "agent_role": request.agent_role,
            })

    def collect_response(self, envelope: MessageEnvelope) -> None:
        """Collect AgentResponseEnvelope objects published on the bus and log them.
        
        The envelope payload is an AgentResponseEnvelope wrapper containing:
        - type: "agent.response"
        - agent: agent role
        - case_id: incident ID
        - timestamp: ISO timestamp
        - payload: AgentResponse object
        - confidence: confidence level
        """
        # Extract the inner AgentResponse from the wrapper's payload field
        envelope_dict = envelope.payload
        if "payload" in envelope_dict and isinstance(envelope_dict["payload"], dict):
            # Inner payload is a dict (AgentResponse fields)
            response = AgentResponse.model_validate(envelope_dict["payload"])
        else:
            # Fallback: try to validate the entire envelope payload as AgentResponse
            response = AgentResponse.model_validate(envelope_dict)
        
        case_id = envelope_dict.get("case_id") or envelope_dict.get("incident_id")
        
        with self._lock:
            self._responses.setdefault(response.agent_role, []).append(response)
            # Also log the raw envelope for audit/replay
            if case_id:
                self._messages_by_case.setdefault(case_id, []).append({
                    "topic": envelope.topic,
                    "source": envelope.source,
                    "timestamp": envelope.timestamp.isoformat(),
                    "payload": envelope.payload,
                })

    def get_responses(self) -> list[AgentResponse]:
        """Return collected responses from the current incident run."""
        with self._lock:
            return [response for responses in self._responses.values() for response in responses]

    def reset(self) -> None:
        """Reset collected responses between incident runs."""
        with self._lock:
            self._responses.clear()

    def publish_final_decision(self, decision: FinalDecision) -> None:
        """Publish the executive final decision on the bus via publish_event."""
        self.publish_event("final.decision", {
            "case_id": decision.case_id,
            "summary": decision.summary,
            "aggregated_risk": decision.aggregated_risk,
            "final_action_plan": decision.final_action_plan,
            "reasoning": decision.reasoning,
        })

    def subscribe_to_responses(self) -> None:
        """Subscribe to the shared agent response topic for collection/logging."""
        self.band.subscribe("agent.response", self.collect_response)

    # ------------------------------------------------------------------
    # Coordinator Publishing, Auditing and Replay
    # ------------------------------------------------------------------
    def publish_event(self, topic: str, message: dict[str, Any]) -> MessageEnvelope:
        """Publish an event via Band with schema validation and audit logging.

        This method centralizes event composition so all events are consistently
        stamped and stored for replay/audit.
        """
        # Normalize case id from known fields
        case_id = message.get("case_id") or message.get("incident_id") or message.get("id")

        env_dict = {
            "source": "coordinator",
            "topic": topic,
            "payload": message,
        }

        # Validate envelope
        envelope = MessageEnvelope.model_validate(env_dict)

        # Validate payload model if available
        payload_model = TOPIC_PAYLOAD_MODELS.get(topic)
        if payload_model:
            try:
                payload_model.model_validate(message)
            except Exception as e:
                raise ValueError(f"Payload validation failed for topic '{topic}': {e}") from e

        # Log message into case history if case id present
        if case_id:
            with self._lock:
                self._messages_by_case.setdefault(case_id, []).append({
                    "topic": topic,
                    "source": envelope.source,
                    "timestamp": envelope.timestamp.isoformat(),
                    "payload": envelope.payload,
                })

        # Publish to underlying Band client
        self.band.publish(topic, envelope)
        return envelope

    def get_messages_by_case(self, case_id: str) -> List[dict[str, Any]]:
        """Return list of serialized events for the given case id."""
        with self._lock:
            return list(self._messages_by_case.get(case_id, []))

    def get_case_state(self, case_id: str) -> dict[str, Any]:
        """Return a simple derived state for the case based on collected events."""
        msgs = self.get_messages_by_case(case_id)
        decisions = [m for m in msgs if m["topic"] == "final.decision"]
        latest_decision = decisions[-1] if decisions else None
        return {
            "case_id": case_id,
            "events_count": len(msgs),
            "latest_decision": latest_decision,
        }

    def export_audit_log(self, case_id: str) -> str:
        """Export audit log for a case as JSON lines string (not writing files).

        Returns:
            JSONL string containing ordered events for the case.
        """
        msgs = self.get_messages_by_case(case_id)
        lines = [json.dumps(m, default=str) for m in msgs]
        return "\n".join(lines)

    def replay_case(self, case_id: str) -> None:
        """Replay all events for a case by republishing them to the Band client."""
        msgs = self.get_messages_by_case(case_id)
        for m in msgs:
            # Re-publish using the original topic and payload
            self.band.publish(m["topic"], {
                "source": m.get("source", "replay"),
                "topic": m["topic"],
                "payload": m["payload"],
            })
