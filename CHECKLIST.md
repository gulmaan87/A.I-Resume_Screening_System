# Pre-Deployment Checklist

Use this checklist before deploying to production.

## Environment Configuration

- [ ] Created `.env` file from `env.example`
- [ ] Set `ENVIRONMENT="production"`
- [ ] Configured `AWS_ACCESS_KEY` with real credentials
- [ ] Configured `AWS_SECRET_KEY` with real credentials
- [ ] Set `S3_BUCKET_NAME` to your production bucket
- [ ] Generated secure `JWT_SECRET_KEY` (use `scripts/generate-secrets.sh` or `.ps1`)
- [ ] Set `VITE_API_BASE_URL` to your production backend URL
- [ ] Configured `ALLOWED_ORIGINS` with your production frontend domain(s)
- [ ] Set `DB_URI` correctly (use container name `mongo` for Docker)
- [ ] If using MongoDB auth: Set `MONGO_ROOT_USERNAME` and `MONGO_ROOT_PASSWORD`

## Security

- [ ] `.env` file is NOT committed to git (check `.gitignore`)
- [ ] JWT secret key is a secure random string (not default)
- [ ] AWS credentials have minimal required permissions
- [ ] CORS origins only include your production domains
- [ ] MongoDB authentication enabled (if using `docker-compose.prod.yml`)
- [ ] MongoDB port not exposed publicly (use `docker-compose.prod.yml`)

## Docker Configuration

- [ ] Docker and Docker Compose are installed
- [ ] All Dockerfiles are present and correct
- [ ] `docker-compose.yml` is configured correctly
- [ ] `docker-compose.prod.yml` is ready (if using production override)

## Testing

- [ ] Tested locally with `docker-compose up --build`
- [ ] Backend health check passes: `curl http://localhost:8000/health`
- [ ] Frontend loads: `curl http://localhost:4173`
- [ ] Frontend can connect to backend API
- [ ] MongoDB connection works
- [ ] File upload functionality works
- [ ] Authentication works (if implemented)

## Production Deployment

- [ ] Server has sufficient resources (CPU, memory, disk)
- [ ] Firewall rules configured (ports 8000, 4173)
- [ ] Domain names configured (if using)
- [ ] SSL/TLS certificates ready (if using HTTPS)
- [ ] Backup strategy for MongoDB data
- [ ] Monitoring and logging configured
- [ ] Error tracking configured (optional)

## Post-Deployment

- [ ] Verify all services are running: `docker-compose ps`
- [ ] Check logs for errors: `docker-compose logs`
- [ ] Test API endpoints
- [ ] Test frontend functionality
- [ ] Monitor resource usage: `docker stats`
- [ ] Set up automated backups
- [ ] Configure log rotation

## Quick Commands

```bash
# Generate secrets
bash scripts/generate-secrets.sh
# or on Windows:
powershell scripts/generate-secrets.ps1

# Start services
docker-compose up -d --build

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Production deployment
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

