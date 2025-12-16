#!/bin/bash
# Generate secure secrets for production deployment

echo "Generating secure secrets for production..."
echo ""
echo "# Add these to your .env file:"
echo ""
echo "JWT_SECRET_KEY=\"$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))' 2>/dev/null || openssl rand -base64 32)\""
echo ""
echo "MONGO_ROOT_PASSWORD=\"$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))' 2>/dev/null || openssl rand -base64 32)\""
echo ""
echo "Done! Copy the values above to your .env file."

