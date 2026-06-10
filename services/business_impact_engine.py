"""
Business Impact Engine - Translates technical findings into business metrics
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import math

from services.war_room_models import (
    Incident, IncidentType, SeverityLevel, BusinessImpactAnalysis,
    ComplianceAnalysis, Finding, Evidence
)


class BusinessImpactEngine:
    """
    Calculates financial, operational, and regulatory impact of cyber incidents.
    """
    
    def __init__(self):
        # Industry benchmarks (customize per customer)
        self.revenue_per_hour = 1_000_000  # $1M/hour operational revenue
        self.customer_lifetime_value = 5_000  # $5k average LTV
        self.regulatory_fine_percentage = 0.04  # 4% of revenue
        self.brand_reputation_impact = 0.15  # 15% of annual revenue
        
        # Incident-specific multipliers
        self.incident_multipliers = {
            IncidentType.RANSOMWARE: 2.5,
            IncidentType.NATION_STATE: 3.0,
            IncidentType.CLOUD_BREACH: 2.0,
            IncidentType.SUPPLY_CHAIN: 3.5,
            IncidentType.POST_QUANTUM_FAILURE: 2.8,
            IncidentType.IDENTITY_COMPROMISE: 2.2
        }
    
    def calculate_business_impact(
        self,
        incident: Incident,
        affected_systems: int,
        affected_customers: int,
        estimated_downtime_hours: float,
        data_breach: bool = False,
        customer_records_affected: int = 0
    ) -> BusinessImpactAnalysis:
        """
        Calculate comprehensive business impact.
        """
        
        # Base calculations
        direct_financial_loss = self._calculate_direct_loss(
            estimated_downtime_hours
        )
        
        customer_churn_loss = self._calculate_churn_loss(
            affected_customers,
            data_breach
        )
        
        regulatory_exposure = self._calculate_regulatory_exposure(
            incident.incident_type,
            customer_records_affected if data_breach else 0
        )
        
        # Severity multiplier
        severity_multiplier = self._get_severity_multiplier(incident.severity)
        incident_multiplier = self.incident_multipliers.get(incident.incident_type, 1.0)
        
        total_multiplier = severity_multiplier * incident_multiplier
        
        # Calculate total exposure
        financial_exposure = (
            (direct_financial_loss + customer_churn_loss) * total_multiplier
        )
        
        revenue_at_risk = self.revenue_per_hour * estimated_downtime_hours
        
        return BusinessImpactAnalysis(
            financial_exposure=financial_exposure,
            affected_systems=affected_systems,
            affected_customers=affected_customers,
            revenue_at_risk_per_hour=self.revenue_per_hour,
            estimated_downtime_hours=estimated_downtime_hours,
            regulatory_fines_potential=regulatory_exposure,
            customer_churn_percentage=self._get_churn_percentage(data_breach),
            reputational_damage_percentage=self._get_reputation_damage(
                incident.incident_type,
                customer_records_affected if data_breach else 0
            ),
            total_financial_impact=financial_exposure + regulatory_exposure,
            confidence=0.85  # Based on data quality
        )
    
    def calculate_compliance_impact(
        self,
        incident: Incident,
        data_breach: bool = False,
        customer_records: int = 0,
        pii_categories: List[str] = None
    ) -> ComplianceAnalysis:
        """
        Calculate regulatory and compliance exposure.
        """
        
        pii_categories = pii_categories or []
        
        regulations_affected = self._determine_regulations(
            data_breach,
            customer_records,
            pii_categories
        )
        
        notification_timeline_hours = self._get_notification_timeline(
            regulations_affected
        )
        
        fines = self._calculate_regulatory_fines(
            regulations_affected,
            customer_records
        )
        
        return ComplianceAnalysis(
            regulations_affected=regulations_affected,
            notification_requirements=[
                f"Notify {record_count} customers" for record_count in [customer_records]
            ] if data_breach else [],
            notification_timeline_hours=notification_timeline_hours,
            regulatory_fines_potential=fines,
            legal_exposure_level=self._get_legal_exposure_level(fines),
            required_actions=self._get_required_actions(
                regulations_affected,
                incident.incident_type
            ),
            confidence=0.88
        )
    
    def estimate_time_to_recovery(
        self,
        incident_type: IncidentType,
        severity: SeverityLevel,
        response_quality: float  # 0.0-1.0
    ) -> Dict[str, Any]:
        """
        Estimate time to recovery based on incident characteristics.
        """
        
        # Base recovery times (hours)
        base_times = {
            IncidentType.RANSOMWARE: 24,
            IncidentType.NATION_STATE: 48,
            IncidentType.CLOUD_BREACH: 18,
            IncidentType.SUPPLY_CHAIN: 36,
            IncidentType.POST_QUANTUM_FAILURE: 12,
            IncidentType.IDENTITY_COMPROMISE: 16
        }
        
        severity_multipliers = {
            SeverityLevel.LOW: 0.5,
            SeverityLevel.MEDIUM: 1.0,
            SeverityLevel.HIGH: 1.5,
            SeverityLevel.CRITICAL: 2.0
        }
        
        base_time = base_times.get(incident_type, 24)
        severity_mult = severity_multipliers.get(severity, 1.0)
        
        # Response quality improves recovery time
        response_factor = 1.0 - (response_quality * 0.4)  # Up to 40% improvement
        
        estimated_hours = base_time * severity_mult * response_factor
        
        # Phases
        detection_hours = max(0.5, estimated_hours * 0.15)  # 15% of total
        containment_hours = max(2, estimated_hours * 0.35)  # 35% of total
        eradication_hours = max(2, estimated_hours * 0.30)  # 30% of total
        recovery_hours = max(1, estimated_hours * 0.20)  # 20% of total
        
        return {
            "total_hours": estimated_hours,
            "total_days": estimated_hours / 24,
            "phases": {
                "detection": {"hours": detection_hours, "status": "complete"},
                "containment": {"hours": containment_hours, "status": "in_progress"},
                "eradication": {"hours": eradication_hours, "status": "pending"},
                "recovery": {"hours": recovery_hours, "status": "pending"}
            },
            "critical_path_items": self._get_critical_path_items(incident_type)
        }
    
    def project_financial_impact_by_hour(
        self,
        initial_impact: float,
        hours_unresolved: int
    ) -> List[Dict[str, Any]]:
        """
        Project cumulative financial impact over time.
        """
        
        projection = []
        
        for hour in range(0, hours_unresolved + 1):
            # Exponential growth of impact as incident continues
            hourly_impact = initial_impact * (1.02 ** hour)  # 2% escalation per hour
            cumulative_impact = sum(initial_impact * (1.02 ** h) for h in range(0, hour + 1))
            
            projection.append({
                "hour": hour,
                "hourly_impact": hourly_impact,
                "cumulative_impact": cumulative_impact,
                "cost_per_minute": hourly_impact / 60
            })
        
        return projection
    
    # ========================================================================
    # PRIVATE CALCULATION METHODS
    # ========================================================================
    
    def _calculate_direct_loss(self, downtime_hours: float) -> float:
        """Direct financial loss from downtime"""
        return self.revenue_per_hour * downtime_hours
    
    def _calculate_churn_loss(
        self,
        affected_customers: int,
        data_breach: bool
    ) -> float:
        """Loss from customer churn"""
        churn_rate = 0.15 if data_breach else 0.05  # 15% or 5% churn
        return affected_customers * self.customer_lifetime_value * churn_rate
    
    def _calculate_regulatory_exposure(
        self,
        incident_type: IncidentType,
        customer_records: int
    ) -> float:
        """Potential regulatory fines"""
        if customer_records == 0:
            return 0.0
        
        # GDPR: up to €20M or 4% revenue
        # HIPAA: up to $1.5M per violation category
        # CCPA: up to $7,500 per record
        base_fine = min(
            customer_records * 5000,  # ~$5k per record average
            self.revenue_per_hour * 24 * 365 * 0.04  # 4% annual revenue
        )
        
        return base_fine
    
    def _get_severity_multiplier(self, severity: SeverityLevel) -> float:
        """Multiplier based on severity level"""
        multipliers = {
            SeverityLevel.LOW: 0.5,
            SeverityLevel.MEDIUM: 1.0,
            SeverityLevel.HIGH: 1.5,
            SeverityLevel.CRITICAL: 2.0
        }
        return multipliers.get(severity, 1.0)
    
    def _get_churn_percentage(self, data_breach: bool) -> float:
        """Expected customer churn percentage"""
        return 0.15 if data_breach else 0.03
    
    def _get_reputation_damage(
        self,
        incident_type: IncidentType,
        customer_records: int
    ) -> float:
        """Estimated reputational damage as % of annual revenue"""
        
        base_damage = {
            IncidentType.RANSOMWARE: 0.12,
            IncidentType.NATION_STATE: 0.08,
            IncidentType.CLOUD_BREACH: 0.20,
            IncidentType.SUPPLY_CHAIN: 0.15,
            IncidentType.POST_QUANTUM_FAILURE: 0.10,
            IncidentType.IDENTITY_COMPROMISE: 0.18
        }
        
        damage = base_damage.get(incident_type, 0.10)
        
        # Increase with customer records affected
        if customer_records > 0:
            damage *= min(2.0, 1.0 + (customer_records / 10000))
        
        return min(0.50, damage)  # Cap at 50% of annual revenue
    
    def _determine_regulations(
        self,
        data_breach: bool,
        customer_records: int,
        pii_categories: List[str]
    ) -> List[str]:
        """Determine which regulations are affected"""
        
        regulations = []
        
        if not data_breach:
            return regulations
        
        # Always GDPR if any EU data
        regulations.append("GDPR")
        
        # Check for specific data categories
        if any(cat in pii_categories for cat in ["health", "medical", "pharmaceutical"]):
            regulations.append("HIPAA")
        
        if customer_records > 1000:
            regulations.append("CCPA")
            regulations.append("NIST")
        
        if "payment_card" in pii_categories:
            regulations.append("PCI-DSS")
        
        return regulations
    
    def _get_notification_timeline(self, regulations: List[str]) -> int:
        """Notification timeline in hours"""
        
        min_timeline = 72  # Default 72 hours
        
        if "GDPR" in regulations:
            min_timeline = min(min_timeline, 72)  # GDPR: without undue delay, max 72h
        
        if "HIPAA" in regulations:
            min_timeline = min(min_timeline, 24)  # HIPAA: 60 days but system operators need 24h notice
        
        if "CCPA" in regulations:
            min_timeline = min(min_timeline, 72)  # CCPA: without undue delay
        
        return min_timeline
    
    def _calculate_regulatory_fines(
        self,
        regulations: List[str],
        customer_records: int
    ) -> float:
        """Calculate potential regulatory fines"""
        
        total_fines = 0.0
        
        for reg in regulations:
            if reg == "GDPR":
                # GDPR: Up to €20M or 4% of global revenue
                total_fines += min(20_000_000, self.revenue_per_hour * 24 * 365 * 0.04)
            elif reg == "HIPAA":
                # HIPAA: $100 - $50,000 per violation
                total_fines += min(1_500_000, customer_records * 100)
            elif reg == "CCPA":
                # CCPA: $100 - $7,500 per record
                total_fines += min(7_500_000, customer_records * 500)
            elif reg == "PCI-DSS":
                # PCI: $5,000 - $100,000 per month until compliance
                total_fines += 50_000
        
        return total_fines
    
    def _get_legal_exposure_level(self, fines: float) -> str:
        """Categorize legal exposure level"""
        
        annual_revenue = self.revenue_per_hour * 24 * 365
        fine_percentage = (fines / annual_revenue) * 100
        
        if fine_percentage > 5:
            return "CRITICAL"
        elif fine_percentage > 2:
            return "HIGH"
        elif fine_percentage > 0.5:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _get_required_actions(
        self,
        regulations: List[str],
        incident_type: IncidentType
    ) -> List[str]:
        """Get required compliance actions"""
        
        actions = []
        
        if "GDPR" in regulations:
            actions.extend([
                "Notify affected data subjects",
                "File Data Protection Authority report",
                "Conduct Data Protection Impact Assessment"
            ])
        
        if "HIPAA" in regulations:
            actions.extend([
                "Notify HHS Office for Civil Rights",
                "Conduct Risk Assessment",
                "File Breach Notification"
            ])
        
        if incident_type == IncidentType.RANSOMWARE:
            actions.extend([
                "Engage law enforcement (FBI)",
                "Do not pay ransom (guidance)",
                "Full system forensics"
            ])
        
        if incident_type == IncidentType.NATION_STATE:
            actions.extend([
                "Notify CISA",
                "Engage national security agencies",
                "Full attribution analysis"
            ])
        
        return actions
    
    def _get_critical_path_items(self, incident_type: IncidentType) -> List[str]:
        """Get critical path items for recovery"""
        
        paths = {
            IncidentType.RANSOMWARE: [
                "Identify patient zeros",
                "Disable ransomware C2",
                "Restore from backups",
                "Verification scan"
            ],
            IncidentType.NATION_STATE: [
                "Assume full compromise",
                "Isolate critical systems",
                "Forensics collection",
                "Full system rebuild"
            ],
            IncidentType.CLOUD_BREACH: [
                "Audit cloud permissions",
                "Isolate compromised resources",
                "Credential rotation",
                "Cloud infrastructure re-hardening"
            ],
            IncidentType.POST_QUANTUM_FAILURE: [
                "Audit all certificates",
                "Rotate affected certificates",
                "Verify key generation",
                "System re-validation"
            ]
        }
        
        return paths.get(incident_type, ["Investigation", "Containment", "Eradication", "Recovery"])
