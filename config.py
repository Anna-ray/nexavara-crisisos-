"""
Production configuration for NEXAVARA Crisis Operating System.

Centralizes all environment variables, API endpoints, and production settings
with comprehensive validation and defaults.
"""
import os
from typing import Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class Environment(str, Enum):
    """Deployment environment."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class Config:
    """Production configuration manager."""
    
    # Environment
    ENVIRONMENT = Environment(os.getenv("ENVIRONMENT", Environment.DEVELOPMENT.value))
    DEBUG = ENVIRONMENT == Environment.DEVELOPMENT
    
    # AI/ML API Configuration
    AIML_API_KEY = os.getenv("AI_ML_API_KEY", "")
    AIML_ENDPOINT = os.getenv(
        "AI_ML_ENDPOINT",
        "https://api.aimlapi.com/v1/chat/completions"
    )
    AIML_MODEL = os.getenv("AIML_MODEL", "gpt-4o-mini")
    AIML_TIMEOUT = int(os.getenv("AIML_TIMEOUT", "30"))
    
    # Featherless API Configuration
    FEATHERLESS_API_KEY = os.getenv("FEATHERLESS_API_KEY", "")
    FEATHERLESS_ENDPOINT = os.getenv(
        "FEATHERLESS_ENDPOINT",
        "https://api.featherless.ai/v1/chat/completions"
    )
    FEATHERLESS_MODEL = os.getenv("FEATHERLESS_MODEL", "meta-llama/Meta-Llama-3.1-8B-Instruct")
    FEATHERLESS_TIMEOUT = int(os.getenv("FEATHERLESS_TIMEOUT", "30"))
    
    # Crisis Coordinator Configuration
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "2"))
    COORDINATOR_TIMEOUT = int(os.getenv("COORDINATOR_TIMEOUT", "30"))
    ENABLE_AUDIT_TRAIL = os.getenv("ENABLE_AUDIT_TRAIL", "true").lower() == "true"
    
    # Database Configuration (for audit trail)
    DB_ENABLED = os.getenv("DB_ENABLED", "false").lower() == "true"
    DB_URL = os.getenv("DB_URL", "sqlite:///nexavara_audit.db")
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE = os.getenv("LOG_FILE", "nexavara.log")
    
    # API Configuration
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    API_WORKERS = int(os.getenv("API_WORKERS", "4"))
    API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))
    
    # Crisis Response Configuration
    INCIDENT_ESCALATION_THRESHOLD = float(os.getenv("INCIDENT_ESCALATION_THRESHOLD", "7.0"))
    AUTO_ESCALATE_ON_CRITICAL = os.getenv("AUTO_ESCALATE_ON_CRITICAL", "true").lower() == "true"
    
    # Security Configuration
    ENABLE_ENCRYPTION = os.getenv("ENABLE_ENCRYPTION", "true").lower() == "true"
    ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "")
    
    @classmethod
    def validate(cls) -> bool:
        """Validate critical configuration."""
        required_in_prod = []
        
        if cls.ENVIRONMENT == Environment.PRODUCTION:
            required_in_prod = [
                ("AIML_API_KEY", cls.AIML_API_KEY),
                ("FEATHERLESS_API_KEY", cls.FEATHERLESS_API_KEY),
                ("ENABLE_AUDIT_TRAIL", cls.ENABLE_AUDIT_TRAIL),
            ]
        
        missing = [key for key, val in required_in_prod if not val]
        
        if missing:
            logger.error(f"❌ Missing required production configs: {', '.join(missing)}")
            return False
        
        logger.info(f"✓ Configuration validated for {cls.ENVIRONMENT.value}")
        return True
    
    @classmethod
    def log_startup(cls):
        """Log startup configuration."""
        logger.info("=" * 60)
        logger.info("🚀 NEXAVARA Crisis Operating System")
        logger.info("=" * 60)
        logger.info(f"Environment: {cls.ENVIRONMENT.value}")
        logger.info(f"Debug Mode: {cls.DEBUG}")
        logger.info(f"AI/ML API: {'✓' if cls.AIML_API_KEY else '✗'}")
        logger.info(f"Featherless API: {'✓' if cls.FEATHERLESS_API_KEY else '✗'}")
        logger.info(f"Audit Trail: {'✓' if cls.ENABLE_AUDIT_TRAIL else '✗'}")
        logger.info(f"Database: {'✓' if cls.DB_ENABLED else '✗'}")
        logger.info(f"Log Level: {cls.LOG_LEVEL}")
        logger.info("=" * 60)


def setup_logging():
    """Configure structured logging."""
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL),
        format=Config.LOG_FORMAT,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(Config.LOG_FILE)
        ]
    )
    
    # Suppress verbose libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)
