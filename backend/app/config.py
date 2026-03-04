from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Neo4j Configuration
    neo4j_uri: str = Field("bolt://localhost:7687", alias="NEO4J_URI")
    neo4j_user: str = Field("neo4j", alias="NEO4J_USER")
    neo4j_password: str = Field("expertlink123", alias="NEO4J_PASSWORD")
    
    # Security Configuration
    secret_key: str = Field("your-super-secret-key", alias="SECRET_KEY")
    algorithm: str = Field("HS256", alias="ALGORITHM")
    access_token_expire_minutes: int = Field(30, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    app_name: str = Field("Nexora", alias="APP_NAME")
    debug: bool = Field(False, alias="DEBUG")
    
    # Email Configuration
    SMTP_HOST: str = Field("smtp.gmail.com", alias="SMTP_HOST")
    SMTP_PORT: int = Field(587, alias="SMTP_PORT")
    SMTP_USER: str = Field("", alias="SMTP_USER")
    SMTP_PASSWORD: str = Field("", alias="SMTP_PASSWORD")
    FROM_EMAIL: str = Field("", alias="FROM_EMAIL")
    FRONTEND_URL: str = Field("http://localhost:3000", alias="FRONTEND_URL")
    VERIFICATION_TOKEN_EXPIRE_HOURS: int = Field(24, alias="VERIFICATION_TOKEN_EXPIRE_HOURS")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()


settings = get_settings()
