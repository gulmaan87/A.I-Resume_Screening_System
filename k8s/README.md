# Kubernetes Deployment Guide

This directory contains Kubernetes manifests for deploying the Resume Screening application to a Kubernetes cluster.

## Prerequisites

1. **Kubernetes Cluster**: A running Kubernetes cluster (v1.24+)
2. **kubectl**: Kubernetes command-line tool configured to access your cluster
3. **Docker Images**: Backend and frontend images pushed to a container registry
4. **Storage Class**: A storage class configured for PersistentVolumes (for MongoDB)

## Directory Structure

```
k8s/
├── namespace.yaml              # Namespace definition
├── configmap.yaml              # Non-sensitive configuration
├── secrets.yaml                # Sensitive data (passwords, API keys)
├── mongodb-statefulset.yaml    # MongoDB StatefulSet with PVC
├── mongodb-service.yaml        # MongoDB service (ClusterIP)
├── backend-deployment.yaml     # Backend API deployment
├── backend-service.yaml        # Backend service
├── frontend-deployment.yaml    # Frontend deployment
├── frontend-service.yaml       # Frontend service
├── ingress.yaml                # Ingress for external access
├── kustomization.yaml          # Kustomize configuration
└── README.md                   # This file
```

## Setup Steps

### 1. Build and Push Docker Images

First, build and push your Docker images to a container registry:

```bash
# Build backend image
docker build -t your-registry/resume-backend:latest ./backend

# Build frontend image with API URL (IMPORTANT: VITE_API_BASE_URL is a build-time variable)
# Option A: Use the backend service URL (for Kubernetes internal communication)
docker build --build-arg VITE_API_BASE_URL=http://backend-service.resume-screening.svc.cluster.local:8000 \
  -t your-registry/resume-frontend:latest ./frontend

# Option B: Use external URL (if accessing via Ingress)
docker build --build-arg VITE_API_BASE_URL=https://resume-screening.yourdomain.com/api \
  -t your-registry/resume-frontend:latest ./frontend

# Push to registry
docker push your-registry/resume-backend:latest
docker push your-registry/resume-frontend:latest
```

**Note**: `VITE_API_BASE_URL` is a build-time environment variable for Vite. It must be set during the Docker build process, not at runtime. Choose the appropriate URL based on how your frontend will access the backend (internal service or external Ingress).

### 2. Update Image References

Edit the deployment files to use your image registry:

- `backend-deployment.yaml`: Update `image` field
- `frontend-deployment.yaml`: Update `image` field

### 3. Configure Secrets

**IMPORTANT**: Update `secrets.yaml` with your actual secrets. All values must be base64 encoded.

```bash
# Encode secrets
echo -n 'your-password' | base64
echo -n 'mongodb+srv://...' | base64
```

Or create secrets directly:

```bash
kubectl create secret generic resume-screening-secrets \
  --from-literal=mongo-root-username=admin \
  --from-literal=mongo-root-password=YourSecurePassword \
  --from-literal=db-uri='mongodb+srv://...' \
  --from-literal=aws-access-key=YourAccessKey \
  --from-literal=aws-secret-key=YourSecretKey \
  --from-literal=jwt-secret-key=YourJWTSecret \
  -n resume-screening
```

### 4. Update ConfigMap

Edit `configmap.yaml` to match your environment:
- Update `ALLOWED_ORIGINS` with your domain
- Update `VITE_API_BASE_URL` if needed

### 5. Configure Storage

Update `mongodb-statefulset.yaml` to use your storage class:

```yaml
storageClassName: standard  # Change to match your cluster
```

### 6. Configure Ingress (Optional)

If using Ingress, update `ingress.yaml`:
- Replace `resume-screening.yourdomain.com` with your domain
- Update `ingressClassName` if not using NGINX
- Configure TLS certificates (cert-manager or manual)

### 7. Deploy to Kubernetes

**Option A: Using Kustomize (Recommended)**

```bash
kubectl apply -k k8s/
```

**Option B: Deploy Individual Resources**

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Create secrets and configmap
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/configmap.yaml

# Deploy MongoDB
kubectl apply -f k8s/mongodb-statefulset.yaml
kubectl apply -f k8s/mongodb-service.yaml

# Deploy Backend
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/backend-service.yaml

# Deploy Frontend
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/frontend-service.yaml

# Deploy Ingress (optional)
kubectl apply -f k8s/ingress.yaml
```

## Verification

Check the status of your deployments:

```bash
# Check all resources
kubectl get all -n resume-screening

# Check pods
kubectl get pods -n resume-screening

# Check services
kubectl get svc -n resume-screening

# Check logs
kubectl logs -f deployment/backend -n resume-screening
kubectl logs -f deployment/frontend -n resume-screening
kubectl logs -f statefulset/mongodb -n resume-screening
```

## Scaling

Scale your deployments:

```bash
# Scale backend
kubectl scale deployment backend --replicas=3 -n resume-screening

# Scale frontend
kubectl scale deployment frontend --replicas=3 -n resume-screening
```

## Accessing the Application

### Using Port Forwarding (Development)

```bash
# Forward frontend
kubectl port-forward svc/frontend-service 4173:4173 -n resume-screening

# Forward backend
kubectl port-forward svc/backend-service 8000:8000 -n resume-screening
```

### Using LoadBalancer/NodePort

Change service type in:
- `backend-service.yaml`: `type: LoadBalancer` or `type: NodePort`
- `frontend-service.yaml`: `type: LoadBalancer` or `type: NodePort`

### Using Ingress

If Ingress is configured, access via:
- Frontend: `https://resume-screening.yourdomain.com`
- Backend API: `https://resume-screening.yourdomain.com/api`

## Updating the Application

### Update Images

```bash
# Set new image
kubectl set image deployment/backend backend=your-registry/resume-backend:v1.1.0 -n resume-screening
kubectl set image deployment/frontend frontend=your-registry/resume-frontend:v1.1.0 -n resume-screening

# Or update the YAML and reapply
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
```

### Rolling Restart

```bash
kubectl rollout restart deployment/backend -n resume-screening
kubectl rollout restart deployment/frontend -n resume-screening
```

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl describe pod <pod-name> -n resume-screening

# Check events
kubectl get events -n resume-screening --sort-by='.lastTimestamp'
```

### MongoDB Connection Issues

```bash
# Check MongoDB logs
kubectl logs statefulset/mongodb -n resume-screening

# Test connection from backend pod
kubectl exec -it deployment/backend -n resume-screening -- curl http://mongodb-service:27017
```

### Image Pull Errors

Ensure:
1. Images are pushed to registry
2. Image pull secrets are configured (if using private registry)
3. Image names are correct in deployment files

## Cleanup

To remove all resources:

```bash
# Using Kustomize
kubectl delete -k k8s/

# Or manually
kubectl delete namespace resume-screening
```

**Warning**: This will delete all data including MongoDB persistent volumes!

## Production Considerations

1. **Secrets Management**: Use external secret management (e.g., HashiCorp Vault, AWS Secrets Manager)
2. **Resource Limits**: Adjust CPU/memory limits based on your workload
3. **High Availability**: Consider MongoDB replica set for production
4. **Backup**: Set up regular backups for MongoDB data
5. **Monitoring**: Add monitoring and logging (Prometheus, Grafana, ELK)
6. **Security**: Enable network policies, use RBAC, scan images for vulnerabilities
7. **TLS**: Configure proper TLS certificates for Ingress
8. **CORS**: Update CORS settings in ConfigMap and Ingress annotations

## Additional Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [MongoDB on Kubernetes](https://www.mongodb.com/docs/kubernetes-operator/)
- [NGINX Ingress Controller](https://kubernetes.github.io/ingress-nginx/)

