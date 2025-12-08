# Kubernetes Deployment Script for Resume Screening Application (PowerShell)
# Usage: .\deploy.ps1 [namespace]

param(
    [string]$Namespace = "resume-screening"
)

Write-Host "🚀 Deploying Resume Screening Application to Kubernetes..." -ForegroundColor Cyan
Write-Host "📦 Namespace: $Namespace" -ForegroundColor Cyan

# Check if kubectl is available
try {
    $null = kubectl version --client 2>&1
} catch {
    Write-Host "❌ kubectl is not installed. Please install kubectl first." -ForegroundColor Red
    exit 1
}

# Check if cluster is accessible
try {
    $null = kubectl cluster-info 2>&1
} catch {
    Write-Host "❌ Cannot connect to Kubernetes cluster. Please check your kubeconfig." -ForegroundColor Red
    exit 1
}

Write-Host "✅ Kubernetes cluster is accessible" -ForegroundColor Green

# Create namespace
Write-Host "📝 Creating namespace..." -ForegroundColor Yellow
kubectl apply -f namespace.yaml

# Create secrets check
Write-Host "🔐 Checking secrets..." -ForegroundColor Yellow
$secretExists = kubectl get secret resume-screening-secrets -n $Namespace 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Secret 'resume-screening-secrets' not found. Please create it first:" -ForegroundColor Yellow
    Write-Host "   kubectl apply -f secrets.yaml" -ForegroundColor Yellow
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne "y" -and $continue -ne "Y") {
        exit 1
    }
} else {
    Write-Host "✅ Secrets found" -ForegroundColor Green
}

# Create ConfigMap
Write-Host "📋 Creating ConfigMap..." -ForegroundColor Yellow
kubectl apply -f configmap.yaml

# Deploy MongoDB
Write-Host "🍃 Deploying MongoDB..." -ForegroundColor Yellow
kubectl apply -f mongodb-statefulset.yaml
kubectl apply -f mongodb-service.yaml

# Wait for MongoDB
Write-Host "⏳ Waiting for MongoDB to be ready..." -ForegroundColor Yellow
kubectl wait --for=condition=ready pod -l app=mongodb -n $Namespace --timeout=300s 2>&1 | Out-Null

# Deploy Backend
Write-Host "🔧 Deploying Backend..." -ForegroundColor Yellow
kubectl apply -f backend-deployment.yaml
kubectl apply -f backend-service.yaml

# Deploy Frontend
Write-Host "🎨 Deploying Frontend..." -ForegroundColor Yellow
kubectl apply -f frontend-deployment.yaml
kubectl apply -f frontend-service.yaml

# Deploy Ingress (optional)
if (Test-Path ingress.yaml) {
    Write-Host "🌐 Deploying Ingress..." -ForegroundColor Yellow
    $deployIngress = Read-Host "Deploy Ingress? (y/n)"
    if ($deployIngress -eq "y" -or $deployIngress -eq "Y") {
        kubectl apply -f ingress.yaml
    }
}

# Show status
Write-Host ""
Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Current status:" -ForegroundColor Cyan
kubectl get all -n $Namespace

Write-Host ""
Write-Host "🔍 To check logs:" -ForegroundColor Cyan
Write-Host "   kubectl logs -f deployment/backend -n $Namespace"
Write-Host "   kubectl logs -f deployment/frontend -n $Namespace"
Write-Host "   kubectl logs -f statefulset/mongodb -n $Namespace"
Write-Host ""
Write-Host "🌐 To access via port-forward:" -ForegroundColor Cyan
Write-Host "   kubectl port-forward svc/frontend-service 4173:4173 -n $Namespace"
Write-Host "   kubectl port-forward svc/backend-service 8000:8000 -n $Namespace"


