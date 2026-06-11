import pytest
from services.memory_layer import MemoryLayer
from services.executive_report import ExecutiveReportGenerator
from nexavara.core_models import CrisisContext, IncidentSeverity


def test_memory_layer_incident_storage_and_retrieval(tmp_path):
    memory = MemoryLayer(str(tmp_path / "memory_store"))
    incident = {
        "incident_id": "INC-100",
        "description": "Simulated HSM entropy warning during PQC key exchange",
        "severity": "critical",
        "resolution_time": 42,
        "agents_involved": ["analysis", "coordination"],
        "outcome": "resolved",
        "lessons_learned": ["improve randomness monitoring"]
    }

    memory_id = memory.store_incident(incident)
    assert isinstance(memory_id, str)
    assert memory.incident_memory[0]["incident_id"] == "INC-100"
    assert memory.incident_memory[0]["outcome"] == "resolved"

    results = memory.find_similar_incidents("entropy warning PQC key exchange", severity="critical")
    assert len(results) >= 1
    assert results[0]["incident"]["incident_id"] == "INC-100"
    assert results[0]["similarity"] > 0.0


def test_memory_layer_agent_performance_metrics():
    memory = MemoryLayer("memory_test_store")
    memory.store_agent_action("analysis", {
        "action_type": "analysis",
        "success": True,
        "response_time": 0.7,
        "confidence": 0.92,
        "context": {"incident_id": "INC-200"},
        "outcome": "analyzed"
    })

    perf = memory.get_agent_performance("analysis")
    assert perf["total_actions"] == 1
    assert perf["success_rate"] == 1.0
    assert perf["avg_response_time"] == 0.7
    assert perf["avg_confidence"] == 0.92
    assert perf["recent_actions"][0]["action_type"] == "analysis"

    missing_perf = memory.get_agent_performance("unknown_agent")
    assert missing_perf["total_actions"] == 0
    assert missing_perf["success_rate"] == 0.0


def test_memory_layer_decision_effectiveness():
    memory = MemoryLayer("memory_test_store")
    memory.store_decision({
        "decision_id": "DEC-001",
        "incident_id": "INC-300",
        "recommendation": "Restart HSM cluster",
        "confidence": 0.85,
        "outcome": "effective",
        "effectiveness": 0.9,
        "context": {"incident_id": "INC-300"}
    })

    eff = memory.get_decision_effectiveness("INC-300")
    assert eff is not None
    assert eff["incident_id"] == "INC-300"
    assert eff["total_decisions"] == 1
    assert eff["avg_confidence"] == pytest.approx(0.85)
    assert eff["avg_effectiveness"] == pytest.approx(0.9)


def test_executive_report_generator_basic_briefing():
    generator = ExecutiveReportGenerator()
    business_impact = {
        "financial_impact": {
            "total_financial_impact": 15000000,
            "per_minute_exposure": 120000,
            "regulatory_fine_risk": 2500000
        },
        "operational_impact": {
            "transactions_blocked_per_hour": 5000,
            "estimated_downtime_hours": 3,
            "affected_services_count": 4
        },
        "customer_impact": {
            "affected_customers": 15000,
            "reputation_score_impact": 70,
            "churn_risk_percentage": 3.2
        },
        "regulatory_risk": {
            "risk_level": "HIGH",
            "compliance_frameworks_affected": ["PCI-DSS", "GDPR"],
            "notification_required": True,
            "notification_deadline_hours": 24
        }
    }

    briefing = generator.generate_executive_briefing(
        incident_id="INC-400",
        incident_title="Post-Quantum Key Exchange Failure",
        severity="critical",
        confidence=0.91,
        root_cause="HSM entropy depletion under peak PQC load",
        business_impact=business_impact,
        technical_details={"root_cause_details": "Entropy pool starvation", "contributing_factors": ["high load"]}
    )

    assert briefing["document_type"] == "EXECUTIVE_CRISIS_BRIEFING"
    assert briefing["executive_summary"]["priority"].startswith("P0")
    assert briefing["risk_mitigation"]["expected_risk_reduction_percentage"] >= 95
    assert "Financial Regulators" in [n["stakeholder"] for n in briefing["stakeholder_notifications"]]
    assert "Execute" in briefing["next_steps"][0]
