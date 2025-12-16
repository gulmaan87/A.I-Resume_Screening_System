"""Test if .env file can be loaded by pydantic-settings."""
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class TestSettings(BaseSettings):
    database_url: str = Field(..., env="DB_URI")
    aws_access_key_id: str = Field(..., env="AWS_ACCESS_KEY")
    
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

try:
    settings = TestSettings()
    print("SUCCESS: Settings loaded!")
    print(f"DB_URI: {settings.database_url}")
    print(f"AWS_ACCESS_KEY: {settings.aws_access_key_id}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()










