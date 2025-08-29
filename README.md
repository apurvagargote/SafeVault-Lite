# SafeVault Lite

A secure secrets management application with AWS Secrets Manager integration, built with FastAPI backend, React frontend, and complete CI/CD pipeline.

## 🚀 Live Demo

- **Frontend**: [https://apurvagargote.github.io/SafeVault-Lite/](https://apurvagargote.github.io/SafeVault-Lite/)
- **Docker Images**: 
  - Backend: `apurva1025/safevault-backend:latest`
  - Frontend: `apurva1025/safevault-frontend:latest`

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React UI      │────│   FastAPI       │────│  AWS Secrets    │
│   (Frontend)    │    │   (Backend)     │    │   Manager       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └──────────────│   PostgreSQL    │──────────────┘
                        │   (Database)    │
                        └─────────────────┘
```

## 🛠️ Tech Stack

- **Backend**: FastAPI, Python 3.11, SQLAlchemy, JWT Authentication
- **Frontend**: React 18, Axios, React Router
- **Database**: PostgreSQL (production), SQLite (development)
- **Cloud**: AWS Secrets Manager
- **Monitoring**: Prometheus, Grafana
- **Containerization**: Docker, Docker Compose
- **Orchestration**: Kubernetes, Kind
- **CI/CD**: GitHub Actions
- **Deployment**: GitHub Pages, Docker Hub

## 🚦 CI/CD Pipeline

The project includes a comprehensive CI/CD pipeline that automatically:

1. **Detects Changes** - Only builds what changed (backend/frontend)
2. **Builds Docker Images** - Pushes to Docker Hub with commit SHA tags
3. **Deploys to GitHub Pages** - Frontend available for demo
4. **Tests Kubernetes Deployment** - Validates in Kind cluster
5. **Monitors with Prometheus** - Collects metrics and health checks

### Pipeline Triggers
- **Push to `main`/`dev`** - Full pipeline execution
- **Pull Requests** - Build and test validation
- **Path-based builds** - Only affected components rebuild

## 🏃‍♂️ Quick Start

### Option 1: Docker Compose (Recommended)
```bash
git clone https://github.com/apurvagargote/SafeVault-Lite.git
cd SafeVault-Lite
docker-compose up
```
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Grafana: http://localhost:3001

### Option 2: Local Development
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app:app --reload

# Frontend (new terminal)
cd frontend
npm install
npm start
```

### Option 3: Kubernetes with Kind
```bash
# Create cluster
kind create cluster --name safevault

# Deploy
kubectl apply -f k8s/deploy-all.yaml

# Access via port-forward
kubectl port-forward service/safevault-frontend-service 3000:80
```

## 📁 Project Structure

```
SafeVault-Lite/
├── backend/                 # FastAPI application
│   ├── app.py              # Main application
│   ├── auth.py             # JWT authentication
│   ├── database.py         # Database models
│   ├── metrics.py          # Prometheus metrics
│   ├── Dockerfile          # Backend container
│   └── requirements.txt    # Python dependencies
├── frontend/               # React application
│   ├── src/
│   │   ├── App.js         # Main component
│   │   ├── Login.js       # Authentication
│   │   └── *.css          # Styling files
│   ├── public/
│   │   └── index.html     # HTML template
│   ├── Dockerfile         # Frontend container
│   └── package.json       # Node dependencies
├── k8s/                   # Kubernetes manifests
│   ├── deploy-all.yaml    # Complete deployment
│   ├── grafana-deployment.yaml
│   ├── prometheus-deployment.yaml
│   └── monitoring-rbac.yaml
├── monitoring/            # Monitoring configuration
│   ├── grafana/          # Grafana dashboards
│   └── prometheus.yml    # Prometheus config
├── .github/workflows/     # CI/CD pipeline
│   └── ci-cd.yml         # GitHub Actions workflow
├── docker-compose.yml     # Local development
├── docker-compose.monitoring.yml  # Monitoring stack
└── .env.example          # Environment template
```

## 🔧 Configuration

### Environment Variables
Copy `.env.example` to `.env` and configure:

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/safevault

# Security
SECRET_KEY=your-jwt-secret-key

# AWS
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1

# Email (Gmail SMTP)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### GitHub Secrets (for CI/CD)
Add these secrets to your GitHub repository:

- `DOCKER_USERNAME` - Docker Hub username
- `DOCKER_PASSWORD` - Docker Hub access token

## 🎯 Features

- ✅ **Secure Secret Management** - Store secrets in AWS Secrets Manager
- ✅ **JWT Authentication** - Secure user authentication
- ✅ **Category-based Organization** - Organize secrets by categories
- ✅ **Real-time Monitoring** - Prometheus metrics & Grafana dashboards
- ✅ **Responsive UI** - Mobile-friendly React interface
- ✅ **Docker Ready** - Complete containerization
- ✅ **Kubernetes Native** - Production-ready K8s manifests
- ✅ **CI/CD Pipeline** - Automated build, test, and deploy

## 📊 Monitoring

Access monitoring dashboards:
- **Prometheus**: http://localhost:9090 (metrics collection)
- **Grafana**: http://localhost:3001 (visualization)
  - Username: `admin`
  - Password: `admin`

### Available Metrics
- HTTP request metrics
- Authentication events
- AWS operations
- Database connections
- Business metrics (secrets count, user activity)

## 🚀 Production Deployment

### AWS EKS Deployment
1. Create EKS cluster
2. Create AWS credentials secret: `kubectl create secret generic aws-credentials --from-literal=access-key-id=your-key --from-literal=secret-access-key=your-secret`
3. Deploy: `kubectl apply -f k8s/deploy-all.yaml`

### Manual Docker Deployment
```bash
# Pull latest images
docker pull apurva1025/safevault-backend:latest
docker pull apurva1025/safevault-frontend:latest

# Run with custom configuration
docker run -d -p 8000:8000 \
  -e DATABASE_URL=your-db-url \
  -e AWS_ACCESS_KEY_ID=your-key \
  apurva1025/safevault-backend:latest
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Repository**: [https://github.com/apurvagargote/SafeVault-Lite](https://github.com/apurvagargote/SafeVault-Lite)
- **Docker Hub**: [https://hub.docker.com/u/apurva1025](https://hub.docker.com/u/apurva1025)
- **Live Demo**: [https://apurvagargote.github.io/SafeVault-Lite/](https://apurvagargote.github.io/SafeVault-Lite/)

---

**Built with ❤️ by [Apurva Gargote](https://github.com/apurvagargote)**