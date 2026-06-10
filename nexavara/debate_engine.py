"""
NEXAVARA CrisisOS - Agent Debate Engine

The system that enables agents to challenge each other, debate positions,
and reach consensus through evidence-based argumentation.

This is the KILLER FEATURE: Agents don't blindly agree. They debate.
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime
import uuid

from .core_models import (
    DirectorAgentType,
    AgentDebate,
    AgentPosition,
    DebateChallenge,
    DebateStatus,
    CrisisContext,
    Evidence,
    AgentTrustMetrics,
)
from .crisis_council import BaseDirectorAgent


# ============================================================================
# DEBATE ENGINE
# ============================================================================

class DebateEngine:
    """
    The Agent Debate Engine
    
    Manages debates between agents, tracks positions, and facilitates
    consensus-building through evidence-based argumentation.
    """
    
    def __init__(self):
        self.active_debates: Dict[str, AgentDebate] = {}
        self.debate_history: List[AgentDebate] = []
        
        # Debate triggers
        self.confidence_delta_threshold = 0.15  # 15% difference triggers debate
        self.cost_disagreement_threshold = 1_000_000  # $1M difference
    
    def should_initiate_debate(
        self,
        position1: AgentPosition,
        position2: AgentPosition,
        context: CrisisContext
    ) -> Tuple[bool, str]:
        """
        Determine if a debate should be initiated between two positions
        
        Returns:
            (should_debate, reason)
        """
        
        # Check confidence delta
        confidence_delta = abs(position1.confidence - position2.confidence)
        if confidence_delta > self.confidence_delta_threshold:
            return True, f"Confidence delta: {confidence_delta:.0%} (threshold: {self.confidence_delta_threshold:.0%})"
        
        # Check for explicit disagreement in positions
        disagreement_keywords = [
            ("immediate", "delay"),
            ("contain", "monitor"),
            ("approve", "reject"),
            ("critical", "moderate"),
            ("high", "low"),
        ]
        
        pos1_lower = position1.position.lower()
        pos2_lower = position2.position.lower()
        
        for keyword1, keyword2 in disagreement_keywords:
            if (keyword1 in pos1_lower and keyword2 in pos2_lower) or \
               (keyword2 in pos1_lower and keyword1 in pos2_lower):
                return True, f"Conflicting positions: '{keyword1}' vs '{keyword2}'"
        
        # Check for cost/benefit disagreement
        if "cost" in pos1_lower and "cost" in pos2_lower:
            # Simplified check - in real implementation, parse actual numbers
            if ("exceed" in pos1_lower and "justify" in pos2_lower) or \
               ("justify" in pos1_lower and "exceed" in pos2_lower):
                return True, "Cost-benefit disagreement detected"
        
        return False, ""
    
    def initiate_debate(
        self,
        topic: str,
        initiating_agent: DirectorAgentType,
        challenged_agent: DirectorAgentType,
        challenge_reason: str,
        incident_id: str,
        evidence: Optional[List[Evidence]] = None
    ) -> AgentDebate:
        """
        Initiate a debate between two agents
        """
        
        challenge = DebateChallenge(
            challenging_agent=initiating_agent,
            challenged_agent=challenged_agent,
            challenge_reason=challenge_reason,
            evidence=evidence or [],
        )
        
        debate = AgentDebate(
            topic=topic,
            incident_id=incident_id,
            initiating_agent=initiating_agent,
            challenged_agent=challenged_agent,
            participating_agents=[initiating_agent, challenged_agent],
            challenge=challenge,
            status=DebateStatus.INITIATED,
        )
        
        self.active_debates[debate.debate_id] = debate
        
        return debate
    
    def add_position(
        self,
        debate_id: str,
        position: AgentPosition
    ) -> AgentDebate:
        """
        Add an agent's position to a debate
        """
        
        if debate_id not in self.active_debates:
            raise ValueError(f"Debate {debate_id} not found")
        
        debate = self.active_debates[debate_id]
        debate.positions.append(position)
        
        # Add agent to participants if not already there
        if position.agent not in debate.participating_agents:
            debate.participating_agents.append(position.agent)
        
        debate.status = DebateStatus.IN_PROGRESS
        
        return debate
    
    def check_consensus(
        self,
        debate_id: str,
        trust_metrics: Dict[DirectorAgentType, AgentTrustMetrics]
    ) -> Tuple[bool, float, Optional[str]]:
        """
        Check if consensus has been reached in a debate
        
        Returns:
            (consensus_reached, confidence, resolution)
        """
        
        if debate_id not in self.active_debates:
            raise ValueError(f"Debate {debate_id} not found")
        
        debate = self.active_debates[debate_id]
        
        if len(debate.positions) < 2:
            return False, 0.0, None
        
        # Calculate trust-weighted consensus
        weighted_sum = 0.0
        total_weight = 0.0
        position_groups: Dict[str, List[AgentPosition]] = {}
        
        for position in debate.positions:
            # Group similar positions
            key = self._normalize_position(position.position)
            if key not in position_groups:
                position_groups[key] = []
            position_groups[key].append(position)
            
            # Calculate weighted confidence
            trust = trust_metrics.get(position.agent)
            if trust:
                weight = position.confidence * trust.overall_trust_score
                weighted_sum += weight
                total_weight += trust.overall_trust_score
        
        # Check if one position dominates
        if position_groups:
            max_group = max(position_groups.values(), key=len)
            if len(max_group) >= len(debate.participating_agents) * 0.7:  # 70% agreement
                consensus_confidence = weighted_sum / total_weight if total_weight > 0 else 0.0
                resolution = max_group[0].position
                return True, consensus_confidence, resolution
        
        # Check if confidence has converged
        confidences = [p.confidence for p in debate.positions]
        if len(confidences) >= 2:
            confidence_range = max(confidences) - min(confidences)
            if confidence_range < 0.10:  # Within 10%
                consensus_confidence = sum(confidences) / len(confidences)
                # Use the position with highest trust-weighted confidence
                best_position = max(
                    debate.positions,
                    key=lambda p: p.confidence * trust_metrics.get(p.agent, AgentTrustMetrics(agent=p.agent)).overall_trust_score
                )
                return True, consensus_confidence, best_position.position
        
        return False, 0.0, None
    
    def resolve_debate(
        self,
        debate_id: str,
        resolution: str,
        consensus_confidence: float
    ) -> AgentDebate:
        """
        Resolve a debate with a final decision
        """
        
        if debate_id not in self.active_debates:
            raise ValueError(f"Debate {debate_id} not found")
        
        debate = self.active_debates[debate_id]
        debate.status = DebateStatus.RESOLVED
        debate.consensus_reached = True
        debate.consensus_confidence = consensus_confidence
        debate.resolution = resolution
        debate.resolved_at = datetime.utcnow()
        
        # Move to history
        self.debate_history.append(debate)
        del self.active_debates[debate_id]
        
        return debate
    
    def escalate_debate(self, debate_id: str) -> AgentDebate:
        """
        Escalate a debate that cannot reach consensus
        """
        
        if debate_id not in self.active_debates:
            raise ValueError(f"Debate {debate_id} not found")
        
        debate = self.active_debates[debate_id]
        debate.status = DebateStatus.ESCALATED
        debate.resolved_at = datetime.utcnow()
        
        # Move to history
        self.debate_history.append(debate)
        del self.active_debates[debate_id]
        
        return debate
    
    def _normalize_position(self, position: str) -> str:
        """
        Normalize a position string for comparison
        """
        # Simple normalization - in production, use NLP
        normalized = position.lower().strip()
        
        # Group similar positions
        if any(word in normalized for word in ["immediate", "now", "urgent"]):
            return "immediate_action"
        elif any(word in normalized for word in ["delay", "wait", "defer"]):
            return "delayed_action"
        elif any(word in normalized for word in ["approve", "support", "agree"]):
            return "approval"
        elif any(word in normalized for word in ["reject", "oppose", "disagree"]):
            return "rejection"
        else:
            return "neutral"
    
    def get_debate_summary(self, debate_id: str) -> str:
        """
        Get a human-readable summary of a debate
        """
        
        debate = self.active_debates.get(debate_id)
        if not debate:
            # Check history
            debate = next((d for d in self.debate_history if d.debate_id == debate_id), None)
            if not debate:
                return f"Debate {debate_id} not found"
        
        summary = f"""
DEBATE: {debate.topic}
Status: {debate.status.value}
Participants: {len(debate.participating_agents)} agents

Challenge:
  From: {debate.challenge.challenging_agent.value}
  To: {debate.challenge.challenged_agent.value}
  Reason: {debate.challenge.challenge_reason}

Positions:
"""
        
        for i, position in enumerate(debate.positions, 1):
            summary += f"""
  {i}. {position.agent.value} (Confidence: {position.confidence:.0%})
     Position: {position.position}
     Reasoning: {position.reasoning}
"""
        
        if debate.consensus_reached:
            summary += f"""
CONSENSUS REACHED: {debate.consensus_confidence:.0%}
Resolution: {debate.resolution}
"""
        
        return summary
    
    def get_active_debates_count(self) -> int:
        """Get count of active debates"""
        return len(self.active_debates)
    
    def get_debate_history_count(self) -> int:
        """Get count of historical debates"""
        return len(self.debate_history)


# ============================================================================
# DEBATE ORCHESTRATOR
# ============================================================================

class DebateOrchestrator:
    """
    Orchestrates debates between agents in the crisis council
    """
    
    def __init__(
        self,
        debate_engine: DebateEngine,
        agents: Dict[DirectorAgentType, BaseDirectorAgent]
    ):
        self.debate_engine = debate_engine
        self.agents = agents
    
    def facilitate_debate(
        self,
        topic: str,
        context: CrisisContext,
        initial_positions: List[AgentPosition]
    ) -> AgentDebate:
        """
        Facilitate a debate on a topic with initial positions
        """
        
        if len(initial_positions) < 2:
            raise ValueError("Need at least 2 positions to start a debate")
        
        # Check if debate should be initiated
        should_debate, reason = self.debate_engine.should_initiate_debate(
            initial_positions[0],
            initial_positions[1],
            context
        )
        
        if not should_debate:
            # No debate needed - positions are aligned
            return None
        
        # Initiate debate
        debate = self.debate_engine.initiate_debate(
            topic=topic,
            initiating_agent=initial_positions[0].agent,
            challenged_agent=initial_positions[1].agent,
            challenge_reason=reason,
            incident_id=context.incident_id,
        )
        
        # Add initial positions
        for position in initial_positions:
            self.debate_engine.add_position(debate.debate_id, position)
        
        # Invite other agents to weigh in
        for agent_type, agent in self.agents.items():
            if agent_type not in [p.agent for p in initial_positions]:
                # Agent forms position on the debate topic
                position = agent.form_position(topic, context)
                self.debate_engine.add_position(debate.debate_id, position)
        
        # Check for consensus
        trust_metrics = {
            agent_type: agent.trust_metrics
            for agent_type, agent in self.agents.items()
        }
        
        consensus_reached, confidence, resolution = self.debate_engine.check_consensus(
            debate.debate_id,
            trust_metrics
        )
        
        if consensus_reached:
            self.debate_engine.resolve_debate(
                debate.debate_id,
                resolution,
                confidence
            )
        
        return debate
    
    def run_debate_round(
        self,
        debate_id: str,
        context: CrisisContext
    ) -> bool:
        """
        Run one round of debate (agents can revise positions)
        
        Returns:
            True if consensus reached, False otherwise
        """
        
        debate = self.debate_engine.active_debates.get(debate_id)
        if not debate:
            return False
        
        # Allow agents to revise positions based on other agents' arguments
        for agent_type in debate.participating_agents:
            agent = self.agents.get(agent_type)
            if agent:
                # Agent considers other positions and may revise
                revised_position = agent.form_position(debate.topic, context)
                self.debate_engine.add_position(debate_id, revised_position)
        
        # Check for consensus
        trust_metrics = {
            agent_type: agent.trust_metrics
            for agent_type, agent in self.agents.items()
        }
        
        consensus_reached, confidence, resolution = self.debate_engine.check_consensus(
            debate_id,
            trust_metrics
        )
        
        if consensus_reached:
            self.debate_engine.resolve_debate(
                debate_id,
                resolution,
                confidence
            )
            return True
        
        return False


# ============================================================================
# DEBATE VISUALIZER
# ============================================================================

class DebateVisualizer:
    """
    Generates visual representations of debates for the UI
    """
    
    @staticmethod
    def format_debate_for_display(debate: AgentDebate) -> Dict[str, any]:
        """
        Format a debate for display in the UI
        """
        
        return {
            "debate_id": debate.debate_id,
            "topic": debate.topic,
            "status": debate.status.value,
            "participants": [agent.value for agent in debate.participating_agents],
            "challenge": {
                "from": debate.challenge.challenging_agent.value,
                "to": debate.challenge.challenged_agent.value,
                "reason": debate.challenge.challenge_reason,
            },
            "positions": [
                {
                    "agent": pos.agent.value,
                    "position": pos.position,
                    "reasoning": pos.reasoning,
                    "confidence": pos.confidence,
                    "timestamp": pos.timestamp.isoformat(),
                }
                for pos in debate.positions
            ],
            "consensus": {
                "reached": debate.consensus_reached,
                "confidence": debate.consensus_confidence,
                "resolution": debate.resolution,
            } if debate.consensus_reached else None,
            "started_at": debate.started_at.isoformat(),
            "resolved_at": debate.resolved_at.isoformat() if debate.resolved_at else None,
        }
    
    @staticmethod
    def generate_debate_timeline(debate: AgentDebate) -> List[Dict[str, any]]:
        """
        Generate a timeline of debate events
        """
        
        timeline = []
        
        # Challenge initiated
        timeline.append({
            "timestamp": debate.started_at.isoformat(),
            "event": "debate_initiated",
            "agent": debate.challenge.challenging_agent.value,
            "description": f"Challenged {debate.challenge.challenged_agent.value}: {debate.challenge.challenge_reason}",
        })
        
        # Positions added
        for position in debate.positions:
            timeline.append({
                "timestamp": position.timestamp.isoformat(),
                "event": "position_stated",
                "agent": position.agent.value,
                "description": position.position,
                "confidence": position.confidence,
            })
        
        # Resolution
        if debate.consensus_reached:
            timeline.append({
                "timestamp": debate.resolved_at.isoformat() if debate.resolved_at else datetime.utcnow().isoformat(),
                "event": "consensus_reached",
                "description": debate.resolution,
                "confidence": debate.consensus_confidence,
            })
        
        return timeline
    
    @staticmethod
    def generate_debate_feed(debates: List[AgentDebate]) -> str:
        """
        Generate a live feed of debate activity (for CLI/terminal display)
        """
        
        feed = "═" * 60 + "\n"
        feed += "AGENT DEBATES - LIVE FEED\n"
        feed += "═" * 60 + "\n\n"
        
        for debate in debates:
            feed += f"[{debate.started_at.strftime('%H:%M:%S')}] {debate.topic}\n"
            feed += f"Status: {debate.status.value.upper()}\n"
            feed += f"Participants: {', '.join(a.value for a in debate.participating_agents)}\n"
            feed += "\n"
            
            for position in debate.positions:
                timestamp = position.timestamp.strftime('%H:%M:%S')
                agent_name = position.agent.value.replace('_', ' ').title()
                
                # Check if this is a challenge
                is_challenge = position.agent == debate.challenge.challenging_agent and \
                              len([p for p in debate.positions if p.timestamp <= position.timestamp]) == 1
                
                if is_challenge:
                    feed += f"[{timestamp}] {agent_name} [CHALLENGES]\n"
                else:
                    feed += f"[{timestamp}] {agent_name}\n"
                
                feed += f'"{position.position}"\n'
                feed += f"Confidence: {position.confidence:.0%}\n\n"
            
            if debate.consensus_reached:
                timestamp = debate.resolved_at.strftime('%H:%M:%S') if debate.resolved_at else "PENDING"
                feed += f"[{timestamp}] CONSENSUS REACHED: {debate.resolution}\n"
                feed += f"Council Confidence: {debate.consensus_confidence:.0%}\n"
            
            feed += "─" * 60 + "\n\n"
        
        return feed


# ============================================================================
# EXAMPLE DEBATE SCENARIOS
# ============================================================================

def create_example_debate_scenario() -> Dict[str, any]:
    """
    Create an example debate scenario for demonstration
    """
    
    return {
        "scenario_name": "Containment Cost vs Risk Exposure",
        "topic": "Should we implement immediate containment?",
        "initial_positions": [
            {
                "agent": "threat_director",
                "position": "Recommend immediate containment. Attack vector is active.",
                "confidence": 0.95,
                "reasoning": "Security-first approach: contain now, investigate later",
            },
            {
                "agent": "finance_director",
                "position": "Containment cost ($500K) exceeds current projected loss ($200K)",
                "confidence": 0.89,
                "reasoning": "Cost-benefit analysis suggests delayed action",
            },
        ],
        "expected_challenge": {
            "from": "compliance_director",
            "to": "finance_director",
            "reason": "Regulatory requirements mandate immediate action. Potential fines exceed containment cost.",
        },
        "expected_outcome": {
            "consensus": True,
            "resolution": "Immediate containment approved",
            "confidence": 0.92,
        }
    }

# Made with Bob
