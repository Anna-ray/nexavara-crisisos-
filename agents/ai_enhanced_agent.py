"""Enhanced agent base class that integrates AI/ML services.

This agent uses the EnhancedAIClient for intelligent analysis and decision-making.
"""

import logging
from typing import Optional, Any, Dict
from abc import abstractmethod

from config import Config
from messages import AgentRequest, AgentResponse
from agents.crisis_base_agent import BaseAgent
from services.enhanced_ai_client import EnhancedAIClient

logger = logging.getLogger(__name__)


class AIEnhancedAgent(BaseAgent):
    """
    Agent that uses AI/ML services for enhanced analysis.
    
    Integrates with EnhancedAIClient to leverage:
    - AI/ML API (GPT-4, etc.)
    - Featherless API (Llama models)
    - Fallback heuristics
    """
    
    def __init__(
        self,
        role: str,
        coordinator: Optional[Any] = None,
        ai_client: Optional[EnhancedAIClient] = None
    ):
        """Initialize enhanced agent with AI/ML client integration."""
        super().__init__(role=role, coordinator=coordinator)
        
        # Initialize or use provided AI client
        if ai_client:
            self.ai_client = ai_client
        else:
            self.ai_client = EnhancedAIClient(
                ai_ml_api_key=Config.AIML_API_KEY,
                featherless_api_key=Config.FEATHERLESS_API_KEY,
                ai_ml_endpoint=Config.AIML_ENDPOINT,
                featherless_endpoint=Config.FEATHERLESS_ENDPOINT
            )
        
        logger.info(f"🤖 {self.role} initialized with AI/ML enhancement")
    
    def get_ai_analysis(
        self,
        description: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get AI-powered analysis for an incident.
        
        Args:
            description: Incident description
            context: Additional context
            
        Returns:
            AI analysis results with severity, root cause, recommendations
        """
        try:
            logger.info(f"🔍 {self.role}: Requesting AI analysis...")
            analysis = self.ai_client.analyze_incident(description, context)
            logger.info(f"✓ {self.role}: AI analysis completed with confidence {analysis.get('confidence_score', 0)}")
            return analysis
        except Exception as e:
            logger.error(f"✗ {self.role}: AI analysis failed: {e}")
            return self._fallback_analysis(description, context)
    
    def _fallback_analysis(
        self,
        description: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Fallback heuristic analysis when AI services unavailable.
        
        Args:
            description: Incident description
            context: Additional context
            
        Returns:
            Basic heuristic analysis
        """
        logger.warning(f"⚠ {self.role}: Using fallback heuristic analysis")
        
        # Heuristic scoring based on keywords and context
        severity = 3
        confidence = 0.6  # Baseline fallback confidence
        
        high_severity_keywords = ["critical", "breach", "ransomware", "outage", "hack", "exploit"]
        if any(keyword in description.lower() for keyword in high_severity_keywords):
            severity = min(5, severity + 2)
            confidence = min(0.95, confidence + 0.3)  # Boost confidence for high-severity keywords
        
        if context:
            context_severity = context.get("severity", 0)
            if context_severity > 7:
                severity = 4
                confidence = min(0.95, confidence + 0.25)  # Boost for high input severity
            elif context_severity >= 5:
                confidence = min(0.90, confidence + 0.15)
        
        return {
            "severity_level": f"Level {severity}",
            "root_cause": "Analysis in progress - see detailed incident assessment",
            "financial_exposure_per_minute": 50000.0,
            "affected_systems": ["network", "infrastructure"],
            "recommended_actions": [
                "Activate crisis response team",
                "Begin incident containment",
                "Notify stakeholders"
            ],
            "confidence_score": confidence,
            "ai_source": "heuristic_fallback"
        }
    
    @abstractmethod
    def analyze(self, request: AgentRequest) -> AgentResponse:
        """Analyze request using AI/ML services. Must be implemented by subclasses."""
        raise NotImplementedError
