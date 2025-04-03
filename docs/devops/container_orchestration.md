# Bifrost Container Orchestration

This document outlines the container orchestration configuration for deploying Bifrost in production environments.

## Container Architecture

```mermaid
flowchart TD
    %% External Access
    Client[Client Requests] --> Ingress[Ingress Controller]
    
    %% Frontend
    Ingress --> WebUI[Web UI Service]
    WebUI --> WebUIPods[Web UI Pods]
    
    %% API Services
    Ingress --> APIGateway[API Gateway Service]
    APIGateway --> APIPods[API Server Pods]
    
    %% Core Services
    subgraph CoreServices[Core Services]
        AssetService[Asset Service]
        ShotService[Shot Service]
        FolderService[Folder Service]
        WorkflowService[Workflow Service]
        SearchService[Search Service]
    end
    
    APIPods --> CoreServices
    
    %% Background Processing
    APIPods --> Queue[Message Queue]
    Queue --> Workers[Worker Pods]
    Workers --> CoreServices
    
    %% Databases
    CoreServices --> PrimaryDB[(Primary DB)]
    CoreServices --> ReadReplicas[(Read Replicas)]
    CoreServices --> Cache[(Cache)]
    
    %% Storage
    CoreServices --> ObjectStorage[(Object Storage)]
    CoreServices --> FileSystem[(Shared File System)]
    
    classDef client fill:#f9e4b7,stroke:#333,stroke-width:1px
    classDef ingress fill:#b5d3e7,stroke:#333,stroke-width:1px
    classDef service fill:#d5f5e3,stroke:#333,stroke-width:1px
    classDef pods fill:#dff9fb,stroke:#333,stroke-width:1px
    classDef storage fill:#f8c6df,stroke:#333,stroke-width:1px
    classDef queue fill:#d6c1e7,stroke:#333,stroke-width:1px
    
    class Client client
    class Ingress ingress
    class WebUI,APIGateway service
    class WebUIPods,APIPods,Workers,CoreServices pods
    class PrimaryDB,ReadReplicas,Cache,ObjectStorage,FileSystem storage
    class Queue queue
```

## Kubernetes Configuration

### Namespace Setup

```yaml
# bifrost-namespaces.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: bifrost-prod
  labels:
    name: bifrost-prod
    environment: production
---
apiVersion: v1
kind: Namespace
metadata:
  name: bifrost-staging
  labels:
    name: bifrost-staging
    environment: staging
---
apiVersion: v1
kind: ResourceQuota
metadata:
  name: bifrost-quota
  namespace: bifrost-prod
spec:
  hard:
    pods: "50"
    requests.cpu: "20"
    requests.memory: 40Gi
    limits.cpu: "40"
    limits.memory: 80Gi
```

### API Server Deployment

```yaml
# bifrost-api-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: bifrost-api
  namespace: bifrost-prod
  labels:
    app: bifrost
    component: api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: bifrost
      component: api
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    metadata:
      labels:
        app: bifrost
        component: api
    spec:
      containers:
      - name: api
        image: bifrost/api:${VERSION}
        imagePullPolicy: Always
        ports:
        - containerPort: 8000
        resources:
          requests:
            cpu: "500m"
            memory: "1Gi"
          limits:
            cpu: "2"
            memory: "4Gi"
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: bifrost-db-credentials
              key: url
        - name: REDIS_URL
          valueFrom:
            configMapKeyRef:
              name: bifrost-config
              key: redis_url
        - name: S3_BUCKET
          valueFrom:
            configMapKeyRef:
              name: bifrost-config
              key: s3_bucket
        - name: ENVIRONMENT
          value: "production"
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 15
          periodSeconds: 20
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - bifrost
              topologyKey: "kubernetes.io/hostname"
```

### API Service and Ingress

```yaml
# bifrost-api-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: bifrost-api
  namespace: bifrost-prod
  labels:
    app: bifrost
    component: api
spec:
  ports:
  - port: 80
    targetPort: 8000
    protocol: TCP
    name: http
  selector:
    app: bifrost
    component: api
  type: ClusterIP
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: bifrost-api-ingress
  namespace: bifrost-prod
  annotations:
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - api.bifrost.example.com
    secretName: bifrost-api-tls
  rules:
  - host: api.bifrost.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: bifrost-api
            port:
              number: 80
```

### Worker Deployment

```yaml
# bifrost-worker-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: bifrost-worker
  namespace: bifrost-prod
  labels:
    app: bifrost
    component: worker
spec:
  replicas: 3
  selector:
    matchLabels:
      app: bifrost
      component: worker
  template:
    metadata:
      labels:
        app: bifrost
        component: worker
    spec:
      containers:
      - name: worker
        image: bifrost/worker:${VERSION}
        imagePullPolicy: Always
        resources:
          requests:
            cpu: "1"
            memory: "2Gi"
          limits:
            cpu: "4"
            memory: "8Gi"
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: bifrost-db-credentials
              key: url
        - name: REDIS_URL
          valueFrom:
            configMapKeyRef:
              name: bifrost-config
              key: redis_url
        - name: S3_BUCKET
          valueFrom:
            configMapKeyRef:
              name: bifrost-config
              key: s3_bucket
        - name: ENVIRONMENT
          value: "production"
        - name: WORKER_CONCURRENCY
          value: "4"
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
```

### Web UI Deployment

```yaml
# bifrost-web-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: bifrost-web
  namespace: bifrost-prod
  labels:
    app: bifrost
    component: web
spec:
  replicas: 2
  selector:
    matchLabels:
      app: bifrost
      component: web
  template:
    metadata:
      labels:
        app: bifrost
        component: web
    spec:
      containers:
      - name: web
        image: bifrost/web:${VERSION}
        imagePullPolicy: Always
        ports:
        - containerPort: 80
        resources:
          requests:
            cpu: "200m"
            memory: "256Mi"
          limits:
            cpu: "500m"
            memory: "512Mi"
        env:
        - name: API_URL
          value: "https://api.bifrost.example.com"
        - name: ENVIRONMENT
          value: "production"
        readinessProbe:
          httpGet:
            path: /health.html
            port: 80
          initialDelaySeconds: 3
          periodSeconds: 5
```

### Persistent Storage

```yaml
# bifrost-storage.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: bifrost-cache-pvc
  namespace: bifrost-prod
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 100Gi
  storageClassName: managed-nfs-storage
```

### ConfigMaps and Secrets

```yaml
# bifrost-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: bifrost-config
  namespace: bifrost-prod
data:
  redis_url: "redis://bifrost-redis:6379/0"
  s3_bucket: "bifrost-assets-prod"
  log_level: "INFO"
  max_file_size_mb: "5000"
  cache_ttl_seconds: "86400"
  allowed_origins: "https://bifrost.example.com"
---
# Secrets would be created separately using kubectl or a secrets manager
# Example (DO NOT store in version control):
# kubectl create secret generic bifrost-db-credentials \
#   --from-literal=url="postgresql://user:password@db-host:5432/bifrost" \
#   --namespace bifrost-prod
```

### Horizontal Pod Autoscaler

```yaml
# bifrost-hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: bifrost-api-hpa
  namespace: bifrost-prod
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: bifrost-api
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Network Policies

```yaml
# bifrost-network-policies.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: bifrost-api-network-policy
  namespace: bifrost-prod
spec:
  podSelector:
    matchLabels:
      app: bifrost
      component: api
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - ipBlock:
        cidr: 10.0.0.0/8
    - namespaceSelector:
        matchLabels:
          name: bifrost-prod
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: bifrost-prod
    - podSelector:
        matchLabels:
          app: postgres
    - podSelector:
        matchLabels:
          app: redis
    ports:
    - protocol: TCP
```

## Docker Compose for Development

```yaml
# docker-compose.yml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: bifrost
      POSTGRES_PASSWORD: development
      POSTGRES_DB: bifrost
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U bifrost"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  api:
    build:
      context: .
      dockerfile: Dockerfile.api
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    environment:
      - DATABASE_URL=postgresql://bifrost:development@db:5432/bifrost
      - REDIS_URL=redis://redis:6379/0
      - S3_BUCKET=bifrost-dev
      - ENVIRONMENT=development
      - LOG_LEVEL=DEBUG
    ports:
      - "8000:8000"
    volumes:
      - ./:/app
      - ./data:/data
    command: ["python", "-m", "uvicorn", "bifrost.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

  worker:
    build:
      context: .
      dockerfile: Dockerfile.worker
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    environment:
      - DATABASE_URL=postgresql://bifrost:development@db:5432/bifrost
      - REDIS_URL=redis://redis:6379/0
      - S3_BUCKET=bifrost-dev
      - ENVIRONMENT=development
      - LOG_LEVEL=DEBUG
      - WORKER_CONCURRENCY=2
    volumes:
      - ./:/app
      - ./data:/data
    command: ["python", "-m", "bifrost.worker.main"]

  web:
    build:
      context: ./web
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - API_URL=http://localhost:8000
      - ENVIRONMENT=development
    volumes:
      - ./web:/app
      - /app/node_modules
    command: ["npm", "run", "dev"]

volumes:
  postgres_data:
  redis_data:
```

## Dockerfile for API

```dockerfile
# Dockerfile.api
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry==1.4.2

# Copy Poetry configuration
COPY pyproject.toml poetry.lock ./

# Configure Poetry to not use a virtual environment
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-interaction --no-ansi --no-root --only main

# Copy project
COPY . .

# Install project
RUN poetry install --no-interaction --no-ansi

# Create a non-root user
RUN useradd -m -u 1000 bifrost
USER bifrost

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/home/bifrost/.local/bin:$PATH"

# Run the application
CMD ["python", "-m", "uvicorn", "bifrost.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Dockerfile for Worker

```dockerfile
# Dockerfile.worker
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry==1.4.2

# Copy Poetry configuration
COPY pyproject.toml poetry.lock ./

# Configure Poetry to not use a virtual environment
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-interaction --no-ansi --no-root --only main

# Copy project
COPY . .

# Install project
RUN poetry install --no-interaction --no-ansi

# Create a non-root user
RUN useradd -m -u 1000 bifrost
USER bifrost

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/home/bifrost/.local/bin:$PATH"

# Run the worker
CMD ["python", "-m", "bifrost.worker.main"]
```

## Helm Chart Structure

For more complex deployments, a Helm chart is recommended. Here's the basic structure:

```
bifrost-chart/
├── Chart.yaml
├── values.yaml
├── values-staging.yaml
├── values-production.yaml
├── templates/
│   ├── _helpers.tpl
│   ├── configmap.yaml
│   ├── deployment-api.yaml
│   ├── deployment-web.yaml
│   ├── deployment-worker.yaml
│   ├── ingress.yaml
│   ├── NOTES.txt
│   ├── secret.yaml
│   ├── service-api.yaml
│   └── service-web.yaml
└── charts/
    ├── postgresql
    └── redis
```

## Resource Considerations

### Storage Requirements

- **Database**: Start with 50GB, monitor growth, and plan for regular backups
- **Object Storage**: Should scale to multiple TB; use cloud provider options (S3, GCS, etc.)
- **Shared File System**: Required for multi-pod deployments; consider NFS, GlusterFS, or cloud solutions

### Memory and CPU

- **API Servers**: 1-2 CPU cores and 2-4GB RAM per pod
- **Workers**: 1-4 CPU cores and 2-8GB RAM per pod, depending on processing needs
- **Web UI**: 0.5 CPU cores and 0.5-1GB RAM per pod
- **Database**: 2-8 CPU cores and 8-32GB RAM, depending on size of asset library

### Network

- **Internal Communication**: Services within the same namespace should communicate directly
- **External Access**: All external access should go through ingress controllers
- **File Transfer**: S3 pre-signed URLs for large file uploads directly to object storage

## Security Considerations

### Container Security

1. **Image Scanning**:
   - Use tools like Trivy, Clair, or Snyk to scan container images
   - Automate scanning in CI/CD pipeline
   - Block deployments with critical vulnerabilities

2. **Minimal Base Images**:
   - Use slim or distroless images where possible
   - Remove unnecessary tools and packages

3. **Non-root Users**:
   - Run containers as non-root users
   - Use read-only file systems where applicable

### Kubernetes Security

1. **Pod Security Policies**:
   - Enforce non-root container execution
   - Prevent privilege escalation
   - Use seccomp profiles

2. **Network Policies**:
   - Restrict pod-to-pod communication
   - Implement "deny all" default policies
   - Allow only necessary traffic

3. **RBAC**:
   - Use role-based access control
   - Follow principle of least privilege
   - Regularly audit permissions

## Monitoring Setup

### Prometheus Configuration

```yaml
# prometheus-configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: monitoring
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
      evaluation_interval: 15s
    
    scrape_configs:
      - job_name: 'kubernetes-pods'
        kubernetes_sd_configs:
          - role: pod
        relabel_configs:
          - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
            action: keep
            regex: true
          - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
            action: replace
            target_label: __metrics_path__
            regex: (.+)
          - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
            action: replace
            regex: (.+):(?:\d+);(\d+)
            replacement: ${1}:${2}
            target_label: __address__
          - source_labels: [__meta_kubernetes_namespace]
            action: replace
            target_label: kubernetes_namespace
          - source_labels: [__meta_kubernetes_pod_name]
            action: replace
            target_label: kubernetes_pod_name
```

### Grafana Dashboard Example

A basic dashboard for monitoring Bifrost would include:

1. **API Performance**:
   - Request rate
   - Error rate
   - Average response time
   - P95 and P99 response times

2. **System Resources**:
   - CPU usage per pod
   - Memory usage per pod
   - Disk I/O
   - Network traffic

3. **Database Metrics**:
   - Connection count
   - Query performance
   - Transaction rate
   - Cache hit ratio

4. **Application Metrics**:
   - Active users
   - Asset creation rate
   - Asset retrieval rate
   - Background job processing rate

## Deployment Checklist

Before deploying to production, ensure:

1. **Security**:
   - All containers are scanned for vulnerabilities
   - Secrets are properly managed (not in code)
   - Network policies are in place
   - TLS is configured for all ingress points

2. **Resources**:
   - Resource requests and limits are set for all containers
   - Horizontal Pod Autoscalers are configured
   - Storage is properly sized and backed up

3. **Monitoring**:
   - Prometheus scraping is configured
   - Grafana dashboards are set up
   - Alerting rules are defined
   - Log aggregation is working

4. **High Availability**:
   - Multi-zone deployment
   - Database replication
   - Proper pod anti-affinity rules
   - Readiness and liveness probes

5. **Disaster Recovery**:
   - Backup procedures are tested
   - Restore procedures are documented and tested
   - DR plan is communicated to team
