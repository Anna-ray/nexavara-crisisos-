"""Unit and integration tests for crisis response agents."""

from datetime import datetime, timezone

import pytest

from agents.crisis_base_agent import BaseAgent
from agents.security_agent import SecurityAgent
from agents.operations_agent import OperationsAgent
from agents.legal_agent import LegalAgent
from agents.finance_agent import FinanceAgent
from agents.executive_agent import ExecutiveAgent
from messages import AgentRequest, AgentResponse, IncidentEvent, FinalDecision


class TestSecurityAgent:
    """Test SecurityAgent rule-based logic."""

    def test_critical_severity_ransomware(self):
        """Test high-severity ransomware incident analysis."""
        agent = SecurityAgent()
        request = AgentRequest(
            incident_id="INC-001",
            context={
                "type": "ransomware",
                "severity": 9,
                "affected_systems": ["file_server", "backup_server"]
            },
            agent_role="SecurityAgent"
        )
        
        response = agent.analyze(request)
        
        assert response.agent_role == "SecurityAgent"
        assert response.risk_score >= 85
        assert response.confidence >= 0.90
        assert "CRITICAL" in response.analysis
        assert len(response.recommended_actions) >= 4

    def test_medium_severity_incident(self):
        """Test medium-severity incident analysis."""
        agent = SecurityAgent()
        request = AgentRequest(
            incident_id="INC-002",
            context={
                "type": "data_exfiltration",
                "severity": 6,
                "affected_systems": ["database"]
            },
            agent_role="SecurityAgent"
        )
        
        response = agent.analyze(request)
        
        assert 60 <= response.risk_score <= 80
        assert response.confidence >= 0.80
        assert "MEDIUM" in response.analysis

    def test_low_severity_incident(self):
        """Test low-severity incident analysis."""
        agent = SecurityAgent()
        request = AgentRequest(
            incident_id="INC-003",
            context={
                "type": "suspicious_login",
                "severity": 2,
                "affected_systems": ["workstation"]
            },
            agent_role="SecurityAgent"
        )
        
        response = agent.analyze(request)
        
        assert response.risk_score < 50
        assert response.confidence >= 0.70
        assert "LOW" in response.analysis


class TestOperationsAgent:
    """Test OperationsAgent operational impact analysis."""

    def test_critical_systems_impact(self):
        """Test analysis of critical system impact."""
        agent = OperationsAgent()
        request = AgentRequest(
            incident_id="INC-004",
            context={
                "type": "ransomware",
                "severity": 8,
                "affected_systems": ["hospital_ehr", "patient_database"]
            },
            agent_role="OperationsAgent"
        )
        
        response = agent.analyze(request)
        
        assert "CRITICAL" in response.analysis or "HIGH" in response.analysis
        assert response.risk_score > 60
        # Check for disaster recovery in analysis or actions
        full_text = response.analysis + " " + " ".join(response.recommended_actions)
        assert "disaster recovery" in full_text.lower()
        assert len(response.recommended_actions) >= 4

    def test_standard_systems_impact(self):
        """Test analysis of standard system impact."""
        agent = OperationsAgent()
        request = AgentRequest(
            incident_id="INC-005",
            context={
                "type": "data_loss",
                "severity": 4,
                "affected_systems": ["archive_server"]
            },
            agent_role="OperationsAgent"
        )
        
        response = agent.analyze(request)
        
        assert response.risk_score < 70


class TestLegalAgent:
    """Test LegalAgent compliance and legal obligation analysis."""

    def test_healthcare_regulation_detection(self):
        """Test HIPAA compliance obligation detection."""
        agent = LegalAgent()
        request = AgentRequest(
            incident_id="INC-006",
            context={
                "type": "data_breach",
                "severity": 8,
                "affected_systems": ["hospital_ehr", "patient_records"]
            },
            agent_role="LegalAgent"
        )
        
        response = agent.analyze(request)
        
        assert "REGULATORY EXPOSURE" in response.analysis
        assert response.risk_score > 50
        assert "notification" in response.analysis.lower()
        assert len(response.recommended_actions) >= 5

    def test_standard_incident_legal_review(self):
        """Test standard incident without specific regulations."""
        agent = LegalAgent()
        request = AgentRequest(
            incident_id="INC-007",
            context={
                "type": "malware",
                "severity": 3,
                "affected_systems": ["test_system"]
            },
            agent_role="LegalAgent"
        )
        
        response = agent.analyze(request)
        
        assert "STANDARD" in response.analysis
        assert response.risk_score < 50


class TestFinanceAgent:
    """Test FinanceAgent financial impact analysis."""

    def test_high_cost_system_impact(self):
        """Test financial impact of critical system outage."""
        agent = FinanceAgent()
        request = AgentRequest(
            incident_id="INC-008",
            context={
                "type": "ransomware",
                "severity": 9,
                "affected_systems": ["banking_system", "payment_processor"]
            },
            agent_role="FinanceAgent"
        )
        
        response = agent.analyze(request)
        
        assert response.risk_score > 60
        assert "$" in response.analysis
        assert "million" in response.analysis.lower() or int("".join(filter(str.isdigit, response.analysis.split("$")[1].split(",")[0]))) > 100000
        assert "CFO" in response.analysis

    def test_standard_system_financial_impact(self):
        """Test financial impact of standard system outage."""
        agent = FinanceAgent()
        request = AgentRequest(
            incident_id="INC-009",
            context={
                "type": "file_corruption",
                "severity": 3,
                "affected_systems": ["internal_wiki"]
            },
            agent_role="FinanceAgent"
        )
        
        response = agent.analyze(request)
        
        assert response.risk_score < 50


class TestExecutiveAgent:
    """Test ExecutiveAgent aggregation and final decision logic."""

    def test_aggregate_responses_critical_incident(self):
        """Test aggregation of responses for critical incident."""
        executive = ExecutiveAgent()
        
        responses = [
            AgentResponse(
                agent_role="SecurityAgent",
                analysis="Critical security threat detected.",
                risk_score=90,
                confidence=0.95,
                recommended_actions=["Isolate systems", "Initiate forensics"]
            ),
            AgentResponse(
                agent_role="FinanceAgent",
                analysis="Significant financial exposure.",
                risk_score=80,
                confidence=0.85,
                recommended_actions=["Alert CFO", "Activate emergency budget"]
            ),
            AgentResponse(
                agent_role="LegalAgent",
                analysis="Regulatory notification required.",
                risk_score=85,
                confidence=0.90,
                recommended_actions=["Prepare regulatory filing", "Engage counsel"]
            )
        ]
        
        decision = executive.aggregate_responses("INC-010", responses)
        
        assert isinstance(decision, FinalDecision)
        assert decision.aggregated_risk > 70
        assert len(decision.final_action_plan) >= 2
        assert "CRITICAL" in decision.summary or decision.aggregated_risk >= 80
        assert "executive" in decision.reasoning.lower()

    def test_aggregate_responses_low_incident(self):
        """Test aggregation of responses for low-severity incident."""
        executive = ExecutiveAgent()
        
        responses = [
            AgentResponse(
                agent_role="SecurityAgent",
                analysis="Low-level threat.",
                risk_score=25,
                confidence=0.70,
                recommended_actions=["Monitor"]
            ),
            AgentResponse(
                agent_role="OperationsAgent",
                analysis="Minimal operational impact.",
                risk_score=20,
                confidence=0.75,
                recommended_actions=["Continue operations"]
            )
        ]
        
        decision = executive.aggregate_responses("INC-011", responses)
        
        assert decision.aggregated_risk < 50
        assert len(decision.final_action_plan) >= 1


class TestIntegration:
    """Integration tests: Incident -> Agents -> Executive Decision."""

    def test_full_incident_response_workflow(self):
        """Test complete workflow from incident detection to executive decision."""
        # 1. Create incident
        incident = IncidentEvent(
            id="INC-CRITICAL-001",
            type="ransomware",
            severity=9,
            description="Ransomware attack on hospital system",
            timestamp=datetime.now(timezone.utc)
        )
        
        # 2. Create incident context for agents
        context = {
            "type": incident.type,
            "severity": incident.severity,
            "description": incident.description,
            "affected_systems": ["hospital_ehr", "patient_database", "backup_server"]
        }
        
        request = AgentRequest(
            incident_id=incident.id,
            context=context,
            agent_role="Orchestrator"
        )
        
        # 3. Dispatch to all agents (parallel)
        security_agent = SecurityAgent()
        operations_agent = OperationsAgent()
        legal_agent = LegalAgent()
        finance_agent = FinanceAgent()
        
        security_response = security_agent.analyze(request)
        operations_response = operations_agent.analyze(request)
        legal_response = legal_agent.analyze(request)
        finance_response = finance_agent.analyze(request)
        
        # Validate individual responses
        assert all(isinstance(r, AgentResponse) for r in [
            security_response, operations_response, legal_response, finance_response
        ])
        
        # 4. Aggregate via ExecutiveAgent
        executive_agent = ExecutiveAgent()
        final_decision = executive_agent.aggregate_responses(
            incident.id,
            [security_response, operations_response, legal_response, finance_response]
        )
        
        # Validate final decision
        assert isinstance(final_decision, FinalDecision)
        assert final_decision.aggregated_risk >= 75
        assert len(final_decision.final_action_plan) >= 2
        assert "executive" in final_decision.reasoning.lower()
        assert "Isolate" in " ".join(final_decision.final_action_plan)
