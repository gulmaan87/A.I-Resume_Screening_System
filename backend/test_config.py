"""Test script to check if .env file is being read correctly."""
from pathlib import Path
from app.config import Settings

# Check if .env file exists
env_path = Path(__file__).parent / ".env"
print(f"Looking for .env at: {env_path.absolute()}")
print(f".env file exists: {env_path.exists()}")

if env_path.exists():
    print(f"\n.env file contents (first 500 chars):")
    with open(env_path, 'r') as f:
        content = f.read()
        # Mask sensitive values
        lines = content.split('\n')
        for line in lines[:20]:  # Show first 20 lines
            if '=' in line:
                key, value = line.split('=', 1)
                if 'SECRET' in key.upper() or 'KEY' in key.upper() or 'PASSWORD' in key.upper():
                    print(f"{key}=***MASKED***")
                else:
                    print(line)
            else:
                print(line)

print("\n" + "="*50)
print("Attempting to load Settings...")
try:
    settings = Settings()
    print("✅ Settings loaded successfully!")
    print(f"DB_URI: {settings.database_url[:50]}..." if len(settings.database_url) > 50 else f"DB_URI: {settings.database_url}")
    print(f"DB_NAME: {settings.mongo_db_name}")
    print(f"S3_BUCKET: {settings.s3_bucket_name}")
except Exception as e:
    print(f"❌ Error loading Settings: {e}")










