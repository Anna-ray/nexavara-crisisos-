#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEXAVARA CrisisOS - Business Impact Engine
Converts technical findings to executive-level business metrics
"""

from typing import Dict, Any, List
from datetime import datetime, timezone
import random


class BusinessImpactEngine:
    """
    Calculates business impact metrics from technical incident data.
    Provides financial exposure, operational impact, customer impact, and regulatory risk.
    """
    
    # System criticality multipliers
    SYSTEM_CRITICALITY = {
        'payment_gateway': 5.0,
        'settlement_system': 4.5,
        'trading_platform': 4.0,
        'customer_portal': 3.0,
        'reporting_system': 2.0,
        'backup_system': 1.5,
        'hsm': 5.0,  # Hardware Security Module
        'clearing_gateway': 4.5,
        'authentication_service': 4.0,
    }
    
    # Severity multipliers
    SEVERITY_MULTIPLIERS = {
        'critical': 5.0,
        'high': 3.5,
        'medium': 2.0,
        'low': 1.0,
    }
    
    # Time-of-day multipliers (peak hours = higher impact)
    def get_time_multiplier(self) -> float:
        """Get time-of-day multiplier based on current hour."""
        hour = datetime.now(timezone.utc).hour
        # Peak hours: 9 AM - 5 PM UTC (business hours)
        if 9 <= hour <= 17:
            return 2.5
        # After hours but still active: 6 PM - 11 PM
        elif 18 <= hour <= 23:
            return 1.5
        # Night hours: lower impact
        else:
            return 1.0
    
    def calculate_financial_exposure(
        self,
        severity: str,
        affected_systems: List[str],
        confidence: float,
        incident_type: str = 'cryptographic_failure'
    ) -> Dict[str, Any]:
        """
        Calculate financial exposure based on incident parameters.
        
        Args:
            severity: Incident severity (critical/high/medium/low)
            affected_systems: List of affected system names
            confidence: Confidence score (0.0 - 1.0)
            incident_type: Type of incident
            
        Returns:
            Dictionary with financial metrics
        """
        # Base transaction value per minute (realistic for financial systems)
        base_tpm = 125000  # $125K per minute in transactions
        
        # Calculate system criticality
        system_multiplier = 1.0
        for system in affected_systems:
            system_lower = system.lower()
            for key, multiplier in self.SYSTEM_CRITICALITY.items():
                if key in system_lower:
                    system_multiplier = max(system_multiplier, multiplier)
        
        # Get severity multiplier
        severity_multiplier = self.SEVERITY_MULTIPLIERS.get(severity.lower(), 2.0)
        
        # Get time multiplier
        time_multiplier = self.get_time_multiplier()
        
        # Calculate per-minute exposure
        per_minute_exposure = (
            base_tpm * 
            system_multiplier * 
            severity_multiplier * 
            time_multiplier * 
            confidence
        )
        
        # Estimate incident duration (minutes)
        if severity.lower() == 'critical':
            estimated_duration = random.randint(15, 45)
        elif severity.lower() == 'high':
            estimated_duration = random.randint(30, 90)
        else:
            estimated_duration = random.randint(60, 180)
        
        # Total exposure
        total_exposure = per_minute_exposure * estimated_duration
        
        # Add regulatory fine risk for cryptographic failures
        regulatory_fine = 0
        if 'crypto' in incident_type.lower() or 'security' in incident_type.lower():
            regulatory_fine = random.randint(500000, 2000000)
        
        return {
            'per_minute_exposure': round(per_minute_exposure, 2),
            'estimated_duration_minutes': estimated_duration,
            'total_exposure': round(total_exposure, 2),
            'regulatory_fine_risk': regulatory_fine,
            'total_financial_impact': round(total_exposure + regulatory_fine, 2),
            'currency': 'USD',
            'calculation_timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    def calculate_operational_impact(
        self,
        severity: str,
        affected_systems: List[str],
        confidence: float
    ) -> Dict[str, Any]:
        """
        Calculate operational impact metrics.
        
        Returns:
            Dictionary with operational metrics
        """
        # Base transactions per hour
        base_tph = 4200
        
        # Calculate system criticality
        system_multiplier = 1.0
        for system in affected_systems:
            system_lower = system.lower()
            for key, multiplier in self.SYSTEM_CRITICALITY.items():
                if key in system_lower:
                    system_multiplier = max(system_multiplier, multiplier)
        
        # Severity multiplier
        severity_multiplier = self.SEVERITY_MULTIPLIERS.get(severity.lower(), 2.0)
        
        # Calculate blocked transactions
        transactions_blocked_per_hour = int(
            base_tph * system_multiplier * severity_multiplier * confidence
        )
        
        # Calculate downtime
        if severity.lower() == 'critical':
            estimated_downtime_hours = round(random.uniform(0.25, 1.5), 2)
        elif severity.lower() == 'high':
            estimated_downtime_hours = round(random.uniform(0.5, 3.0), 2)
        else:
            estimated_downtime_hours = round(random.uniform(1.0, 6.0), 2)
        
        # Calculate affected services
        affected_services_count = len(affected_systems)
        
        return {
            'transactions_blocked_per_hour': transactions_blocked_per_hour,
            'estimated_downtime_hours': estimated_downtime_hours,
            'affected_services_count': affected_services_count,
            'service_degradation_percentage': round(confidence * 100, 1),
            'recovery_time_estimate_minutes': int(estimated_downtime_hours * 60),
            'calculation_timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    def calculate_customer_impact(
        self,
        severity: str,
        affected_systems: List[str],
        confidence: float
    ) -> Dict[str, Any]:
        """
        Calculate customer impact metrics.
        
        Returns:
            Dictionary with customer impact metrics
        """
        # Base customer count
        base_customers = 50000
        
        # Calculate system criticality
        system_multiplier = 1.0
        for system in affected_systems:
            system_lower = system.lower()
            for key, multiplier in self.SYSTEM_CRITICALITY.items():
                if key in system_lower:
                    system_multiplier = max(system_multiplier, multiplier)
        
        # Severity multiplier
        severity_multiplier = self.SEVERITY_MULTIPLIERS.get(severity.lower(), 2.0)
        
        # Calculate affected customers
        affected_customers = int(
            base_customers * (system_multiplier / 5.0) * (severity_multiplier / 5.0) * confidence
        )
        
        # Reputation score impact (0-100 scale)
        reputation_impact = round(
            20 * (severity_multiplier / 5.0) * confidence,
            1
        )
        
        # Calculate churn risk
        if severity.lower() == 'critical':
            churn_risk_percentage = round(random.uniform(2.0, 5.0), 2)
        elif severity.lower() == 'high':
            churn_risk_percentage = round(random.uniform(1.0, 3.0), 2)
        else:
            churn_risk_percentage = round(random.uniform(0.5, 1.5), 2)
        
        return {
            'affected_customers': affected_customers,
            'reputation_score_impact': reputation_impact,
            'churn_risk_percentage': churn_risk_percentage,
            'estimated_customer_loss': int(affected_customers * (churn_risk_percentage / 100)),
            'social_media_risk': 'HIGH' if severity.lower() == 'critical' else 'MEDIUM',
            'calculation_timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    def calculate_regulatory_risk(
        self,
        severity: str,
        incident_type: str,
        affected_systems: List[str],
        confidence: float
    ) -> Dict[str, Any]:
        """
        Calculate regulatory risk and compliance implications.
        
        Returns:
            Dictionary with regulatory risk metrics
        """
        # Determine compliance frameworks affected
        compliance_frameworks = []
        potential_violations = []
        
        # Check for cryptographic/security incidents
        if 'crypto' in incident_type.lower() or 'security' in incident_type.lower():
            compliance_frameworks.extend(['PCI-DSS', 'SOX', 'GDPR'])
            potential_violations.extend([
                'Inadequate cryptographic controls',
                'Failure to protect cardholder data',
                'Insufficient security monitoring'
            ])
        
        # Check for payment systems
        for system in affected_systems:
            system_lower = system.lower()
            if 'payment' in system_lower or 'settlement' in system_lower:
                if 'PCI-DSS' not in compliance_frameworks:
                    compliance_frameworks.append('PCI-DSS')
                if 'SOX' not in compliance_frameworks:
                    compliance_frameworks.append('SOX')
        
        # Calculate risk level
        if severity.lower() == 'critical' and confidence > 0.8:
            risk_level = 'HIGH'
            notification_required = True
            notification_deadline_hours = 24
        elif severity.lower() in ['critical', 'high'] and confidence > 0.6:
            risk_level = 'MEDIUM'
            notification_required = True
            notification_deadline_hours = 72
        else:
            risk_level = 'LOW'
            notification_required = False
            notification_deadline_hours = None
        
        # Estimate potential fines
        if risk_level == 'HIGH':
            min_fine = 500000
            max_fine = 5000000
        elif risk_level == 'MEDIUM':
            min_fine = 100000
            max_fine = 1000000
        else:
            min_fine = 10000
            max_fine = 100000
        
        return {
            'risk_level': risk_level,
            'compliance_frameworks_affected': compliance_frameworks,
            'potential_violations': potential_violations,
            'notification_required': notification_required,
            'notification_deadline_hours': notification_deadline_hours,
            'estimated_fine_range': {
                'min': min_fine,
                'max': max_fine,
                'currency': 'USD'
            },
            'audit_trail_required': True,
            'calculation_timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    def calculate_complete_impact(
        self,
        severity: str,
        affected_systems: List[str],
        confidence: float,
        incident_type: str = 'cryptographic_failure',
        incident_description: str = ''
    ) -> Dict[str, Any]:
        """
        Calculate complete business impact across all dimensions.
        
        Args:
            severity: Incident severity
            affected_systems: List of affected systems
            confidence: Confidence score (0.0 - 1.0)
            incident_type: Type of incident
            incident_description: Description of the incident
            
        Returns:
            Complete business impact assessment
        """
        financial = self.calculate_financial_exposure(
            severity, affected_systems, confidence, incident_type
        )
        
        operational = self.calculate_operational_impact(
            severity, affected_systems, confidence
        )
        
        customer = self.calculate_customer_impact(
            severity, affected_systems, confidence
        )
        
        regulatory = self.calculate_regulatory_risk(
            severity, incident_type, affected_systems, confidence
        )
        
        return {
            'incident_summary': {
                'severity': severity.upper(),
                'confidence': round(confidence * 100, 1),
                'affected_systems': affected_systems,
                'incident_type': incident_type,
                'assessment_timestamp': datetime.now(timezone.utc).isoformat()
            },
            'financial_impact': financial,
            'operational_impact': operational,
            'customer_impact': customer,
            'regulatory_risk': regulatory,
            'overall_risk_score': self._calculate_overall_risk_score(
                severity, confidence, regulatory['risk_level']
            )
        }
    
    def _calculate_overall_risk_score(
        self,
        severity: str,
        confidence: float,
        regulatory_risk: str
    ) -> Dict[str, Any]:
        """Calculate overall risk score (0-100)."""
        severity_score = {
            'critical': 90,
            'high': 70,
            'medium': 50,
            'low': 30
        }.get(severity.lower(), 50)
        
        regulatory_score = {
            'HIGH': 30,
            'MEDIUM': 20,
            'LOW': 10
        }.get(regulatory_risk, 15)
        
        overall_score = min(100, int(
            (severity_score * 0.6) + 
            (regulatory_score * 0.2) + 
            (confidence * 100 * 0.2)
        ))
        
        if overall_score >= 80:
            risk_category = 'CRITICAL'
        elif overall_score >= 60:
            risk_category = 'HIGH'
        elif overall_score >= 40:
            risk_category = 'MEDIUM'
        else:
            risk_category = 'LOW'
        
        return {
            'score': overall_score,
            'category': risk_category,
            'confidence': round(confidence * 100, 1)
        }


# Convenience function for quick calculations
def calculate_business_impact(
    severity: str,
    affected_systems: List[str],
    confidence: float = 0.85,
    incident_type: str = 'cryptographic_failure',
    incident_description: str = ''
) -> Dict[str, Any]:
    """
    Quick function to calculate business impact.
    
    Example:
        impact = calculate_business_impact(
            severity='critical',
            affected_systems=['HSM', 'Payment Gateway'],
            confidence=0.89,
            incident_type='post_quantum_cryptographic_failure'
        )
    """
    engine = BusinessImpactEngine()
    return engine.calculate_complete_impact(
        severity=severity,
        affected_systems=affected_systems,
        confidence=confidence,
        incident_type=incident_type,
        incident_description=incident_description
    )


if __name__ == '__main__':
    # Demo usage
    print("=" * 80)
    print("NEXAVARA CrisisOS - Business Impact Engine Demo")
    print("=" * 80)
    print()
    
    impact = calculate_business_impact(
        severity='critical',
        affected_systems=['HSM', 'Cross-Border Clearing Gateway', 'Payment Gateway'],
        confidence=0.89,
        incident_type='post_quantum_cryptographic_failure',
        incident_description='Entropy degradation in HSM during Kyber-1024 handshakes'
    )
    
    print("Financial Impact:")
    print(f"  Total Exposure: ${impact['financial_impact']['total_financial_impact']:,.2f}")
    print(f"  Per Minute: ${impact['financial_impact']['per_minute_exposure']:,.2f}")
    print()
    
    print("Operational Impact:")
    print(f"  Transactions Blocked: {impact['operational_impact']['transactions_blocked_per_hour']:,}/hour")
    print(f"  Estimated Downtime: {impact['operational_impact']['estimated_downtime_hours']} hours")
    print()
    
    print("Customer Impact:")
    print(f"  Affected Customers: {impact['customer_impact']['affected_customers']:,}")
    print(f"  Churn Risk: {impact['customer_impact']['churn_risk_percentage']}%")
    print()
    
    print("Regulatory Risk:")
    print(f"  Risk Level: {impact['regulatory_risk']['risk_level']}")
    print(f"  Frameworks: {', '.join(impact['regulatory_risk']['compliance_frameworks_affected'])}")
    print()
    
    print("Overall Risk Score:")
    print(f"  Score: {impact['overall_risk_score']['score']}/100")
    print(f"  Category: {impact['overall_risk_score']['category']}")
    print()

# Made with Bob