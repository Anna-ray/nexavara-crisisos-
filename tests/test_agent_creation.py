import pytest
from adapters.band_client import InMemoryBandClient
from agents.analysis_agent import PQCAnalysisAgent
from agents.coordination_agent import PQCCoordinationAgent
from agents.decision_agent import PQCDecisionAgent
from agents.audit_agent import PQCAuditAgent
from services.memory_layer import MemoryLayer
from services.executive_report import ExecutiveReportGenerator
from nexavara.crisis_council import ThreatDirectorAgent, RiskDirectorAgent, ComplianceDirectorAgent, LegalDirectorAgent, ExecutiveBriefingDirectorAgent

def test_band_client_instantiation():
    client = InMemoryBandClient()
    assert client is not None


def test_analysis_agent_creation():
    client = InMemoryBandClient()
    agent = PQCAnalysisAgent(name="analysis", band_client=client)
    assert agent.name == "analysis"
    assert agent.band is client


def test_coordination_agent_creation():
    client = InMemoryBandClient()
    agent = PQCCoordinationAgent(name="coordination", band_client=client)
    assert agent.name == "coordination"
    assert agent.band is client


def test_decision_agent_creation():
    client = InMemoryBandClient()
    agent = PQCDecisionAgent(name="decision", band_client=client)
    assert agent.name == "decision"
    assert agent.band is client


def test_audit_agent_creation_and_subscription(tmp_path):
    client = InMemoryBandClient()
    audit_file = tmp_path / "audit.jsonl"
    agent = PQCAuditAgent(name="audit", band_client=client, audit_file_path=str(audit_file))
    assert agent.name == "audit"
    assert agent.audit_file_path == str(audit_file)
    assert audit_file.parent.exists()


def test_memory_layer_store_and_query(tmp_path):
    storage = tmp_path / "memory_store"
    memory = MemoryLayer(str(storage))
    payload = {
        "incident_id": "INC-001",
        "description": "Test incident",
        "severity": "critical",
        "outcome": "resolved",
        "agents_involved": ["analysis", "decision"]
    }
    memory_id = memory.store_incident(payload)
    assert memory_id is not None
    assert len(memory.incident_memory) == 1
    assert memory.incident_memory[0]["incident_id"] == "INC-001"

    similar = memory.find_similar_incidents("Test incident", severity="critical")
    assert isinstance(similar, list)
    assert similar[0]["incident"]["incident_id"] == "INC-001"


def test_executive_report_generation():
    generator = ExecutiveReportGenerator()
    impact = {
        "financial_impact": {
            "total_financial_impact": 1234567,
            "per_minute_exposure": 50000,
            "regulatory_fine_risk": 1000000
        },
        "operational_impact": {
            "transactions_blocked_per_hour": 2000,
            "estimated_downtime_hours": 2,
            "affected_services_count": 3
        },
        "customer_impact": {
            "affected_customers": 12000,
            "reputation_score_impact": 50,
            "churn_risk_percentage": 2.5
        },
        "regulatory_risk": {
            "risk_level": "HIGH",
            "compliance_frameworks_affected": ["PCI-DSS"],
            "notification_required": True,
            "notification_deadline_hours": 24
        }
    }

    briefing = generator.generate_executive_briefing(
        incident_id="INC-001",
        incident_title="Post-Quantum Cryptographic Failure",
        severity="critical",
        confidence=0.85,
        root_cause="HSM entropy starvation",
        business_impact=impact,
        technical_details={"root_cause_details": "Entropy pools starved"}
    )

    assert briefing["document_type"] == "EXECUTIVE_CRISIS_BRIEFING"
    assert briefing["executive_summary"]["priority"].startswith("P")
    assert len(briefing["recommended_actions"]) >= 1


def test_director_agent_memory_and_context():
    threat_agent = ThreatDirectorAgent()
    context = threat_agent.current_context
    assert context is None
    # Use a minimal crisis context object from nexavara.core_models
    from nexavara.core_models import CrisisContext, IncidentSeverity
    incident_context = CrisisContext(
        incident_type="post_quantum_failure",
        severity=IncidentSeverity.CRITICAL,
        description="HSM entropy degraded during Kyber-1024 handshakes",
        affected_entities=["HSM", "Clearing Gateway"]
    )
    finding = threat_agent.analyze_crisis(incident_context)
    assert finding.agent == threat_agent.agent_type
    assert finding.confidence >= 0.0
    assert len(threat_agent.memory) == 1


def test_agency_context_transfer_between_agents():
    from nexavara.core_models import CrisisContext, IncidentSeverity
    threat_agent = ThreatDirectorAgent()
    risk_agent = RiskDirectorAgent()
    context = CrisisContext(
        incident_type="post_quantum_failure",
        severity=IncidentSeverity.CRITICAL,
        description="HSM entropy degradation impacting transaction clearing",
        affected_entities=["HSM", "Payments"]
    )

    threat_finding = threat_agent.analyze_crisis(context)
    risk_finding = risk_agent.analyze_crisis(context)
    assert threat_finding.severity == risk_finding.severity
    assert threat_agent.current_context == context
    assert risk_agent.current_context == context


def test_digital_twin_model_validation():
    from nexavara.core_models import DigitalTwin, OrganizationalEntity, EntityType
    node = OrganizationalEntity(
        entity_type=EntityType.APPLICATION,
        name="HSM Cluster",
        description="Hardware security module cluster",
        criticality=5
    )
    twin = DigitalTwin(
        organization_name="NEXAVARA Labs",
        entities={node.entity_id: node}
    )
    assert twin.total_entities == 0
    assert list(twin.entities.values())[0].name == "HSM Cluster"
