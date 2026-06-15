"""Production-ready REST API for NEXAVARA Crisis Operating System.

Provides:
- Incident creation and management
- Real-time case status tracking
- Executive decision requests
- Audit log export
- Health checks and metrics
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from config import Config, setup_logging
from messages import IncidentEvent, FinalDecision, AgentRequest
from orchestrator.enhanced_coordinator import EnhancedCoordinator
from agents.executive_agent import ExecutiveAgent

logger = logging.getLogger(__name__)

# Initialize logging
setup_logging()


# ============================================================================
# Request/Response Models
# ============================================================================

class IncidentCreateRequest(BaseModel):
    """Request to create a new incident."""
    incident_type: str = Field(..., description="Type of incident (e.g., 'ransomware', 'data_breach')")
    severity: int = Field(..., ge=1, le=10, description="Severity level from 1 to 10")
    description: str = Field(..., min_length=1, description="Full incident description")
    affected_systems: Optional[List[str]] = Field(default=None, description="List of affected systems")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")


class IncidentResponse(BaseModel):
    """Response containing incident details."""
    incident_id: str
    type: str
    severity: int
    description: str
    status: str = "created"
    timestamp: str


class CaseStatusResponse(BaseModel):
    """Response containing case status and responses."""
    case_id: str
    events_count: int
    responses_collected: int
    status: str
    latest_decision: Optional[Dict[str, Any]] = None
    timestamp: str


class DecisionRequest(BaseModel):
    """Request to make a final decision on a case."""
    case_id: str = Field(..., description="Case ID for which to make a decision")


class DecisionResponse(BaseModel):
    """Response containing final decision."""
    case_id: str
    summary: str
    aggregated_risk: float
    final_action_plan: List[str]
    reasoning: str
    timestamp: str


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    environment: str
    services: Dict[str, bool]
    timestamp: str


# ============================================================================
# FastAPI Application
# ============================================================================

class NexavaraAPI:
    """NEXAVARA Crisis Operating System REST API."""
    
    def __init__(self, coordinator: EnhancedCoordinator, executive_agent: ExecutiveAgent):
        """Initialize API with coordinator and executive agent."""
        self.app = FastAPI(
            title="NEXAVARA Crisis Operating System API",
            description="AI-powered crisis response orchestration platform",
            version="1.0.0"
        )
        self.coordinator = coordinator
        self.executive_agent = executive_agent
        self._setup_routes()
        logger.info("🚀 NEXAVARA API initialized")
    
    def _setup_routes(self):
        """Configure all API routes."""
        # Health & Status
        self.app.get("/health", response_model=HealthResponse)(self.health_check)
        self.app.get("/metrics")(self.get_metrics)
        
        # Incident Management
        self.app.post("/incidents", response_model=IncidentResponse)(self.create_incident)
        self.app.get("/incidents/{case_id}", response_model=CaseStatusResponse)(self.get_case_status)
        
        # Executive Decisions
        self.app.post("/decide", response_model=DecisionResponse)(self.make_decision)
        
        # Audit & Export
        self.app.get("/audit/{case_id}")(self.export_audit_log)
        self.app.post("/replay/{case_id}")(self.replay_case)
        
        # Error handlers
        self.app.add_exception_handler(ValueError, self._handle_validation_error)
        self.app.add_exception_handler(Exception, self._handle_general_error)
    
    async def health_check(self) -> HealthResponse:
        """Health check endpoint."""
        return HealthResponse(
            status="healthy",
            environment=Config.ENVIRONMENT.value,
            services={
                "coordinator": True,
                "ai_ml": bool(Config.AIML_API_KEY),
                "featherless": bool(Config.FEATHERLESS_API_KEY),
                "database": Config.DB_ENABLED,
            },
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get coordinator metrics."""
        return {
            "coordinator": self.coordinator.get_metrics(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    
    async def create_incident(
        self,
        request: IncidentCreateRequest,
        background_tasks: BackgroundTasks
    ) -> IncidentResponse:
        """Create a new incident and initiate crisis response."""
        try:
            logger.info(f"📋 API: Creating incident (type: {request.incident_type}, severity: {request.severity})")
            
            # Create incident event
            incident = IncidentEvent(
                id=f"INC-{datetime.now(timezone.utc).timestamp():.0f}",
                type=request.incident_type,
                severity=request.severity,
                description=request.description,
                timestamp=datetime.now(timezone.utc)
            )
            
            # Dispatch to all agents
            context = request.context or {}
            if request.affected_systems:
                context["affected_systems"] = request.affected_systems
            
            agent_roles = [
                "SecurityAgent",
                "OperationsAgent",
                "LegalAgent",
                "FinanceAgent"
            ]
            
            self.coordinator.dispatch_incident(incident, agent_roles, context)
            
            # Schedule decision-making in background
            background_tasks.add_task(self._make_decision_after_responses, incident.id)
            
            return IncidentResponse(
                incident_id=incident.id,
                type=incident.type,
                severity=incident.severity,
                description=incident.description,
                status="dispatched_to_agents",
                timestamp=incident.timestamp.isoformat(),
            )
        except Exception as e:
            logger.error(f"❌ Failed to create incident: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    async def get_case_status(self, case_id: str) -> CaseStatusResponse:
        """Get current status of a case."""
        try:
            logger.info(f"📊 API: Getting status for case {case_id}")
            
            case_state = self.coordinator.get_case_state(case_id)
            messages = self.coordinator.get_messages_by_case(case_id)
            responses = [m for m in messages if m["topic"] == "agent.response"]
            
            return CaseStatusResponse(
                case_id=case_id,
                events_count=case_state["events_count"],
                responses_collected=len(responses),
                status="in_progress" if not case_state["latest_decision"] else "decided",
                latest_decision=case_state.get("latest_decision"),
                timestamp=datetime.now(timezone.utc).isoformat(),
            )
        except Exception as e:
            logger.error(f"❌ Failed to get case status: {e}")
            raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
    
    async def make_decision(self, request: DecisionRequest) -> DecisionResponse:
        """Make final executive decision for a case."""
        try:
            logger.info(f"🎯 API: Making decision for case {request.case_id}")
            
            # Use executive agent to make decision
            decision = self.executive_agent.decide_for_case(request.case_id)
            
            return DecisionResponse(
                case_id=decision.case_id,
                summary=decision.summary,
                aggregated_risk=decision.aggregated_risk,
                final_action_plan=decision.final_action_plan,
                reasoning=decision.reasoning,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )
        except Exception as e:
            logger.error(f"❌ Failed to make decision: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    async def export_audit_log(self, case_id: str) -> Dict[str, Any]:
        """Export audit log for a case."""
        try:
            logger.info(f"📁 API: Exporting audit log for case {case_id}")
            
            audit_log = self.coordinator.export_audit_log(case_id)
            
            return {
                "case_id": case_id,
                "audit_log": audit_log,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            logger.error(f"❌ Failed to export audit log: {e}")
            raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
    
    async def replay_case(self, case_id: str) -> Dict[str, Any]:
        """Replay all events for a case."""
        try:
            logger.info(f"🔄 API: Replaying case {case_id}")
            
            self.coordinator.replay_case(case_id)
            
            return {
                "case_id": case_id,
                "status": "replay_initiated",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            logger.error(f"❌ Failed to replay case: {e}")
            raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
    
    async def _make_decision_after_responses(self, case_id: str, delay_seconds: int = 5):
        """Background task to make decision after agents respond."""
        import asyncio
        await asyncio.sleep(delay_seconds)
        try:
            logger.info(f"⏱ Background: Making decision for case {case_id} after response delay")
            self.executive_agent.decide_for_case(case_id)
        except Exception as e:
            logger.warning(f"⚠ Background decision failed for case {case_id}: {e}")
    
    def _handle_validation_error(self, request, exc):
        """Handle validation errors."""
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc), "type": "validation_error"},
        )
    
    def _handle_general_error(self, request, exc):
        """Handle general errors."""
        logger.error(f"❌ Unhandled error: {exc}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "type": "internal_error"},
        )
