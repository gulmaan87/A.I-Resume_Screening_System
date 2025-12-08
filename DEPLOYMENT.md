# Deployment Guide

## Prerequisites

1. Docker and Docker Compose installed
2. AWS credentials (if using S3)
3. Domain name or server IP address (for production)

## Quick Start (Development)

1. Copy environment file:
   ```bash
   cp env.example .env
   ```

2. Update `.env` with your local development values (minimal changes needed for local dev)

3. Start services:
   ```bash
   docker-compose up --build
   ```

4. Access:
   - Frontend: http://localhost:4173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Production Deployment

### Step 1: Create Production Environment File

```bash
cp env.example .env
```

### Step 2: Update `.env` with Production Values

**CRITICAL: Update these values:**

1. **Environment:**
   ```bash
   ENVIRONMENT="production"
   ```

2. **AWS Credentials:**
   ```bash
   AWS_ACCESS_KEY="your-real-aws-access-key"
   AWS_SECRET_KEY="your-real-aws-secret-key"
   S3_BUCKET_NAME="your-production-bucket"
   ```

3. **Frontend API URL:**
   ```bash
   # Use your production backend URL
   VITE_API_BASE_URL="https://api.yourdomain.com"
   # Or if using IP: http://your-server-ip:8000
   ```

4. **CORS Origins:**
   ```bash
   # Set to your production frontend domain(s)
   ALLOWED_ORIGINS="https://app.yourdomain.com,https://www.yourdomain.com"
   ```

5. **JWT Secret Key:**
   ```bash
   # Generate a secure key:
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   # Or: openssl rand -base64 32
   # Then set:
   JWT_SECRET_KEY="your-generated-secure-key-here"
   ```

6. **MongoDB (if using authentication):**
   ```bash
   MONGO_ROOT_USERNAME="admin"
   MONGO_ROOT_PASSWORD="your-secure-mongo-password"
   ```

### Step 3: Deploy

**Option A: Standard Production (with MongoDB auth)**
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

**Option B: Standard Production (without MongoDB auth)**
```bash
docker-compose up -d --build
```

### Step 4: Verify Deployment

1. Check health:
   ```bash
   curl http://localhost:8000/health
   curl http://localhost:4173
   ```

2. Check logs:
   ```bash
   docker-compose logs -f backend
   docker-compose logs -f frontend
   ```

3. Verify services are running:
   ```bash
   docker-compose ps
   ```

## Security Checklist

- [ ] `.env` file is not committed to git
- [ ] `JWT_SECRET_KEY` is a secure random string
- [ ] AWS credentials are valid and have minimal required permissions
- [ ] `ALLOWED_ORIGINS` only includes your production domains
- [ ] MongoDB is not exposed publicly (use docker-compose.prod.yml)
- [ ] `ENVIRONMENT` is set to "production"
- [ ] `VITE_API_BASE_URL` points to your production backend URL

## Troubleshooting

### Frontend can't connect to backend

- Verify `VITE_API_BASE_URL` in `.env` matches your backend URL
- Check browser console for CORS errors
- Verify `ALLOWED_ORIGINS` includes your frontend URL

### MongoDB connection issues

- Check MongoDB container is running: `docker-compose ps mongo`
- Verify `DB_URI` in `.env` matches your setup
- For production with auth, ensure credentials are correct

### Build failures

- Clear Docker cache: `docker-compose build --no-cache`
- Verify all environment variables are set correctly
- Check Docker logs: `docker-compose logs`

## Monitoring

View logs:
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f mongo
```

Check resource usage:
```bash
docker stats
```

## Updates

To update the application:

1. Pull latest code
2. Rebuild containers:
   ```bash
   docker-compose up -d --build
   ```
3. Restart if needed:
   ```bash
   docker-compose restart
   ```

