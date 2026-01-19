"""
Robust MongoDB connection handler with DNS fallback and retry logic.
"""
import asyncio
import logging
import socket
from typing import Optional, Tuple
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError, ConfigurationError

logger = logging.getLogger(__name__)


def resolve_hostname_with_fallback(hostname: str, timeout: int = 5) -> Optional[str]:
    """
    Resolve hostname using system DNS.
    
    Note: This function currently uses system DNS only. To use custom DNS servers,
    the dnspython library would be required. The MongoDB driver will handle DNS
    resolution during connection, so this is primarily for diagnostic purposes.
    
    Returns the IP address if successful, None otherwise.
    """
    # Try system DNS
    try:
        ip = socket.gethostbyname(hostname)
        logger.debug(f"Resolved {hostname} to {ip} using system DNS")
        return ip
    except socket.gaierror as e:
        logger.debug(f"DNS resolution failed for {hostname}: {e}")
        return None


def enhance_mongodb_uri(uri: str) -> str:
    """
    Enhance MongoDB URI with better connection options for DNS issues.
    """
    parsed = urlparse(uri)
    query_params = parse_qs(parsed.query)
    
    # Add connection options that help with DNS/network issues
    enhanced_params = {
        "serverSelectionTimeoutMS": "15000",  # 15 seconds
        "connectTimeoutMS": "15000",
        "socketTimeoutMS": "30000",  # 30 seconds for operations
        "retryWrites": "true",
        "retryReads": "true",
        "maxPoolSize": "10",
        "minPoolSize": "1",
        "maxIdleTimeMS": "45000",
        "heartbeatFrequencyMS": "10000",
        "directConnection": "false",  # Use SRV records properly
    }
    
    # Merge with existing params (don't override user settings)
    for key, value in enhanced_params.items():
        if key not in query_params:
            query_params[key] = [value]
    
    # Rebuild URI
    new_query = urlencode(query_params, doseq=True)
    enhanced_uri = urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        new_query,
        parsed.fragment
    ))
    
    return enhanced_uri


async def create_mongodb_client(
    database_url: str,
    max_retries: int = 3,
    retry_delay: int = 3,
    use_dns_fallback: bool = True
) -> Tuple[Optional[AsyncIOMotorClient], bool]:
    """
    Create MongoDB client with robust error handling and DNS fallback.
    
    Returns:
        Tuple of (client, success_flag)
    """
    enhanced_uri = enhance_mongodb_uri(database_url)
    
    # Extract hostname for DNS resolution
    parsed = urlparse(database_url)
    hostname = parsed.hostname
    
    # Try DNS resolution first if using SRV (mongodb+srv://)
    if use_dns_fallback and hostname and "mongodb+srv" in database_url:
        logger.info(f"Attempting DNS resolution for {hostname}...")
        ip = resolve_hostname_with_fallback(hostname, timeout=5)
        if ip:
            logger.info(f"✅ DNS resolution successful: {hostname} -> {ip}")
        else:
            logger.warning(f"⚠️  DNS resolution failed for {hostname}, will try connection anyway")
    
    # Try to connect with retries
    last_error = None
    for attempt in range(max_retries):
        try:
            logger.info(
                f"MongoDB connection attempt {attempt + 1}/{max_retries}...",
                extra={"request_id": "startup"}
            )
            
            client = AsyncIOMotorClient(enhanced_uri)
            
            # Test connection with timeout
            await asyncio.wait_for(
                client.admin.command("ping"),
                timeout=15.0
            )
            
            logger.info(
                "✅ MongoDB connection established successfully",
                extra={"request_id": "startup"}
            )
            return client, True
            
        except asyncio.TimeoutError:
            last_error = "Connection timeout"
            logger.warning(
                f"Connection attempt {attempt + 1} timed out",
                extra={"request_id": "startup"}
            )
        except ServerSelectionTimeoutError as e:
            last_error = f"Server selection timeout: {str(e)}"
            logger.warning(
                f"Server selection failed on attempt {attempt + 1}: {e}",
                extra={"request_id": "startup"}
            )
        except ConfigurationError as e:
            last_error = f"Configuration error: {str(e)}"
            logger.error(
                f"Invalid MongoDB configuration: {e}",
                extra={"request_id": "startup"}
            )
            # Don't retry on configuration errors
            break
        except Exception as e:
            last_error = f"Unexpected error: {type(e).__name__}: {str(e)}"
            logger.warning(
                f"Connection attempt {attempt + 1} failed: {e}",
                extra={"request_id": "startup"},
                exc_info=True
            )
        
        # Wait before retry (except on last attempt)
        if attempt < max_retries - 1:
            logger.info(
                f"Retrying in {retry_delay} seconds...",
                extra={"request_id": "startup"}
            )
            await asyncio.sleep(retry_delay)
        else:
            # Close client if it was created
            try:
                if 'client' in locals():
                    client.close()
            except:
                pass
    
    logger.error(
        f"❌ Failed to connect to MongoDB after {max_retries} attempts",
        extra={"request_id": "startup"}
    )
    logger.error(
        f"Last error: {last_error}",
        extra={"request_id": "startup"}
    )
    
    return None, False


def get_fallback_local_uri() -> str:
    """Get fallback local MongoDB URI."""
    return "mongodb://localhost:27017/?serverSelectionTimeoutMS=5000"


async def connect_with_fallback(
    primary_uri: str,
    fallback_uri: Optional[str] = None,
    db_name: str = "Resume_Screening"
) -> Tuple[Optional[AsyncIOMotorClient], Optional[str], bool]:
    """
    Connect to MongoDB with automatic fallback to local instance.
    
    Returns:
        Tuple of (client, database_name, success_flag)
    """
    # Try primary connection (MongoDB Atlas)
    logger.info("Attempting primary MongoDB connection (Atlas)...")
    client, success = await create_mongodb_client(primary_uri)
    
    if success:
        return client, db_name, True
    
    # Try fallback to local MongoDB
    fallback = fallback_uri or get_fallback_local_uri()
    logger.warning("Primary connection failed, attempting fallback to local MongoDB...")
    logger.info(f"Fallback URI: {fallback}")
    
    client, success = await create_mongodb_client(
        fallback,
        max_retries=2,
        retry_delay=1,
        use_dns_fallback=False
    )
    
    if success:
        logger.info("✅ Connected to local MongoDB fallback")
        return client, db_name, True
    
    logger.error("❌ All MongoDB connection attempts failed")
    return None, None, False









