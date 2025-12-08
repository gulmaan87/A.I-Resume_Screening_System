from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import Field, HttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load configuration from the first env file that exists
# Check backend directory first, then project root
_ENV_CANDIDATES = [
    Path(__file__).parent.parent / ".env",  # backend/.env
    Path(__file__).parent.parent.parent / ".env",  # project root .env
    Path(__file__).parent.parent / ".env.local",  # backend/.env.local
    Path(__file__).parent.parent.parent / ".env.local",  # project root .env.local
    Path(__file__).parent.parent.parent / "env.example",  # project root env.example
]
_active_env_path: Path | None = None
for candidate in _ENV_CANDIDATES:
    if candidate.exists():
        load_dotenv(candidate, override=True)
        _active_env_path = candidate
        break


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    app_name: str = Field("AI-Powered Resume Screening", env="APP_NAME")
    api_prefix: str = Field("/api", env="API_PREFIX")
    environment: str = Field("development", env="ENVIRONMENT")

    database_url: str = Field("mongodb+srv://gulmanm8787_db_user:JOzuPNHZiLLXfkJV@cluster1.jczm3i1.mongodb.net/?retryWrites=true&w=majority&appName=Cluster1", env="DB_URI")
    mongo_db_name: str = Field("Resume_Screening", env="DB_NAME")

    aws_access_key_id: str = Field("local-dev-access-key", env="AWS_ACCESS_KEY")
    aws_secret_access_key: str = Field("local-dev-secret-key", env="AWS_SECRET_KEY")
    aws_region: str = Field("us-east-1", env="AWS_REGION")
    s3_bucket_name: str = Field("local-resume-bucket", env="S3_BUCKET_NAME")
    s3_endpoint_url: Optional[HttpUrl] = Field(None, env="S3_ENDPOINT_URL")

    resume_max_size_mb: int = Field(10, env="RESUME_MAX_SIZE_MB")

    spacy_model: str = Field("en_core_web_sm", env="SPACY_MODEL")
    embedding_model: str = Field(
        "sentence-transformers/all-MiniLM-L6-v2", env="EMBEDDING_MODEL_NAME"
    )

    allowed_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:4173", "http://localhost:5173"],
        env="ALLOWED_ORIGINS",
    )

    # JWT Authentication
    jwt_secret_key: str = Field(
        "your-secret-key-change-in-production",
        env="JWT_SECRET_KEY",
        description="Secret key for JWT token signing. MUST be changed in production!",
    )
    jwt_algorithm: str = Field("HS256", env="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(30, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    jwt_refresh_token_expire_days: int = Field(7, env="JWT_REFRESH_TOKEN_EXPIRE_DAYS")

    model_config = SettingsConfigDict(
        # Don't use env_file here since we load it manually with dotenv
        # This ensures the env parameter in Field() works correctly
        case_sensitive=False,
        extra="ignore",
        env_ignore_empty=True,
    )

    @field_validator("allowed_origins", mode="before")
    def split_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @field_validator("mongo_db_name", "database_url", mode="before")
    def strip_quotes(cls, v):
        if isinstance(v, str) and ((v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'"))):
            return v[1:-1]
        return v

    def __init__(self, **values):
        super().__init__(**values)
        # Print for debugging
        print(f"[DEBUG] DB_URI: {self.database_url}\n[DEBUG] DB_NAME: {self.mongo_db_name}")

    @property
    def resume_max_size_bytes(self) -> int:
        return self.resume_max_size_mb * 1024 * 1024
    
    def validate_production(self) -> list[str]:
        """
        Validate that required production settings are configured.
        Returns a list of validation errors (empty if valid).
        """
        errors = []
        
        if self.environment.lower() == "production":
            # Check for default/dev credentials
            if self.aws_access_key_id in ["local-dev-access-key", "your-aws-access-key", ""]:
                errors.append("AWS_ACCESS_KEY must be set in production")
            
            if self.aws_secret_access_key in ["local-dev-secret-key", "your-aws-secret-key", ""]:
                errors.append("AWS_SECRET_KEY must be set in production")
            
            if self.s3_bucket_name in ["local-resume-bucket", "your-resume-bucket", ""]:
                errors.append("S3_BUCKET_NAME must be set in production")
            
            # Check for localhost database in production
            if "localhost" in self.database_url or "127.0.0.1" in self.database_url:
                errors.append("Database URL should not use localhost in production")
            
            # Check CORS origins
            if "localhost" in str(self.allowed_origins):
                errors.append("CORS origins should not include localhost in production")
            
            if len(self.allowed_origins) == 0:
                errors.append("ALLOWED_ORIGINS must be configured in production")
            
            # Check JWT secret key
            if self.jwt_secret_key in ["your-secret-key-change-in-production", "secret", ""]:
                errors.append("JWT_SECRET_KEY must be set to a secure random string in production")
        
        return errors


# Don't cache settings to ensure .env is always loaded fresh
def get_settings() -> Settings:
    # Ensure env file is loaded (in case it wasn't loaded during module import)
    if _active_env_path and _active_env_path.exists():
        load_dotenv(_active_env_path, override=True)
    
    # Create settings instance
    settings = Settings()
    
    # Debug: Log which env file was loaded and the DB_URI being used
    import os
    db_uri_from_env = os.getenv("DB_URI", "NOT_SET")
    if _active_env_path:
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(
            f"Loaded env from: {_active_env_path}, DB_URI from env: {db_uri_from_env[:50]}...",
            extra={"request_id": "config"}
        )
    
    return settings

