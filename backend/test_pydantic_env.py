"""Test pydantic-settings with .env file."""
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# Create a simple test .env file
test_env = Path(__file__).parent / ".env"
print(f"Reading .env from: {test_env.absolute()}")

class TestSettings(BaseSettings):
    database_url: str = Field(..., env="DB_URI")
    aws_access_key: str = Field(..., env="AWS_ACCESS_KEY")
    
    model_config = SettingsConfigDict(
        env_file=str(test_env),
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

# Try to load settings
try:
    settings = TestSettings()
    print(f"SUCCESS! database_url={settings.database_url[:50]}...")
    print(f"SUCCESS! aws_access_key={settings.aws_access_key}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
    # Try with debug
    import os
    from dotenv import load_dotenv
    load_dotenv(test_env)
    print(f"\nDirect dotenv load:")
    print(f"DB_URI={os.getenv('DB_URI', 'NOT FOUND')}")
    print(f"AWS_ACCESS_KEY={os.getenv('AWS_ACCESS_KEY', 'NOT FOUND')}")












