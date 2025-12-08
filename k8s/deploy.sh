#!/bin/bash

# Kubernetes Deployment Script for Resume Screening Application
# Usage: ./deploy.sh [namespace]

set -e

NAMESPACE=${1:-resume-screening}

echo "🚀 Deploying Resume Screening Application to Kubernetes..."
echo "📦 Namespace: $NAMESPACE"

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed. Please install kubectl first."
    exit 1
fi

# Check if cluster is accessible
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Cannot connect to Kubernetes cluster. Please check your kubeconfig."
    exit 1
fi

echo "✅ Kubernetes cluster is accessible"

# Create namespace
echo "📝 Creating namespace..."
kubectl apply -f namespace.yaml

# Wait for namespace to be ready
kubectl wait --for=condition=Active namespace/$NAMESPACE --timeout=30s || true

# Create secrets (if not exists)
echo "🔐 Checking secrets..."
if ! kubectl get secret resume-screening-secrets -n $NAMESPACE &> /dev/null; then
    echo "⚠️  Secret 'resume-screening-secrets' not found. Please create it first:"
    echo "   kubectl apply -f secrets.yaml"
    echo "   Or create manually with: kubectl create secret generic resume-screening-secrets ..."
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ Secrets found"
fi

# Create ConfigMap
echo "📋 Creating ConfigMap..."
kubectl apply -f configmap.yaml

# Deploy MongoDB
echo "🍃 Deploying MongoDB..."
kubectl apply -f mongodb-statefulset.yaml
kubectl apply -f mongodb-service.yaml

# Wait for MongoDB to be ready
echo "⏳ Waiting for MongoDB to be ready..."
kubectl wait --for=condition=ready pod -l app=mongodb -n $NAMESPACE --timeout=300s || echo "⚠️  MongoDB may still be starting"

# Deploy Backend
echo "🔧 Deploying Backend..."
kubectl apply -f backend-deployment.yaml
kubectl apply -f backend-service.yaml

# Deploy Frontend
echo "🎨 Deploying Frontend..."
kubectl apply -f frontend-deployment.yaml
kubectl apply -f frontend-service.yaml

# Deploy Ingress (optional)
if [ -f ingress.yaml ]; then
    echo "🌐 Deploying Ingress..."
    read -p "Deploy Ingress? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kubectl apply -f ingress.yaml
    fi
fi

# Show status
echo ""
echo "✅ Deployment complete!"
echo ""
echo "📊 Current status:"
kubectl get all -n $NAMESPACE

echo ""
echo "🔍 To check logs:"
echo "   kubectl logs -f deployment/backend -n $NAMESPACE"
echo "   kubectl logs -f deployment/frontend -n $NAMESPACE"
echo "   kubectl logs -f statefulset/mongodb -n $NAMESPACE"
echo ""
echo "🌐 To access via port-forward:"
echo "   kubectl port-forward svc/frontend-service 4173:4173 -n $NAMESPACE"
echo "   kubectl port-forward svc/backend-service 8000:8000 -n $NAMESPACE"

