"""Base class for crisis response agents."""

from abc import ABC, abstractmethod
from typing import Optional, Any
from datetime import datetime, timezone

from messages import AgentRequest, AgentResponse
from messages.models import MessageEnvelope


class BaseAgent(ABC):
    """
    Abstract base class for crisis response agents.

    Agents consume AgentRequest objects and return AgentResponse objects.
    Band integration is supported through an optional BandClient.
    """

    def __init__(self, role: str, coordinator: Optional[Any] = None):
        """Initialize agent with a role identifier and optional BandCoordinator."""
        self.role = role
        self.coordinator = coordinator

    @abstractmethod
    def analyze(self, request: AgentRequest) -> AgentResponse:
        """
        Analyze the incident and return a structured response.

        Args:
            request: AgentRequest with incident context

        Returns:
            AgentResponse with analysis, risk score, confidence, and recommended actions
        """
        raise NotImplementedError

    @property
    def request_topic(self) -> str:
        return "agent.request"

    @property
    def response_topic(self) -> str:
        return "agent.response"

    def publish_response(self, response: AgentResponse, case_id: str) -> None:
        """Publish the agent response via the coordinator using the standard event schema."""
        if not getattr(self, "coordinator", None):
            raise RuntimeError("Coordinator is not configured for this agent")

        event = {
            "type": "agent.response",
            "agent": self.role,
            "case_id": case_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": response.model_dump(),
            "confidence": float(response.confidence),
        }

        # Delegate publish and logging to the coordinator
        self.coordinator.publish_event("agent.response", event)

    def handle_message(self, message: MessageEnvelope) -> None:
        """Handle an incoming Band message and respond if it is addressed to this agent."""
        request = AgentRequest.model_validate(message.payload)
        if request.agent_role != self.role:
            return

        response = self.analyze(request)
        # Publish using coordinator and include case id (incident id)
        case_id = request.incident_id
        self.publish_response(response, case_id)
