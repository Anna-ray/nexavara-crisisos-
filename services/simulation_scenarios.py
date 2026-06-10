"""
Simulation Scenarios - Predefined crisis scenarios for demonstration
"""

from typing import List, Dict, Any
from datetime import datetime, timezone

from services.war_room_models import (
    IncidentType, Evidence, SeverityLevel, SimulationScenario,
    Incident
)


class SimulationScenarioLibrary:
    """
    Pre-defined incident scenarios for hackathon demonstration.
    Each scenario is designed to showcase agent collaboration.
    """
    
    @staticmethod
    def get_scenario_ransomware_attack() -> SimulationScenario:
        """
        Scenario 1: Sophisticated ransomware targeting financial infrastructure
        """
        
        return SimulationScenario(
            name="Ransomware Attack - LockBit Evolution",
            description="Sophisticated ransomware targeting financial infrastructure. Multiple exfiltration points detected.",
            incident_type=IncidentType.RANSOMWARE,
            initial_evidence=[
                Evidence(
                    source="EDR System",
                    metric_name="suspicious_process_execution",
                    value="cmd.exe executing from temp directory",
                    threshold="normal_behavior",
                    severity=SeverityLevel.HIGH,
                    confidence=0.92
                ),
                Evidence(
                    source="Network IDS",
                    metric_name="c2_communication",
                    value="192.0.2.100:443",
                    threshold="known_malware_c2",
                    severity=SeverityLevel.CRITICAL,
                    confidence=0.88
                ),
                Evidence(
                    source="File Integrity Monitor",
                    metric_name="mass_file_encryption",
                    value="1,247 files encrypted in 1 hour",
                    threshold="normal_operation",
                    severity=SeverityLevel.CRITICAL,
                    confidence=0.95
                )
            ],
            expected_severity=SeverityLevel.CRITICAL,
            expected_financial_impact=2_500_000,
            expected_regulatory_impact="HIGH",
            progression_steps=[
                {
                    "timestamp_offset_minutes": 0,
                    "stage": "Initial Detection",
                    "description": "EDR detects suspicious process execution"
                },
                {
                    "timestamp_offset_minutes": 5,
                    "stage": "C2 Detection",
                    "description": "Network IDS identifies C2 communication"
                },
                {
                    "timestamp_offset_minutes": 10,
                    "stage": "Lateral Movement",
                    "description": "Ransomware spreads across SMB shares"
                },
                {
                    "timestamp_offset_minutes": 20,
                    "stage": "Data Exfiltration",
                    "description": "Attacker exfiltrating sensitive data"
                },
                {
                    "timestamp_offset_minutes": 30,
                    "stage": "Ransom Note",
                    "description": "Ransom demand: $5M in Bitcoin"
                }
            ],
            duration_minutes=60
        )
    
    @staticmethod
    def get_scenario_nation_state_attack() -> SimulationScenario:
        """
        Scenario 2: Nation-state APT targeting cryptographic infrastructure
        """
        
        return SimulationScenario(
            name="Nation-State Attack - Post-Quantum Cryptography Compromise",
            description="Advanced persistent threat with focus on quantum-resistant cryptography. High sophistication indicators.",
            incident_type=IncidentType.NATION_STATE,
            initial_evidence=[
                Evidence(
                    source="HSM Monitoring",
                    metric_name="entropy_degradation",
                    value=0.12,
                    threshold=0.80,
                    severity=SeverityLevel.CRITICAL,
                    confidence=0.96
                ),
                Evidence(
                    source="Key Generation Audit",
                    metric_name="kyber_generation_latency",
                    value=847,  # milliseconds
                    threshold=12,  # normal
                    severity=SeverityLevel.CRITICAL,
                    confidence=0.94
                ),
                Evidence(
                    source="Supply Chain Analysis",
                    metric_name="hsm_firmware_tampering",
                    value="Modified bootloader detected",
                    threshold="integrity_verified",
                    severity=SeverityLevel.CRITICAL,
                    confidence=0.88
                ),
                Evidence(
                    source="Threat Intelligence",
                    metric_name="mitre_techniques",
                    value="T1583.005, T1589.001, T1591.004",  # MITRE ATT&CK
                    threshold="known_state_sponsored_patterns",
                    severity=SeverityLevel.HIGH,
                    confidence=0.90
                )
            ],
            expected_severity=SeverityLevel.CRITICAL,
            expected_financial_impact=18_200_000,
            expected_regulatory_impact="CRITICAL",
            progression_steps=[
                {
                    "timestamp_offset_minutes": 0,
                    "stage": "Detection",
                    "description": "HSM entropy degradation detected"
                },
                {
                    "timestamp_offset_minutes": 5,
                    "stage": "Investigation",
                    "description": "Analysis reveals key generation compromise"
                },
                {
                    "timestamp_offset_minutes": 15,
                    "stage": "Supply Chain Analysis",
                    "description": "Firmware tampering confirmed"
                },
                {
                    "timestamp_offset_minutes": 25,
                    "stage": "Attribution",
                    "description": "Attribution to known APT group"
                },
                {
                    "timestamp_offset_minutes": 40,
                    "stage": "Regulatory Notification",
                    "description": "CISA and regulators notified"
                }
            ],
            duration_minutes=90
        )
    
    @staticmethod
    def get_scenario_cloud_breach() -> SimulationScenario:
        """
        Scenario 3: Cloud credential compromise leading to data breach
        """
        
        return SimulationScenario(
            name="Cloud Breach - AWS Credential Compromise",
            description="Compromised developer credentials leading to unauthorized cloud access and data exfiltration.",
            incident_type=IncidentType.CLOUD_BREACH,
            initial_evidence=[
                Evidence(
                    source="CloudTrail",
                    metric_name="unusual_api_calls",
                    value="145,000 S3 GetObject calls in 2 hours",
                    threshold="baseline_behavior",
                    severity=SeverityLevel.HIGH,
                    confidence=0.91
                ),
                Evidence(
                    source="GuardDuty",
                    metric_name="credential_compromise",
                    value="Dev credentials used from TOR exit node",
                    threshold="normal_access",
                    severity=SeverityLevel.CRITICAL,
                    confidence=0.93
                ),
                Evidence(
                    source="S3 Access Logs",
                    metric_name="data_exfiltration",
                    value="847GB downloaded to external IP",
                    threshold="zero_baseline",
                    severity=SeverityLevel.CRITICAL,
                    confidence=0.94
                )
            ],
            expected_severity=SeverityLevel.CRITICAL,
            expected_financial_impact=12_500_000,
            expected_regulatory_impact="HIGH",
            progression_steps=[
                {
                    "timestamp_offset_minutes": 0,
                    "stage": "Anomaly Detection",
                    "description": "Unusual API activity detected"
                },
                {
                    "timestamp_offset_minutes": 8,
                    "stage": "Credential Identification",
                    "description": "Compromised developer credentials identified"
                },
                {
                    "timestamp_offset_minutes": 15,
                    "stage": "Scope Assessment",
                    "description": "Data exposure scope determined: 145K customers"
                },
                {
                    "timestamp_offset_minutes": 25,
                    "stage": "Credential Revocation",
                    "description": "Credentials revoked, access blocked"
                }
            ],
            duration_minutes=60
        )
    
    @staticmethod
    def get_scenario_supply_chain_attack() -> SimulationScenario:
        """
        Scenario 4: Supply chain attack through compromised dependency
        """
        
        return SimulationScenario(
            name="Supply Chain Attack - Compromised Library",
            description="Popular open-source library compromised to inject backdoor affecting thousands of enterprises.",
            incident_type=IncidentType.SUPPLY_CHAIN,
            initial_evidence=[
                Evidence(
                    source="Software Composition Analysis",
                    metric_name="malicious_dependency",
                    value="crypto-utils v2.3.1 contains backdoor",
                    threshold="trusted_libraries",
                    severity=SeverityLevel.CRITICAL,
                    confidence=0.92
                ),
                Evidence(
                    source="Binary Analysis",
                    metric_name="reverse_shell_capability",
                    value="Obfuscated reverse shell in libcrypto.so",
                    threshold="zero_threat",
                    severity=SeverityLevel.CRITICAL,
                    confidence=0.89
                ),
                Evidence(
                    source="Threat Intelligence",
                    metric_name="known_bad_c2",
                    value="Command server linked to APT29",
                    threshold="known_malicious",
                    severity=SeverityLevel.CRITICAL,
                    confidence=0.91
                )
            ],
            expected_severity=SeverityLevel.CRITICAL,
            expected_financial_impact=25_000_000,
            expected_regulatory_impact="CRITICAL",
            progression_steps=[
                {
                    "timestamp_offset_minutes": 0,
                    "stage": "Detection",
                    "description": "SCA tool detects malicious dependency"
                },
                {
                    "timestamp_offset_minutes": 10,
                    "stage": "Scope Analysis",
                    "description": "Identifying affected internal services"
                },
                {
                    "timestamp_offset_minutes": 20,
                    "stage": "Attribution",
                    "description": "Link to known APT group confirmed"
                },
                {
                    "timestamp_offset_minutes": 35,
                    "stage": "Containment",
                    "description": "Force update to patched version"
                }
            ],
            duration_minutes=75
        )
    
    @staticmethod
    def get_scenario_post_quantum_failure() -> SimulationScenario:
        """
        Scenario 5: Post-quantum cryptography system failure
        """
        
        return SimulationScenario(
            name="Post-Quantum Failure - HSM System Compromise",
            description="Critical failure in post-quantum cryptography infrastructure requiring immediate certificate rotation.",
            incident_type=IncidentType.POST_QUANTUM_FAILURE,
            initial_evidence=[
                Evidence(
                    source="Cryptographic Audit",
                    metric_name="certificate_validation_failures",
                    value="1,247 failures in 30 minutes",
                    threshold="zero_failures",
                    severity=SeverityLevel.CRITICAL,
                    confidence=0.96
                ),
                Evidence(
                    source="HSM Cluster Monitor",
                    metric_name="entropy_pool_depletion",
                    value="Entropy: 2% (critical threshold: 20%)",
                    threshold=20,
                    severity=SeverityLevel.CRITICAL,
                    confidence=0.98
                ),
                Evidence(
                    source="Performance Metrics",
                    metric_name="key_generation_time",
                    value="847ms for Kyber-1024 (normal: 12ms)",
                    threshold=12,
                    severity=SeverityLevel.HIGH,
                    confidence=0.94
                )
            ],
            expected_severity=SeverityLevel.CRITICAL,
            expected_financial_impact=8_500_000,
            expected_regulatory_impact="MEDIUM",
            progression_steps=[
                {
                    "timestamp_offset_minutes": 0,
                    "stage": "Anomaly Detection",
                    "description": "Certificate validation failures detected"
                },
                {
                    "timestamp_offset_minutes": 5,
                    "stage": "Root Cause Analysis",
                    "description": "HSM entropy depletion identified"
                },
                {
                    "timestamp_offset_minutes": 15,
                    "stage": "Impact Assessment",
                    "description": "127 systems affected, 42K customers impacted"
                },
                {
                    "timestamp_offset_minutes": 25,
                    "stage": "Certificate Rotation",
                    "description": "Emergency certificate rotation initiated"
                }
            ],
            duration_minutes=60
        )
    
    @staticmethod
    def get_scenario_identity_compromise() -> SimulationScenario:
        """
        Scenario 6: Privileged identity compromise
        """
        
        return SimulationScenario(
            name="Identity Compromise - Privileged Account Takeover",
            description="Sophisticated attack leading to privileged account compromise and potential lateral movement.",
            incident_type=IncidentType.IDENTITY_COMPROMISE,
            initial_evidence=[
                Evidence(
                    source="Identity Provider",
                    metric_name="mfa_bypass_attempt",
                    value="MFA challenge bypass detected for admin@company.com",
                    threshold="zero_bypass_tolerance",
                    severity=SeverityLevel.CRITICAL,
                    confidence=0.93
                ),
                Evidence(
                    source="SIEM",
                    metric_name="unusual_privileged_access",
                    value="Admin accessed systems from unknown location at 3AM",
                    threshold="baseline_admin_behavior",
                    severity=SeverityLevel.HIGH,
                    confidence=0.88
                ),
                Evidence(
                    source="Threat Intelligence",
                    metric_name="credential_spray_attempt",
                    value="1,247 login attempts on executive mailboxes",
                    threshold="baseline_login_rate",
                    severity=SeverityLevel.HIGH,
                    confidence=0.91
                )
            ],
            expected_severity=SeverityLevel.HIGH,
            expected_financial_impact=5_200_000,
            expected_regulatory_impact="MEDIUM",
            progression_steps=[
                {
                    "timestamp_offset_minutes": 0,
                    "stage": "Detection",
                    "description": "MFA bypass attempts detected"
                },
                {
                    "timestamp_offset_minutes": 8,
                    "stage": "Investigation",
                    "description": "Privilege escalation attempts identified"
                },
                {
                    "timestamp_offset_minutes": 20,
                    "stage": "Scope Determination",
                    "description": "12 privileged accounts potentially compromised"
                },
                {
                    "timestamp_offset_minutes": 35,
                    "stage": "Remediation",
                    "description": "Force password resets, MFA re-enrollment"
                }
            ],
            duration_minutes=60
        )
    
    @staticmethod
    def get_all_scenarios() -> List[SimulationScenario]:
        """Get all available scenarios"""
        return [
            SimulationScenarioLibrary.get_scenario_ransomware_attack(),
            SimulationScenarioLibrary.get_scenario_nation_state_attack(),
            SimulationScenarioLibrary.get_scenario_cloud_breach(),
            SimulationScenarioLibrary.get_scenario_supply_chain_attack(),
            SimulationScenarioLibrary.get_scenario_post_quantum_failure(),
            SimulationScenarioLibrary.get_scenario_identity_compromise()
        ]
    
    @staticmethod
    def get_scenario_by_type(incident_type: IncidentType) -> SimulationScenario:
        """Get a specific scenario by incident type"""
        
        scenarios_map = {
            IncidentType.RANSOMWARE: SimulationScenarioLibrary.get_scenario_ransomware_attack,
            IncidentType.NATION_STATE: SimulationScenarioLibrary.get_scenario_nation_state_attack,
            IncidentType.CLOUD_BREACH: SimulationScenarioLibrary.get_scenario_cloud_breach,
            IncidentType.SUPPLY_CHAIN: SimulationScenarioLibrary.get_scenario_supply_chain_attack,
            IncidentType.POST_QUANTUM_FAILURE: SimulationScenarioLibrary.get_scenario_post_quantum_failure,
            IncidentType.IDENTITY_COMPROMISE: SimulationScenarioLibrary.get_scenario_identity_compromise
        }
        
        scenario_func = scenarios_map.get(incident_type)
        if scenario_func:
            return scenario_func()
        
        raise ValueError(f"No scenario found for incident type: {incident_type}")
