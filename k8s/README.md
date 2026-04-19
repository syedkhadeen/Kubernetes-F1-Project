# Kubernetes Deployment Guide

This folder contains Kubernetes manifests to deploy RaceMetrics on any Kubernetes cluster.

## 📋 Prerequisites

- Kubernetes cluster (Minikube, EKS, GKE, AKS, or any K8s cluster)
- kubectl configured to access your cluster
- Docker (for building images)

## 🔒 Security Setup (IMPORTANT)

**Before deploying, you MUST update the secrets:**

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Generate a strong JWT secret:
   ```bash
   openssl rand -hex 32
   ```

3. Update `configmap-secret.yaml` with your generated secret:
   ```yaml
   stringData:
     JWT_SECRET: "YOUR_GENERATED_SECRET_HERE"
   ```

## 🚀 Deployment Steps

### Option 1: Minikube (Local Development)

1. **Start Minikube and enable ingress:**
   ```bash
   minikube start --driver=hyperv  # or docker, virtualbox, etc.
   minikube addons enable ingress
   ```

2. **Build and load images into Minikube:**
   ```powershell
   # Windows PowerShell
   .\k8s\build_and_load_images.ps1
   ```
   
   Or manually:
   ```bash
   # Set Docker to use Minikube's Docker daemon
   eval $(minikube docker-env)
   
   # Build all images
   docker build -t racemetrics/auth-service:latest ./auth-service
   docker build -t racemetrics/api-fetch-service:latest ./api-fetch-service
   docker build -t racemetrics/scraper-service:latest ./scraper-service
   docker build -t racemetrics/data-cleaner-service:latest ./data-cleaner-service
   docker build -t racemetrics/driver-service:latest ./driver-service
   docker build -t racemetrics/constructor-service:latest ./constructor-service
   docker build -t racemetrics/race-service:latest ./race-service
   docker build -t racemetrics/stats-service:latest ./stats-service
   docker build -t racemetrics/frontend-service:latest ./frontend-service
   ```

3. **Apply Kubernetes manifests:**
   ```bash
   kubectl apply -f k8s/namespace.yaml
   kubectl apply -f k8s/configmap-secret.yaml
   kubectl apply -f k8s/mongo-statefulset.yaml
   kubectl apply -f k8s/redis-deployment.yaml
   kubectl apply -f k8s/backend-deployments.yaml
   kubectl apply -f k8s/backend-services.yaml
   kubectl apply -f k8s/frontend-deployment.yaml
   kubectl apply -f k8s/ingress.yaml
   ```

4. **Add host entry:**
   - **Windows**: Edit `C:\Windows\System32\drivers\etc\hosts` (as Administrator)
   - **Linux/Mac**: Edit `/etc/hosts` (with sudo)
   
   Add:
   ```
   127.0.0.1 racemetrics.local
   ```

5. **Access the application:**
   ```
   http://racemetrics.local
   ```

### Option 2: Cloud Kubernetes (Production)

1. **Build and push images to container registry:**
   ```bash
   # Tag images for your registry
   docker tag racemetrics/auth-service:latest your-registry/racemetrics/auth-service:latest
   
   # Push to registry
   docker push your-registry/racemetrics/auth-service:latest
   # Repeat for all services...
   ```

2. **Update image references in manifests:**
   Edit `backend-deployments.yaml` and `frontend-deployment.yaml` to use your registry:
   ```yaml
   image: your-registry/racemetrics/auth-service:latest
   ```

3. **Update ingress configuration:**
   Edit `ingress.yaml` to use your domain:
   ```yaml
   spec:
     rules:
     - host: racemetrics.yourdomain.com
   ```

4. **Apply manifests:**
   ```bash
   kubectl apply -f k8s/
   ```

5. **Configure DNS:**
   Point your domain to the ingress load balancer IP

## 📦 Manifest Files

- `namespace.yaml` - Creates the racemetrics namespace
- `configmap-secret.yaml` - Configuration and secrets (UPDATE BEFORE DEPLOYING!)
- `mongo-statefulset.yaml` - MongoDB StatefulSet with persistent storage
- `redis-deployment.yaml` - Redis cache deployment
- `backend-deployments.yaml` - All backend microservices
- `backend-services.yaml` - Services for backend microservices
- `frontend-deployment.yaml` - React frontend deployment
- `ingress.yaml` - Ingress rules for routing

## 🔍 Verification

Check deployment status:
```bash
# Check all pods
kubectl get pods -n racemetrics

# Check services
kubectl get svc -n racemetrics

# Check ingress
kubectl get ingress -n racemetrics

# View logs
kubectl logs -f deployment/auth-service -n racemetrics
```

## 🛠️ Troubleshooting

### Pods not starting
```bash
kubectl describe pod <pod-name> -n racemetrics
kubectl logs <pod-name> -n racemetrics
```

### Ingress not working
```bash
# Check ingress controller
kubectl get pods -n ingress-nginx

# For Minikube
minikube addons enable ingress
```

### Database connection issues
```bash
# Check MongoDB pod
kubectl logs -f statefulset/mongo -n racemetrics

# Test connection from a pod
kubectl exec -it deployment/auth-service -n racemetrics -- sh
# Inside pod: ping mongo
```

## 📊 Scaling

Scale individual services:
```bash
kubectl scale deployment auth-service --replicas=3 -n racemetrics
kubectl scale deployment driver-service --replicas=2 -n racemetrics
```

## 🔄 Updates

Update a service:
```bash
# Build new image
docker build -t racemetrics/auth-service:v2 ./auth-service

# Update deployment
kubectl set image deployment/auth-service auth-service=racemetrics/auth-service:v2 -n racemetrics

# Or apply updated manifest
kubectl apply -f k8s/backend-deployments.yaml
```

## 🗑️ Cleanup

Remove all resources:
```bash
kubectl delete namespace racemetrics
```

## 📝 Notes

- Images use `imagePullPolicy: IfNotPresent` for local development
- For production, use specific version tags instead of `latest`
- MongoDB uses a PersistentVolumeClaim for data persistence
- Update resource limits based on your cluster capacity
- Consider using Helm charts for easier management in production

## 🔐 Production Checklist

- [ ] Update JWT_SECRET in configmap-secret.yaml
- [ ] Use container registry for images
- [ ] Configure TLS/HTTPS for ingress
- [ ] Set up MongoDB authentication
- [ ] Configure resource limits and requests
- [ ] Enable network policies
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy for MongoDB
- [ ] Use specific image tags (not :latest)
- [ ] Review and harden security settings
