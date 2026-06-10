"""
War Room API - FastAPI backend for multi-agent orchestration
"""

from fastapi import FastAPI, WebSocket, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
import asyncio
from typing import Dict, List, Set
from datetime import datetime, timezone

from services.war_room_models import (
    Incident, IncidentType, SeverityLevel, MemoryGraph,
    WarRoomState, AgentType, AgentStatus, Decision,
    ExecutiveBriefing, Finding, Evidence
)
from services.agent_debate_system import AgentDebateSystem, DebateExplainer
from services.business_impact_engine import BusinessImpactEngine
from services.simulation_scenarios import SimulationScenarioLibrary


app = FastAPI(
    title="NEXAVARA War Room API",
    description="Multi-Agent Cyber Crisis Operating System",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
class WarRoomState:
    def __init__(self):
        self.active_incidents: Dict[str, Incident] = {}
        self.memory_graphs: Dict[str, MemoryGraph] = {}
        self.debate_systems: Dict[str, AgentDebateSystem] = {}
        self.connected_clients: Set[WebSocket] = set()
        self.business_impact_engine = BusinessImpactEngine()
    
    async def broadcast(self, message: Dict):
        """Broadcast message to all connected WebSocket clients"""
        disconnected = set()
        for client in self.connected_clients:
            try:
                await client.send_json(message)
            except Exception as e:
                disconnected.add(client)
        
        for client in disconnected:
            self.connected_clients.discard(client)

war_room = WarRoomState()


# ============================================================================
# INCIDENT MANAGEMENT ENDPOINTS
# ============================================================================

@app.post("/api/incidents")
async def create_incident(
    incident_type: IncidentType,
    title: str,
    description: str,
    severity: SeverityLevel = SeverityLevel.MEDIUM
) -> Incident:
    """Create a new incident"""
    
    incident = Incident(
        incident_type=incident_type,
        title=title,
        description=description,
        severity=severity
    )
    
    war_room.active_incidents[incident.id] = incident
    war_room.memory_graphs[incident.id] = MemoryGraph()
    war_room.debate_systems[incident.id] = AgentDebateSystem(war_room.memory_graphs[incident.id])
    
    await war_room.broadcast({
        "type": "incident_created",
        "incident_id": incident.id,
        "title": incident.title,
        "severity": incident.severity.value,
        "timestamp": incident.detected_at.isoformat()
    })
    
    return incident


@app.get("/api/incidents/{incident_id}")
async def get_incident(incident_id: str) -> Incident:
    """Get incident details"""
    
    incident = war_room.active_incidents.get(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    return incident


@app.get("/api/incidents")
async def list_incidents() -> List[Incident]:
    """List all active incidents"""
    return list(war_room.active_incidents.values())


# ============================================================================
# AGENT FINDINGS & ANALYSIS ENDPOINTS
# ============================================================================

@app.post("/api/incidents/{incident_id}/findings")
async def add_finding(
    incident_id: str,
    agent_type: AgentType,
    content: str,
    confidence: float,
    severity: SeverityLevel,
    reasoning: str,
    evidence_ids: List[str] = None
) -> Finding:
    """Add a finding from an agent"""
    
    incident = war_room.active_incidents.get(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    finding = Finding(
        agent_type=agent_type,
        content=content,
        confidence=confidence,
        severity=severity,
        reasoning=reasoning,
        evidence_ids=evidence_ids or []
    )
    
    memory = war_room.memory_graphs[incident_id]
    memory.findings.append(finding)
    incident.finding_ids.append(finding.id)
    
    # Broadcast finding to war room
    await war_room.broadcast({
        "type": "finding_added",
        "incident_id": incident_id,
        "agent": agent_type.value,
        "finding": {
            "id": finding.id,
            "content": finding.content,
            "confidence": finding.confidence,
            "severity": finding.severity.value,
            "timestamp": finding.timestamp.isoformat()
        }
    })
    
    return finding


@app.post("/api/incidents/{incident_id}/evidence")
async def add_evidence(
    incident_id: str,
    source: str,
    metric_name: str,
    value,
    severity: SeverityLevel,
    confidence: float,
    threshold = None
) -> Evidence:
    """Add evidence to an incident"""
    
    incident = war_room.active_incidents.get(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    evidence = Evidence(
        source=source,
        metric_name=metric_name,
        value=value,
        threshold=threshold,
        severity=severity,
        confidence=confidence
    )
    
    memory = war_room.memory_graphs[incident_id]
    memory.evidence.append(evidence)
    incident.evidence_ids.append(evidence.id)
    
    await war_room.broadcast({
        "type": "evidence_added",
        "incident_id": incident_id,
        "evidence": {
            "id": evidence.id,
            "source": evidence.source,
            "metric": evidence.metric_name,
            "value": str(evidence.value),
            "severity": evidence.severity.value
        }
    })
    
    return evidence


# ============================================================================
# DEBATE SYSTEM ENDPOINTS
# ============================================================================

@app.post("/api/incidents/{incident_id}/debates")
async def initiate_debate(
    incident_id: str,
    topic: str,
    initiating_agent: AgentType,
    challenged_agent: AgentType,
    challenge_reason: str,
    position: str,
    confidence: float
):
    """Initiate an agent debate"""
    
    if incident_id not in war_room.debate_systems:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    debate_system = war_room.debate_systems[incident_id]
    debate = debate_system.initiate_debate(
        topic=topic,
        initiating_agent=initiating_agent,
        challenged_agent=challenged_agent,
        challenge_reason=challenge_reason,
        initiating_agent_position=position,
        initiating_agent_confidence=confidence
    )
    
    await war_room.broadcast({
        "type": "debate_initiated",
        "incident_id": incident_id,
        "debate": {
            "id": debate.id,
            "topic": debate.topic,
            "initiating_agent": debate.initiated_by.value,
            "challenged_agent": debate.challenged_agent.value if debate.challenged_agent else None,
            "reason": debate.challenge_reason
        }
    })
    
    return {"debate_id": debate.id, "status": "initiated"}


@app.post("/api/incidents/{incident_id}/debates/{debate_id}/response")
async def add_debate_response(
    incident_id: str,
    debate_id: str,
    agent_type: AgentType,
    response: str,
    confidence: float,
    concedes: bool = False
):
    """Add a response to a debate"""
    
    debate_system = war_room.debate_systems.get(incident_id)
    if not debate_system:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    debate = debate_system.add_debate_response(
        debate_id=debate_id,
        responding_agent=agent_type,
        response_content=response,
        confidence=confidence,
        concedes=concedes
    )
    
    if not debate:
        raise HTTPException(status_code=404, detail="Debate not found")
    
    await war_room.broadcast({
        "type": "debate_response",
        "incident_id": incident_id,
        "debate_id": debate_id,
        "agent": agent_type.value,
        "concedes": concedes,
        "message": response
    })
    
    return {"status": "response_added"}


@app.get("/api/incidents/{incident_id}/debates")
async def get_debates(incident_id: str) -> List:
    """Get all debates for an incident"""
    
    debate_system = war_room.debate_systems.get(incident_id)
    if not debate_system:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    return [debate_system.get_debate_summary(d.id) for d in debate_system.debates]


# ============================================================================
# BUSINESS IMPACT ENDPOINTS
# ============================================================================

@app.post("/api/incidents/{incident_id}/calculate-impact")
async def calculate_business_impact(
    incident_id: str,
    affected_systems: int,
    affected_customers: int,
    downtime_hours: float,
    data_breach: bool = False,
    customer_records_affected: int = 0
):
    """Calculate business impact"""
    
    incident = war_room.active_incidents.get(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    impact = war_room.business_impact_engine.calculate_business_impact(
        incident=incident,
        affected_systems=affected_systems,
        affected_customers=affected_customers,
        estimated_downtime_hours=downtime_hours,
        data_breach=data_breach,
        customer_records_affected=customer_records_affected
    )
    
    await war_room.broadcast({
        "type": "impact_calculated",
        "incident_id": incident_id,
        "financial_exposure": impact.financial_exposure,
        "affected_systems": impact.affected_systems,
        "affected_customers": impact.affected_customers
    })
    
    return impact.dict()


@app.get("/api/incidents/{incident_id}/impact-projection")
async def get_impact_projection(incident_id: str, hours: int = 24):
    """Get financial impact projection over time"""
    
    incident = war_room.active_incidents.get(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    # Use a baseline impact for projection
    baseline_impact = 1_000_000  # $1M baseline
    
    projection = war_room.business_impact_engine.project_financial_impact_by_hour(
        initial_impact=baseline_impact,
        hours_unresolved=hours
    )
    
    return {"projection": projection}


# ============================================================================
# EXECUTIVE BRIEFING ENDPOINTS
# ============================================================================

@app.post("/api/incidents/{incident_id}/executive-briefing")
async def generate_executive_briefing(
    incident_id: str,
    current_status: str = "In Progress"
) -> ExecutiveBriefing:
    """Generate executive briefing"""
    
    incident = war_room.active_incidents.get(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    memory = war_room.memory_graphs.get(incident_id)
    
    briefing = ExecutiveBriefing(
        incident_id=incident_id,
        current_severity=incident.severity,
        current_status=current_status,
        time_since_detection_minutes=int(
            (datetime.now(timezone.utc) - incident.detected_at).total_seconds() / 60
        ),
        financial_exposure=5_200_000,  # Placeholder
        affected_systems=len(incident.finding_ids),
        affected_customers=42000,
        regulatory_risk_level="HIGH",
        immediate_actions=[
            "Isolate affected systems",
            "Notify leadership",
            "Activate incident response team"
        ],
        recommended_next_steps=[
            "Conduct forensic analysis",
            "Prepare customer notifications",
            "Coordinate with regulators"
        ],
        executive_summary="Critical incident detected requiring immediate leadership attention",
        key_talking_points=[
            "Rapid detection and response",
            "Business continuity maintained",
            "Proactive customer communication planned"
        ],
        recommended_disclosure="Within 4 hours",
        supporting_evidence_count=len(memory.evidence) if memory else 0,
        confidence=0.88
    )
    
    await war_room.broadcast({
        "type": "briefing_generated",
        "incident_id": incident_id,
        "severity": briefing.current_severity.value,
        "financial_exposure": briefing.financial_exposure
    })
    
    return briefing


# ============================================================================
# SIMULATION ENDPOINTS
# ============================================================================

@app.post("/api/simulations/start")
async def start_simulation(incident_type: IncidentType, background_tasks: BackgroundTasks):
    """Start a simulation scenario"""
    
    try:
        scenario = SimulationScenarioLibrary.get_scenario_by_type(incident_type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Create incident from scenario
    incident = Incident(
        incident_type=incident_type,
        title=scenario.name,
        description=scenario.description,
        severity=scenario.expected_severity
    )
    
    war_room.active_incidents[incident.id] = incident
    war_room.memory_graphs[incident.id] = MemoryGraph()
    war_room.debate_systems[incident.id] = AgentDebateSystem(war_room.memory_graphs[incident.id])
    
    # Add initial evidence
    for evidence_item in scenario.initial_evidence:
        war_room.memory_graphs[incident.id].evidence.append(evidence_item)
        incident.evidence_ids.append(evidence_item.id)
    
    # Schedule simulation progression
    background_tasks.add_task(_run_simulation, incident.id, scenario)
    
    await war_room.broadcast({
        "type": "simulation_started",
        "incident_id": incident.id,
        "scenario": scenario.name,
        "severity": incident.severity.value
    })
    
    return {"incident_id": incident.id, "scenario": scenario.name}


async def _run_simulation(incident_id: str, scenario):
    """Run simulation progression in background"""
    
    for step in scenario.progression_steps:
        # Wait for the offset time
        await asyncio.sleep(step.get("timestamp_offset_minutes", 0) * 60 / 10)  # Speed up for demo
        
        await war_room.broadcast({
            "type": "simulation_stage",
            "incident_id": incident_id,
            "stage": step.get("stage"),
            "description": step.get("description")
        })


# ============================================================================
# WEBSOCKET ENDPOINT
# ============================================================================

@app.websocket("/ws/war-room/{incident_id}")
async def websocket_endpoint(websocket: WebSocket, incident_id: str):
    """WebSocket connection for real-time war room updates"""
    
    await websocket.accept()
    war_room.connected_clients.add(websocket)
    
    try:
        # Send initial state
        incident = war_room.active_incidents.get(incident_id)
        memory = war_room.memory_graphs.get(incident_id)
        
        if incident and memory:
            initial_state = {
                "type": "initial_state",
                "incident": {
                    "id": incident.id,
                    "title": incident.title,
                    "severity": incident.severity.value,
                    "findings_count": len(incident.finding_ids),
                    "evidence_count": len(incident.evidence_ids)
                },
                "memory": {
                    "findings_count": len(memory.findings),
                    "evidence_count": len(memory.evidence),
                    "average_confidence": memory.get_average_confidence()
                }
            }
            await websocket.send_json(initial_state)
        
        # Keep connection alive
        while True:
            await websocket.receive_text()
    
    except Exception as e:
        print(f"WebSocket error: {e}")
    
    finally:
        war_room.connected_clients.discard(websocket)


# ============================================================================
# STATUS & HEALTH ENDPOINTS
# ============================================================================

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "operational",
        "active_incidents": len(war_room.active_incidents),
        "connected_clients": len(war_room.connected_clients),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/api/war-room/status/{incident_id}")
async def get_war_room_status(incident_id: str):
    """Get overall war room status"""
    
    incident = war_room.active_incidents.get(incident_id)
    memory = war_room.memory_graphs.get(incident_id)
    debate_system = war_room.debate_systems.get(incident_id)
    
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    return {
        "incident": {
            "id": incident.id,
            "title": incident.title,
            "severity": incident.severity.value,
            "detected_at": incident.detected_at.isoformat()
        },
        "analysis_progress": {
            "findings": len(memory.findings) if memory else 0,
            "evidence": len(memory.evidence) if memory else 0,
            "decisions": len(memory.decisions) if memory else 0
        },
        "collaboration": {
            "active_debates": debate_system.get_active_debates_count() if debate_system else 0,
            "consensus_level": debate_system.get_consensus_level() if debate_system else 1.0
        },
        "connected_clients": len(war_room.connected_clients)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
