from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings."""
    
    # Azure AI Settings
    AZURE_AI_ENDPOINT: str
    AZURE_AI_KEY: Optional[str] = None
    MODEL_DEPLOYMENT_NAME: str = "gpt-4"
    
    # Agent Settings
    ORCHESTRATOR_AGENT_NAME: str = "ORCHESTRATOR_AGENT"
    VERIFICATION_AGENT_NAME: str = "VERIFICATION_AGENT"
    REPORT_AGENT_NAME: str = "REPORT_GENERATION_AGENT"
    
    # Logging Settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()