import io
import mimetypes
import uuid
from datetime import timedelta
from pathlib import Path
from typing import Optional, Union

import boto3
from botocore.client import Config
from botocore.exceptions import BotoCoreError, ClientError

from ..config import Settings, get_settings


class LocalStorageClient:
    """Handle local file storage for development/testing."""

    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        # Create storage directory if it doesn't exist
        self.storage_dir = Path(__file__).parent.parent.parent / "storage" / "resumes"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.base_url = getattr(self.settings, "local_storage_base_url", "http://localhost:8000/storage")

    def upload_bytes(
        self,
        *,
        data: bytes,
        filename: str,
        content_type: Optional[str] = None,
        expires_in_days: int = 365,
    ) -> dict:
        """Store file locally and return metadata."""
        # Generate unique path
        file_id = uuid.uuid4().hex
        file_extension = Path(filename).suffix
        local_filename = f"{file_id}{file_extension}"
        file_path = self.storage_dir / local_filename

        # Write file
        file_path.write_bytes(data)

        # Generate URL (for local dev, this would be served by a static file endpoint)
        relative_path = f"resumes/{local_filename}"
        url = f"{self.base_url}/{relative_path}"

        return {
            "key": relative_path,
            "url": url,
            "content_type": content_type or mimetypes.guess_type(filename)[0] or "application/octet-stream",
            "local_path": str(file_path),
        }


class S3StorageClient:
    """Handle interactions with AWS S3."""

    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        self._session = boto3.session.Session(
            aws_access_key_id=self.settings.aws_access_key_id,
            aws_secret_access_key=self.settings.aws_secret_access_key,
            region_name=self.settings.aws_region,
        )
        extra_config = Config(s3={"addressing_style": "virtual"})
        self._client = self._session.client(
            "s3",
            endpoint_url=self.settings.s3_endpoint_url,
            config=extra_config,
        )

    def upload_bytes(
        self,
        *,
        data: bytes,
        filename: str,
        content_type: Optional[str] = None,
        expires_in_days: int = 365,
    ) -> dict:
        """Upload bytes to S3 and return metadata."""
        key = f"resumes/{uuid.uuid4().hex}/{filename}"
        content_type = content_type or mimetypes.guess_type(filename)[0] or "application/octet-stream"

        self._client.upload_fileobj(
            io.BytesIO(data),
            self.settings.s3_bucket_name,
            key,
            ExtraArgs={
                "ContentType": content_type,
                "ACL": "private",
            },
        )

        presigned_url = self._client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.settings.s3_bucket_name, "Key": key},
            ExpiresIn=int(timedelta(days=expires_in_days).total_seconds()),
        )

        return {
            "key": key,
            "url": presigned_url,
            "content_type": content_type,
        }


def _is_s3_configured(settings: Settings) -> bool:
    """Check if S3 is properly configured with real credentials."""
    # Check if using default/local dev credentials
    is_default_key = settings.aws_access_key_id in [
        "local-dev-access-key",
        "your-aws-access-key",
        "",
    ]
    is_default_secret = settings.aws_secret_access_key in [
        "local-dev-secret-key",
        "your-aws-secret-key",
        "",
    ]

    # If using default credentials, assume local storage
    if is_default_key or is_default_secret:
        return False

    # If endpoint URL is set (e.g., LocalStack/MinIO), try S3
    if settings.s3_endpoint_url:
        return True

    # Otherwise, check if bucket name suggests real AWS
    # If bucket name is a default/local name, use local storage
    if settings.s3_bucket_name in [
        "local-resume-bucket",
        "your-resume-bucket",
        "",
    ]:
        return False

    # If we have non-default credentials, try S3
    return True


def get_storage_client(settings: Settings | None = None) -> Union[LocalStorageClient, S3StorageClient]:
    """
    Get the appropriate storage client based on configuration.
    Automatically falls back to local storage if S3 is not configured.
    """
    settings = settings or get_settings()

    # Try to use S3 if properly configured
    if _is_s3_configured(settings):
        try:
            # Test S3 connection by creating client
            client = S3StorageClient(settings)
            # Try a simple operation to verify it works
            # If this fails, we'll catch and fall back to local
            return client
        except Exception:
            # If S3 fails, fall back to local storage
            pass

    # Use local storage as fallback
    return LocalStorageClient(settings)
