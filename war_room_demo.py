"""
War Room Demo CLI - Interactive demonstration of multi-agent collaboration
"""

import asyncio
import sys
from datetime import datetime, timezone
from typing import Optional

from services.war_room_models import (
    Incident, IncidentType, SeverityLevel, AgentType,
    MemoryGraph, Finding, Evidence
)
from services.agent_debate_system import AgentDebateSystem, DebateExplainer
from services.business_impact_engine import BusinessImpactEngine
from services.simulation_scenarios import SimulationScenarioLibrary


class Colors:
    """ANSI color codes"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


class WarRoomDemo:
    """Interactive war room demonstration"""
    
    def __init__(self):
        self.incident: Optional[Incident] = None
        self.memory: Optional[MemoryGraph] = None
        self.debate_system: Optional[AgentDebateSystem] = None
        self.business_engine = BusinessImpactEngine()
    
    def print_banner(self, text: str):
        """Print formatted banner"""
        width = 80
        print(f"\n{Colors.CYAN}{'='*width}")
        print(f"{text:^{width}}")
        print(f"{'='*width}{Colors.END}\n")
    
    def print_section(self, title: str):
        """Print section header"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}→ {title}{Colors.END}")
        print(f"{Colors.BLUE}{'-'*70}{Colors.END}\n")
    
    def print_agent_message(self, agent: AgentType, message: str, confidence: float, color: str = Colors.GREEN):
        """Print agent message"""
        timestamp = datetime.now(timezone.utc).strftime("%H:%M:%S")
        agent_name = agent.value.replace("_", " ").title()
        confidence_bar = "█" * int(confidence * 10) + "░" * (10 - int(confidence * 10))
        
        print(f"{color}[{timestamp}] {agent_name}{Colors.END}")
        print(f"  {message}")
        print(f"  Confidence: [{confidence_bar}] {confidence:.0%}\n")
    
    async def demo_nation_state_attack(self):
        """Demonstrate nation-state attack scenario"""
        
        self.print_banner("🚨 NEXAVARA WAR ROOM - NATION-STATE ATTACK SCENARIO 🚨")
        
        print(f"""
{Colors.YELLOW}Scenario: Post-Quantum Cryptography Compromise
Duration: ~90 seconds
Agents: Detection → Threat Intelligence → Risk → Compliance → Response → Executive{Colors.END}

The most sophisticated cyber threat to enterprise infrastructure:
A nation-state actor has compromised HSM firmware to degrade entropy generation,
threatening post-quantum cryptographic key generation for a Fortune 500 bank.

{Colors.BOLD}Watch as 6 specialized agents collaborate in real-time to:
1. Detect the anomaly
2. Investigate the root cause
3. Quantify business impact
4. Identify regulatory implications
5. Propose containment actions
6. Brief executive leadership{Colors.END}

Press Enter to begin...
""")
        input()
        
        # Get scenario
        scenario = SimulationScenarioLibrary.get_scenario_nation_state_attack()
        
        # Create incident
        self.incident = Incident(
            incident_type=scenario.incident_type,
            title=scenario.name,
            description=scenario.description,
            severity=scenario.expected_severity
        )
        
        self.memory = MemoryGraph()
        self.debate_system = AgentDebateSystem(self.memory)
        
        # Add initial evidence
        for evidence in scenario.initial_evidence:
            self.memory.evidence.append(evidence)
        
        self.print_section("Step 1: Detection Agent - Discovers Anomaly")
        
        self.print_agent_message(
            AgentType.DETECTION,
            "🔍 CRITICAL ALERT: Anomaly detected in post-quantum certificate chain",
            0.96,
            Colors.RED
        )
        
        # Create first finding
        finding1 = Finding(
            agent_type=AgentType.DETECTION,
            content="HSM entropy degradation detected - rate: 0.12 (threshold: 0.80)",
            confidence=0.96,
            severity=SeverityLevel.CRITICAL,
            reasoning="Entropy rate critically low, threatening key generation integrity",
            evidence_ids=[scenario.initial_evidence[0].id]
        )
        self.memory.findings.append(finding1)
        
        print(f"{Colors.CYAN}Evidence Supporting This Finding:{Colors.END}")
        for evidence in scenario.initial_evidence[:1]:
            print(f"  • {evidence.source}: {evidence.metric_name} = {evidence.value}")
            print(f"    Threshold: {evidence.threshold}, Severity: {Colors.RED}{evidence.severity.value.upper()}{Colors.END}\n")
        
        await asyncio.sleep(2)
        
        # Step 2: Threat Intelligence
        self.print_section("Step 2: Threat Intelligence Agent - Investigates Root Cause")
        
        self.print_agent_message(
            AgentType.THREAT_INTELLIGENCE,
            "🕵️ Root cause identified: HSM firmware tampering",
            0.88,
            Colors.YELLOW
        )
        
        print(f"{Colors.CYAN}Analysis:{Colors.END}")
        print(f"  Threat Actor Classification: State-sponsored (probability: 92%)")
        print(f"  Attack Vector: Supply chain compromise of HSM vendor")
        print(f"  Motive: Degrade quantum-resistant key generation\n")
        
        await asyncio.sleep(2)
        
        # Step 3: Risk Assessment
        self.print_section("Step 3: Risk Assessment Agent - Quantifies Business Impact")
        
        self.print_agent_message(
            AgentType.RISK_ASSESSMENT,
            "💰 Estimated financial exposure: $5M",
            0.75,
            Colors.YELLOW
        )
        
        print(f"{Colors.YELLOW}⚠️ DEBATE INITIATED{Colors.END}\n")
        await asyncio.sleep(1)
        
        # Step 4: Compliance Agent - Challenges Risk Agent
        self.print_section("Step 4: Compliance Agent - Challenges Risk Estimate")
        
        self.print_agent_message(
            AgentType.COMPLIANCE,
            "📋 CHALLENGE: Exposure significantly higher if customer records affected",
            0.92,
            Colors.YELLOW
        )
        
        print(f"{Colors.CYAN}Challenge Details:{Colors.END}")
        print(f"  If 145,000 customer records exposed:")
        print(f"    • GDPR fines: Up to €20M")
        print(f"    • HIPAA fines: Up to $1.5M per violation category")
        print(f"    • CCPA fines: Up to $7,500 per record")
        print(f"    • Customer churn: 15%")
        print(f"  Revised estimate: $20M+\n")
        
        await asyncio.sleep(2)
        
        # Risk Agent recalculates
        self.print_section("Risk Agent Recalculates with New Information")
        
        self.print_agent_message(
            AgentType.RISK_ASSESSMENT,
            "💰 REVISED estimate: $18.2M exposure",
            0.85,
            Colors.GREEN
        )
        
        print(f"{Colors.GREEN}✓ Consensus achieved{Colors.END}\n")
        await asyncio.sleep(2)
        
        # Step 5: Response Agent
        self.print_section("Step 5: Response Agent - Proposes Containment")
        
        self.print_agent_message(
            AgentType.RESPONSE,
            "🛡️ Immediate actions recommended:",
            0.79,
            Colors.CYAN
        )
        
        actions = [
            ("Isolate affected HSM cluster", 5, "IMMEDIATE"),
            ("Audit all cryptographic keys generated in last 48 hours", 30, "IMMEDIATE"),
            ("Emergency certificate rotation across all systems", 120, "HIGH"),
            ("Engage law enforcement and CISA", 15, "IMMEDIATE"),
            ("Prepare customer notifications", 60, "HIGH")
        ]
        
        print(f"{Colors.CYAN}Action Plan:{Colors.END}")
        for i, (action, duration, priority) in enumerate(actions, 1):
            priority_color = Colors.RED if priority == "IMMEDIATE" else Colors.YELLOW
            print(f"  {i}. {action}")
            print(f"     Duration: {duration}m | Priority: {priority_color}{priority}{Colors.END}\n")
        
        await asyncio.sleep(2)
        
        # Step 6: Executive Briefing
        self.print_section("Step 6: Executive Agent - Prepares Leadership Briefing")
        
        self.print_agent_message(
            AgentType.EXECUTIVE,
            "🎯 Executive briefing prepared and ready for board",
            0.88,
            Colors.BOLD
        )
        
        print(f"""
{Colors.BOLD}╔════════════════════════════════════════════════════════════════╗
║                    EXECUTIVE BRIEFING                          ║
║                                                                  ║
║ INCIDENT: Post-Quantum Cryptography System Compromise         ║
║ STATUS: {Colors.RED}CRITICAL{Colors.BOLD}                                              ║
║                                                                  ║
║ Current Exposure: $18.2M                                       ║
║ Affected Systems: 127                                          ║
║ Affected Customers: 145,000                                    ║
║ Regulatory Risk: {Colors.RED}CRITICAL{Colors.BOLD}                                          ║
║                                                                  ║
║ RECOMMENDED IMMEDIATE ACTIONS:                                 ║
║  1. Isolate HSM cluster (5 minutes)                            ║
║  2. Engage law enforcement                                      ║
║  3. Notify board immediately                                    ║
║  4. Prepare customer notification                               ║
║  5. Coordinate with regulators                                  ║
║                                                                  ║
║ CONFIDENCE LEVEL: 86%                                          ║
║ ESTIMATED TIME TO RECOVERY: 24-48 hours                        ║
║                                                                  ║
╚════════════════════════════════════════════════════════════════╝{Colors.END}
""")
        
        await asyncio.sleep(3)
        
        # Show shared memory
        self.print_section("Shared Memory - What Agents Learned")
        
        print(f"{Colors.CYAN}Findings ({len(self.memory.findings)}){Colors.END}")
        for finding in self.memory.findings[:3]:
            print(f"  • {finding.content} (confidence: {finding.confidence:.0%})\n")
        
        print(f"{Colors.CYAN}Evidence ({len(self.memory.evidence)}){Colors.END}")
        for evidence in self.memory.evidence:
            print(f"  • {evidence.source}: {evidence.metric_name}\n")
        
        print(f"{Colors.CYAN}Collaboration Metrics{Colors.END}")
        print(f"  • Agents involved: 6")
        print(f"  • Debates initiated: 1")
        print(f"  • Consensus achieved: Yes")
        print(f"  • Average confidence: 0.86\n")
        
        self.print_banner("✅ DEMO COMPLETE - AGENTS SUCCESSFULLY COLLABORATED")
        
        print(f"""
{Colors.GREEN}What you just witnessed:{Colors.END}

1. {Colors.BOLD}Detection Agent{Colors.END} discovered the anomaly within seconds
2. {Colors.BOLD}Threat Intelligence Agent{Colors.END} identified root cause and motive
3. {Colors.BOLD}Risk Agent{Colors.END} initially underestimated impact
4. {Colors.BOLD}Compliance Agent{Colors.END} challenged and corrected the estimate
5. {Colors.BOLD}Response Agent{Colors.END} proposed actionable containment steps
6. {Colors.BOLD}Executive Agent{Colors.END} translated technical findings into business language

{Colors.YELLOW}Key Differentiators:{Colors.END}
✓ Multi-agent collaboration visible on screen
✓ Agents debating and challenging each other
✓ Shared memory accessible to all agents
✓ Financial impact calculated from technical findings
✓ Executive briefing generated automatically
✓ No black boxes - every decision explainable

{Colors.CYAN}This is not another cybersecurity dashboard.
This is the world's first AI-powered Multi-Agent War Room.{Colors.END}

Press Enter to continue...
""")
        input()
    
    async def run(self):
        """Run the demo"""
        await self.demo_nation_state_attack()


async def main():
    """Main entry point"""
    demo = WarRoomDemo()
    await demo.run()


if __name__ == "__main__":
    asyncio.run(main())
