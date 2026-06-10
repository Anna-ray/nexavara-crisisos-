#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEXAVARA CrisisOS - Executive Report Generator
Generates executive-ready crisis briefings and recommendations
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import json


class ExecutiveReportGenerator:
    """
    Generates executive-level crisis reports with clear recommendations
    and business impact metrics.
    """
    
    def generate_executive_briefing(
        self,
        incident_id: str,
        incident_title: str,
        severity: str,
        confidence: float,
        root_cause: str,
        business_impact: Dict[str, Any],
        technical_details: Optional[Dict[str, Any]] = None,
        analysis_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a complete executive crisis briefing.
        
        Args:
            incident_id: Unique incident identifier
            incident_title: Clear, business-focused title
            severity: Incident severity level
            confidence: Confidence score (0.0 - 1.0)
            root_cause: Clear explanation of root cause
            business_impact: Business impact metrics from BusinessImpactEngine
            technical_details: Optional technical details
            analysis_data: Optional analysis data from agents
            
        Returns:
            Complete executive briefing document
        """
        timestamp = datetime.now(timezone.utc)
        
        # Generate recommended actions
        recommended_actions = self._generate_recommended_actions(
            severity=severity,
            business_impact=business_impact,
            root_cause=root_cause
        )
        
        # Calculate risk reduction
        risk_reduction = self._calculate_risk_reduction(
            severity=severity,
            recommended_actions=recommended_actions
        )
        
        # Generate timeline estimate
        implementation_timeline = self._generate_implementation_timeline(
            recommended_actions=recommended_actions,
            severity=severity
        )
        
        # Build the briefing
        briefing = {
            'document_type': 'EXECUTIVE_CRISIS_BRIEFING',
            'generated_at': timestamp.isoformat(),
            'incident_id': incident_id,
            
            'executive_summary': {
                'incident_title': incident_title,
                'severity': severity.upper(),
                'confidence_percentage': round(confidence * 100, 1),
                'status': 'ACTIVE',
                'priority': self._determine_priority(severity, confidence)
            },
            
            'root_cause': {
                'summary': root_cause,
                'technical_details': technical_details.get('root_cause_details', '') if technical_details else '',
                'contributing_factors': self._extract_contributing_factors(root_cause, technical_details)
            },
            
            'business_impact': {
                'financial': {
                    'total_exposure': business_impact['financial_impact']['total_financial_impact'],
                    'per_minute_loss': business_impact['financial_impact']['per_minute_exposure'],
                    'regulatory_fine_risk': business_impact['financial_impact']['regulatory_fine_risk'],
                    'currency': 'USD'
                },
                'operational': {
                    'transactions_blocked_per_hour': business_impact['operational_impact']['transactions_blocked_per_hour'],
                    'estimated_downtime_hours': business_impact['operational_impact']['estimated_downtime_hours'],
                    'affected_services': business_impact['operational_impact']['affected_services_count']
                },
                'customer': {
                    'affected_customers': business_impact['customer_impact']['affected_customers'],
                    'reputation_impact': business_impact['customer_impact']['reputation_score_impact'],
                    'churn_risk_percentage': business_impact['customer_impact']['churn_risk_percentage']
                },
                'regulatory': {
                    'risk_level': business_impact['regulatory_risk']['risk_level'],
                    'compliance_frameworks': business_impact['regulatory_risk']['compliance_frameworks_affected'],
                    'notification_required': business_impact['regulatory_risk']['notification_required'],
                    'notification_deadline_hours': business_impact['regulatory_risk']['notification_deadline_hours']
                }
            },
            
            'recommended_actions': recommended_actions,
            
            'risk_mitigation': {
                'expected_risk_reduction_percentage': risk_reduction,
                'implementation_time_minutes': implementation_timeline['total_minutes'],
                'implementation_phases': implementation_timeline['phases']
            },
            
            'stakeholder_notifications': self._generate_stakeholder_notifications(
                severity=severity,
                business_impact=business_impact
            ),
            
            'next_steps': self._generate_next_steps(
                severity=severity,
                recommended_actions=recommended_actions
            )
        }
        
        return briefing
    
    def _generate_recommended_actions(
        self,
        severity: str,
        business_impact: Dict[str, Any],
        root_cause: str
    ) -> List[Dict[str, Any]]:
        """Generate prioritized recommended actions."""
        actions = []
        
        # Critical immediate actions
        if severity.lower() == 'critical':
            actions.append({
                'priority': 1,
                'action': 'Suspend affected settlement channels immediately',
                'rationale': 'Prevent further financial exposure and data integrity issues',
                'estimated_time_minutes': 5,
                'responsible_team': 'Operations',
                'approval_required': False
            })
        
        # Cryptographic remediation
        if 'crypto' in root_cause.lower() or 'key' in root_cause.lower():
            actions.append({
                'priority': 2,
                'action': 'Rotate cryptographic keys and certificates',
                'rationale': 'Restore cryptographic integrity and security posture',
                'estimated_time_minutes': 15,
                'responsible_team': 'Security Operations',
                'approval_required': False
            })
        
        # HSM-specific actions
        if 'hsm' in root_cause.lower() or 'entropy' in root_cause.lower():
            actions.append({
                'priority': 2,
                'action': 'Restart HSM entropy pools and verify randomness quality',
                'rationale': 'Address root cause of cryptographic failures',
                'estimated_time_minutes': 10,
                'responsible_team': 'Infrastructure',
                'approval_required': False
            })
        
        # Regulatory notifications
        if business_impact['regulatory_risk']['notification_required']:
            actions.append({
                'priority': 3,
                'action': f"Notify financial regulators within {business_impact['regulatory_risk']['notification_deadline_hours']} hours",
                'rationale': 'Maintain regulatory compliance and avoid additional penalties',
                'estimated_time_minutes': 120,
                'responsible_team': 'Legal & Compliance',
                'approval_required': True
            })
        
        # System recovery
        actions.append({
            'priority': 4,
            'action': 'Initiate emergency security review and system validation',
            'rationale': 'Ensure no additional vulnerabilities or compromises',
            'estimated_time_minutes': 180,
            'responsible_team': 'Security',
            'approval_required': True
        })
        
        # Customer communication
        if business_impact['customer_impact']['affected_customers'] > 10000:
            actions.append({
                'priority': 5,
                'action': 'Prepare customer communication and status updates',
                'rationale': 'Maintain customer trust and manage reputation',
                'estimated_time_minutes': 60,
                'responsible_team': 'Customer Relations',
                'approval_required': True
            })
        
        # Post-incident review
        actions.append({
            'priority': 6,
            'action': 'Schedule post-incident review within 48 hours',
            'rationale': 'Identify systemic improvements and prevent recurrence',
            'estimated_time_minutes': 120,
            'responsible_team': 'Engineering Leadership',
            'approval_required': False
        })
        
        return actions
    
    def _calculate_risk_reduction(
        self,
        severity: str,
        recommended_actions: List[Dict[str, Any]]
    ) -> int:
        """Calculate expected risk reduction percentage."""
        if severity.lower() == 'critical':
            base_reduction = 95
        elif severity.lower() == 'high':
            base_reduction = 85
        elif severity.lower() == 'medium':
            base_reduction = 75
        else:
            base_reduction = 90
        
        # Adjust based on number of actions
        action_count = len(recommended_actions)
        if action_count >= 5:
            return min(99, base_reduction + 2)
        
        return base_reduction
    
    def _generate_implementation_timeline(
        self,
        recommended_actions: List[Dict[str, Any]],
        severity: str
    ) -> Dict[str, Any]:
        """Generate implementation timeline."""
        phases = []
        total_minutes = 0
        
        # Group actions by priority
        immediate_actions = [a for a in recommended_actions if a['priority'] <= 2]
        short_term_actions = [a for a in recommended_actions if 3 <= a['priority'] <= 4]
        follow_up_actions = [a for a in recommended_actions if a['priority'] >= 5]
        
        if immediate_actions:
            immediate_time = sum(a['estimated_time_minutes'] for a in immediate_actions)
            phases.append({
                'phase': 'Immediate Response',
                'duration_minutes': immediate_time,
                'actions': [a['action'] for a in immediate_actions]
            })
            total_minutes += immediate_time
        
        if short_term_actions:
            short_term_time = sum(a['estimated_time_minutes'] for a in short_term_actions)
            phases.append({
                'phase': 'Short-term Mitigation',
                'duration_minutes': short_term_time,
                'actions': [a['action'] for a in short_term_actions]
            })
            total_minutes += short_term_time
        
        if follow_up_actions:
            follow_up_time = sum(a['estimated_time_minutes'] for a in follow_up_actions)
            phases.append({
                'phase': 'Follow-up & Recovery',
                'duration_minutes': follow_up_time,
                'actions': [a['action'] for a in follow_up_actions]
            })
            total_minutes += follow_up_time
        
        return {
            'total_minutes': total_minutes,
            'total_hours': round(total_minutes / 60, 1),
            'phases': phases
        }
    
    def _determine_priority(self, severity: str, confidence: float) -> str:
        """Determine executive priority level."""
        if severity.lower() == 'critical' and confidence >= 0.8:
            return 'P0 - IMMEDIATE'
        elif severity.lower() == 'critical' or (severity.lower() == 'high' and confidence >= 0.8):
            return 'P1 - URGENT'
        elif severity.lower() == 'high':
            return 'P2 - HIGH'
        else:
            return 'P3 - NORMAL'
    
    def _extract_contributing_factors(
        self,
        root_cause: str,
        technical_details: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Extract contributing factors from root cause and technical details."""
        factors = []
        
        # Parse from root cause
        if 'peak' in root_cause.lower() or 'load' in root_cause.lower():
            factors.append('High system load during peak hours')
        
        if 'entropy' in root_cause.lower():
            factors.append('Insufficient entropy pool management')
        
        if 'kyber' in root_cause.lower() or 'pqc' in root_cause.lower():
            factors.append('Post-quantum cryptographic algorithm complexity')
        
        # Add from technical details if available
        if technical_details and 'contributing_factors' in technical_details:
            factors.extend(technical_details['contributing_factors'])
        
        # Default if none found
        if not factors:
            factors.append('Under investigation')
        
        return factors
    
    def _generate_stakeholder_notifications(
        self,
        severity: str,
        business_impact: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate stakeholder notification requirements."""
        notifications = []
        
        # Executive leadership
        if severity.lower() in ['critical', 'high']:
            notifications.append({
                'stakeholder': 'Executive Leadership (CEO, CTO, CFO)',
                'notification_type': 'Immediate',
                'method': 'Phone + Email',
                'deadline_minutes': 15
            })
        
        # Board of Directors
        if severity.lower() == 'critical' and business_impact['financial_impact']['total_financial_impact'] > 10000000:
            notifications.append({
                'stakeholder': 'Board of Directors',
                'notification_type': 'Urgent',
                'method': 'Email + Briefing Document',
                'deadline_minutes': 60
            })
        
        # Regulators
        if business_impact['regulatory_risk']['notification_required']:
            notifications.append({
                'stakeholder': 'Financial Regulators',
                'notification_type': 'Mandatory',
                'method': 'Official Filing',
                'deadline_minutes': business_impact['regulatory_risk']['notification_deadline_hours'] * 60
            })
        
        # Customers
        if business_impact['customer_impact']['affected_customers'] > 5000:
            notifications.append({
                'stakeholder': 'Affected Customers',
                'notification_type': 'Required',
                'method': 'Email + Status Page',
                'deadline_minutes': 120
            })
        
        return notifications
    
    def _generate_next_steps(
        self,
        severity: str,
        recommended_actions: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate clear next steps for executives."""
        next_steps = []
        
        # Immediate actions
        immediate = [a for a in recommended_actions if a['priority'] <= 2]
        if immediate:
            next_steps.append(f"Execute {len(immediate)} immediate response actions within 30 minutes")
        
        # Approval requirements
        approval_needed = [a for a in recommended_actions if a.get('approval_required', False)]
        if approval_needed:
            next_steps.append(f"Review and approve {len(approval_needed)} actions requiring executive authorization")
        
        # Monitoring
        next_steps.append("Monitor system recovery and financial impact in real-time")
        
        # Communication
        next_steps.append("Coordinate stakeholder communications per notification schedule")
        
        # Post-incident
        next_steps.append("Schedule post-incident review within 48 hours")
        
        return next_steps
    
    def format_as_text(self, briefing: Dict[str, Any]) -> str:
        """Format briefing as readable text report."""
        lines = []
        
        lines.append("=" * 80)
        lines.append("EXECUTIVE CRISIS BRIEFING")
        lines.append("=" * 80)
        lines.append("")
        
        # Header
        summary = briefing['executive_summary']
        lines.append(f"Incident: {summary['incident_title']}")
        lines.append(f"Severity: {summary['severity']}")
        lines.append(f"Confidence: {summary['confidence_percentage']}%")
        lines.append(f"Priority: {summary['priority']}")
        lines.append(f"Generated: {briefing['generated_at']}")
        lines.append("")
        
        # Root Cause
        lines.append("Root Cause:")
        lines.append(f"  {briefing['root_cause']['summary']}")
        lines.append("")
        if briefing['root_cause']['contributing_factors']:
            lines.append("Contributing Factors:")
            for factor in briefing['root_cause']['contributing_factors']:
                lines.append(f"  • {factor}")
            lines.append("")
        
        # Business Impact
        lines.append("Estimated Exposure:")
        financial = briefing['business_impact']['financial']
        lines.append(f"  - Financial: ${financial['total_exposure']:,.0f}")
        lines.append(f"  - Per Minute Loss: ${financial['per_minute_loss']:,.0f}/min")
        
        operational = briefing['business_impact']['operational']
        lines.append(f"  - Operational: {operational['transactions_blocked_per_hour']:,} transactions/hour blocked")
        
        customer = briefing['business_impact']['customer']
        lines.append(f"  - Customer Impact: {customer['affected_customers']:,} customers affected")
        
        regulatory = briefing['business_impact']['regulatory']
        lines.append(f"  - Regulatory Risk: {regulatory['risk_level']}")
        if regulatory['compliance_frameworks']:
            lines.append(f"    Frameworks: {', '.join(regulatory['compliance_frameworks'])}")
        lines.append("")
        
        # Recommended Actions
        lines.append("Recommended Actions:")
        for i, action in enumerate(briefing['recommended_actions'], 1):
            lines.append(f"  {i}. {action['action']}")
            lines.append(f"     Rationale: {action['rationale']}")
            lines.append(f"     Time: {action['estimated_time_minutes']} minutes | Team: {action['responsible_team']}")
            if action.get('approval_required'):
                lines.append(f"     ⚠️  APPROVAL REQUIRED")
            lines.append("")
        
        # Risk Mitigation
        mitigation = briefing['risk_mitigation']
        lines.append(f"Expected Risk Reduction: {mitigation['expected_risk_reduction_percentage']}%")
        lines.append(f"Implementation Time: {mitigation['implementation_time_minutes']} minutes ({mitigation['implementation_time_minutes'] / 60:.1f} hours)")
        lines.append("")
        
        # Next Steps
        lines.append("Next Steps:")
        for i, step in enumerate(briefing['next_steps'], 1):
            lines.append(f"  {i}. {step}")
        lines.append("")
        
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def format_as_json(self, briefing: Dict[str, Any]) -> str:
        """Format briefing as JSON."""
        return json.dumps(briefing, indent=2)
    
    def format_as_html(self, briefing: Dict[str, Any]) -> str:
        """Format briefing as HTML (basic)."""
        # This would be expanded for full HTML rendering
        return f"<pre>{self.format_as_text(briefing)}</pre>"


# Convenience function
def generate_executive_report(
    incident_id: str,
    incident_title: str,
    severity: str,
    confidence: float,
    root_cause: str,
    business_impact: Dict[str, Any],
    format: str = 'text'
) -> str:
    """
    Quick function to generate an executive report.
    
    Args:
        format: 'text', 'json', or 'html'
    """
    generator = ExecutiveReportGenerator()
    briefing = generator.generate_executive_briefing(
        incident_id=incident_id,
        incident_title=incident_title,
        severity=severity,
        confidence=confidence,
        root_cause=root_cause,
        business_impact=business_impact
    )
    
    if format == 'json':
        return generator.format_as_json(briefing)
    elif format == 'html':
        return generator.format_as_html(briefing)
    else:
        return generator.format_as_text(briefing)


if __name__ == '__main__':
    # Demo usage
    from business_impact import calculate_business_impact
    
    print("=" * 80)
    print("NEXAVARA CrisisOS - Executive Report Generator Demo")
    print("=" * 80)
    print()
    
    # Calculate business impact
    impact = calculate_business_impact(
        severity='critical',
        affected_systems=['HSM', 'Cross-Border Clearing Gateway', 'Payment Gateway'],
        confidence=0.89,
        incident_type='post_quantum_cryptographic_failure'
    )
    
    # Generate report
    report = generate_executive_report(
        incident_id='PQC-INCIDENT-20260610-152800',
        incident_title='Post-Quantum Cryptographic Failure',
        severity='critical',
        confidence=0.89,
        root_cause='HSM entropy starvation under peak Kyber-1024 load',
        business_impact=impact,
        format='text'
    )
    
    print(report)

# Made with Bob