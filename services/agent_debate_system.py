"""
Agent Debate System - Enables visible agent disagreement and resolution
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import json
from enum import Enum

from services.war_room_models import (
    Debate, AgentMessage, AgentType, DecisionStatus, Finding,
    Evidence, MemoryGraph
)


class DebateResolutionStrategy(str, Enum):
    CONFIDENCE_WEIGHTED = "confidence_weighted"
    EVIDENCE_BASED = "evidence_based"
    CONSENSUS_SEEKING = "consensus_seeking"
    ESCALATE_TO_HUMAN = "escalate_to_human"


class AgentDebateSystem:
    """
    Manages visible debates between agents.
    
    Key principle: Agents must challenge each other when confidence differs significantly.
    """
    
    def __init__(self, memory_graph: MemoryGraph):
        self.memory_graph = memory_graph
        self.debates: List[Debate] = []
        self.disagreement_threshold = 0.30  # If difference > 30%, debate is required
    
    def initiate_debate(
        self,
        topic: str,
        initiating_agent: AgentType,
        challenged_agent: AgentType,
        challenge_reason: str,
        initiating_agent_position: str,
        initiating_agent_confidence: float
    ) -> Debate:
        """Initiate a debate between two agents"""
        
        debate = Debate(
            initiated_by=initiating_agent,
            challenged_agent=challenged_agent,
            topic=topic,
            initial_position=initiating_agent_position,
            challenge_reason=challenge_reason,
            status=DecisionStatus.DEBATED
        )
        
        # Add initial message from initiating agent
        initial_message = AgentMessage(
            agent_type=initiating_agent,
            content=f"I challenge: {challenge_reason}",
            message_type="challenge",
            confidence=initiating_agent_confidence,
            targets_agent=challenged_agent
        )
        
        debate.messages.append(initial_message)
        self.debates.append(debate)
        self.memory_graph.debates.append(debate)
        
        return debate
    
    def add_debate_response(
        self,
        debate_id: str,
        responding_agent: AgentType,
        response_content: str,
        confidence: float,
        concedes: bool = False
    ) -> Optional[Debate]:
        """Add a response to an active debate"""
        
        debate = next((d for d in self.debates if d.id == debate_id), None)
        if not debate:
            return None
        
        message = AgentMessage(
            agent_type=responding_agent,
            content=response_content,
            message_type="challenge" if not concedes else "acknowledgment",
            confidence=confidence,
            targets_agent=debate.initiated_by
        )
        
        debate.messages.append(message)
        
        # If agent concedes, calculate new consensus
        if concedes:
            self._resolve_debate(debate, "consensus_achieved")
        
        return debate
    
    def check_for_conflicts(
        self,
        finding1: Finding,
        finding2: Finding
    ) -> Optional[Debate]:
        """
        Check if two findings from different agents conflict.
        Return a debate if significant disagreement exists.
        """
        
        # Calculate confidence difference
        confidence_diff = abs(finding1.confidence - finding2.confidence)
        
        # If severity differs and confidence difference is significant
        if (finding1.severity != finding2.severity and 
            confidence_diff > self.disagreement_threshold):
            
            # Initiate debate
            debate = self.initiate_debate(
                topic=f"Incident severity assessment",
                initiating_agent=finding1.agent_type,
                challenged_agent=finding2.agent_type,
                challenge_reason=f"Severity disagreement: {finding1.severity} vs {finding2.severity}",
                initiating_agent_position=str(finding1.severity),
                initiating_agent_confidence=finding1.confidence
            )
            
            return debate
        
        return None
    
    def resolve_debate_with_evidence(
        self,
        debate_id: str,
        new_evidence: List[Evidence]
    ) -> Debate:
        """
        Resolve a debate by presenting additional evidence.
        Agents should acknowledge and update their positions.
        """
        
        debate = next((d for d in self.debates if d.id == debate_id), None)
        if not debate:
            raise ValueError(f"Debate {debate_id} not found")
        
        # Add evidence to memory
        for evidence in new_evidence:
            self.memory_graph.evidence.append(evidence)
        
        # Create evidence discussion message
        evidence_summary = self._summarize_evidence(new_evidence)
        message = AgentMessage(
            agent_type=AgentType.THREAT_INTELLIGENCE,  # Using as neutral analyzer
            content=f"New evidence found: {evidence_summary}",
            message_type="analysis",
            confidence=0.85
        )
        
        debate.messages.append(message)
        
        return debate
    
    def auto_resolve_debate(self, debate_id: str) -> Optional[str]:
        """
        Automatically resolve a debate based on strategy.
        Returns the resolution.
        """
        
        debate = next((d for d in self.debates if d.id == debate_id), None)
        if not debate:
            return None
        
        # Calculate consensus
        confidences = [msg.confidence for msg in debate.messages]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        confidence_variance = self._calculate_variance(confidences)
        
        if confidence_variance > 0.15:
            # High disagreement - needs human review
            resolution = "escalate_to_human"
        else:
            # Low disagreement - consensus achieved
            resolution = "consensus_achieved"
        
        self._resolve_debate(debate, resolution)
        
        return resolution
    
    def _resolve_debate(self, debate: Debate, resolution: str):
        """Mark debate as resolved"""
        if resolution == "consensus_achieved":
            debate.status = DecisionStatus.CONSENSUS
            debate.resolution = "Agents reached consensus on position"
        elif resolution == "escalate_to_human":
            debate.status = DecisionStatus.HUMAN_REVIEW
            debate.resolution = "High disagreement - requires human review"
        else:
            debate.resolution = resolution
    
    def get_debate_timeline(self, debate_id: str) -> List[Dict[str, Any]]:
        """Get chronological timeline of a debate"""
        
        debate = next((d for d in self.debates if d.id == debate_id), None)
        if not debate:
            return []
        
        timeline = []
        for msg in debate.messages:
            timeline.append({
                "timestamp": msg.timestamp.isoformat(),
                "agent": msg.agent_type.value,
                "message": msg.content,
                "confidence": msg.confidence,
                "type": msg.message_type
            })
        
        return timeline
    
    def get_debate_summary(self, debate_id: str) -> Dict[str, Any]:
        """Get a summary of a debate"""
        
        debate = next((d for d in self.debates if d.id == debate_id), None)
        if not debate:
            return {}
        
        return {
            "id": debate.id,
            "topic": debate.topic,
            "initiated_by": debate.initiated_by.value,
            "challenged_agent": debate.challenged_agent.value if debate.challenged_agent else None,
            "initial_position": debate.initial_position,
            "status": debate.status.value,
            "resolution": debate.resolution,
            "message_count": len(debate.messages),
            "agents_involved": list(set(msg.agent_type.value for msg in debate.messages)),
            "disagreement_level": debate.disagreement_level,
            "timeline": self.get_debate_timeline(debate_id)
        }
    
    def get_active_debates_count(self) -> int:
        """Get count of unresolved debates"""
        return sum(1 for d in self.debates if d.status == DecisionStatus.DEBATED)
    
    def get_consensus_level(self) -> float:
        """
        Get overall consensus level across all debates.
        0.0 = total disagreement, 1.0 = perfect consensus
        """
        
        if not self.debates:
            return 1.0
        
        # Calculate average disagreement
        total_disagreement = sum(d.disagreement_level for d in self.debates)
        avg_disagreement = total_disagreement / len(self.debates)
        
        # Invert to get consensus
        return 1.0 - avg_disagreement
    
    # ========================================================================
    # PRIVATE METHODS
    # ========================================================================
    
    def _summarize_evidence(self, evidence_list: List[Evidence]) -> str:
        """Create a summary of evidence"""
        if not evidence_list:
            return "No evidence provided"
        
        summary_parts = []
        for e in evidence_list:
            summary_parts.append(f"{e.metric_name}: {e.value} (severity: {e.severity.value})")
        
        return "; ".join(summary_parts)
    
    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of a list of values"""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5  # Return standard deviation


class DebateExplainer:
    """Explains debate outcomes to humans"""
    
    @staticmethod
    def explain_debate(debate: Debate) -> str:
        """Generate human-readable explanation of a debate"""
        
        explanation = f"""
DEBATE ANALYSIS: {debate.topic}

Topic: {debate.topic}
Initiated by: {debate.initiated_by.value.replace('_', ' ').title()}
Challenged Agent: {debate.challenged_agent.value.replace('_', ' ').title() if debate.challenged_agent else 'None'}

Initial Position: {debate.initial_position}
Challenge Reason: {debate.challenge_reason}

Status: {debate.status.value}
Resolution: {debate.resolution}

Debate Timeline:
"""
        
        for i, msg in enumerate(debate.messages, 1):
            explanation += f"\n  {i}. {msg.agent_type.value.replace('_', ' ').title()} (confidence: {msg.confidence:.1%})"
            explanation += f"\n     {msg.content}\n"
        
        return explanation
    
    @staticmethod
    def explain_why_debate_matters(debate: Debate) -> str:
        """Explain why this debate is important for the incident"""
        
        return f"""
This debate matters because:

1. The {debate.challenged_agent.value.replace('_', ' ').title()} and {debate.initiated_by.value.replace('_', ' ').title()}
   have different assessments of the situation.

2. A {debate.disagreement_level:.0%} disagreement level indicates moderate uncertainty.

3. The topic ({debate.topic}) directly affects downstream decisions about:
   - Incident severity
   - Response actions
   - Executive communication
   - Resource allocation

4. Resolution status: {debate.status.value}
   {f"   → Awaiting human review due to high disagreement" if debate.status == DecisionStatus.HUMAN_REVIEW else "   → Consensus achieved"}
"""
