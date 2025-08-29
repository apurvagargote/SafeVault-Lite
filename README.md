# SafeVault Lite

A comprehensive secrets management application with AWS Secrets Manager integration, featuring secure authentication, real-time monitoring, and complete CI/CD automation.

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
         └──────────────│   SQLite/       │──────────────┘
                        │   PostgreSQL    │
                        └─────────────────┘
```

## 🔐 Security Features

### Authentication & Authorization
- **JWT-based Authentication** - Secure token-based user sessions
- **Password Hashing** - Bcrypt encryption for user passwords
- **Role-based Access Control** - User and admin roles with different permissions
- **Session Management** - Configurable token expiration and refresh

### Security Monitoring
- **Failed Login Detection** - Automatic alerts after multiple failed attempts
- **Security Event Logging** - Comprehensive audit trail of all user actions
- **Email Alerts** - Real-time notifications for suspicious activities
- **IP Address Tracking** - Monitor access patterns and locations

### Data Protection
- **Hybrid Storage** - Local database + AWS Secrets Manager encryption
- **Category-based Organization** - Organize secrets by type (API keys, passwords, etc.)
- **Automatic Sync** - Seamless synchronization between local and cloud storage
- **Fallback Mechanism** - Continues working even if AWS is unavailable

## 🛠️ Tech Stack

- **Backend**: FastAPI, Python 3.11, SQLAlchemy, JWT Authentication
- **Frontend**: React 18, Axios, React Router, Responsive CSS
- **Database**: SQLite (development), PostgreSQL (production)
- **Cloud**: AWS Secrets Manager, EC2 deployment
- **Monitoring**: Prometheus metrics, Grafana dashboards
- **Containerization**: Docker, Docker Compose
- **Orchestration**: Kubernetes, Kind (testing)
- **CI/CD**: GitHub Actions with automated builds and deployments

## 🚦 CI/CD Pipeline

Advanced automation pipeline with intelligent path-based builds:

### Pipeline Features
1. **Smart Change Detection** - Only builds components that changed
2. **Parallel Builds** - Backend and frontend build simultaneously
3. **Docker Registry** - Automatic push to Docker Hub with SHA tags
4. **GitHub Pages Deployment** - Frontend automatically deployed for demos
5. **Kubernetes Testing** - Validates deployments in Kind cluster
6. **Monitoring Integration** - Prometheus metrics collection

### Pipeline Triggers
- **Push to `main`/`dev`** - Full pipeline execution
- **Pull Requests** - Build validation and testing
- **Path-based optimization** - Only affected components rebuild

## 🏃♂️ Quick Start

### Option 1: Docker Compose (Recommended)
```bash
git clone https://github.com/apurvagargote/SafeVault-Lite.git
cd SafeVault-Lite

# Create environment file
cp .env.example .env
# Edit .env with your AWS credentials

# Start all services
docker-compose up -d
```
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Grafana Dashboard**: http://localhost:3001 (admin/admin)

### Option 2: Local Development
```bash
# Backend setup
cd backend
pip install -r requirements.txt
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Frontend setup (new terminal)
cd frontend
npm install
npm start
```

### Option 3: Kubernetes Deployment
```bash
# Create Kind cluster
kind create cluster --name safevault

# Deploy application
kubectl apply -f k8s/deploy-all.yaml

# Access via port-forward
kubectl port-forward service/safevault-frontend-service 3000:80
kubectl port-forward service/safevault-backend-service 8000:8000
```

## 📁 Project Structure

```
SafeVault-Lite/
├── backend/                 # FastAPI application
│   ├── app.py              # Main application with all endpoints
│   ├── auth.py             # JWT authentication & password hashing
│   ├── database.py         # SQLAlchemy models (User, Secret, SecurityLog)
│   ├── metrics.py          # Prometheus metrics collection
│   ├── Dockerfile          # Backend container configuration
│   └── requirements.txt    # Python dependencies
├── frontend/               # React application
│   ├── src/
│   │   ├── App.js         # Main component with routing
│   │   ├── Login.js       # Authentication interface
│   │   ├── Signup.js      # User registration
│   │   └── *.css          # Responsive styling
│   ├── public/
│   │   └── index.html     # HTML template
│   ├── Dockerfile         # Frontend container configuration
│   └── package.json       # Node.js dependencies
├── k8s/                   # Kubernetes manifests
│   ├── deploy-all.yaml    # Complete application deployment
│   ├── grafana-deployment.yaml    # Monitoring dashboard
│   ├── prometheus-deployment.yaml # Metrics collection
│   └── monitoring-rbac.yaml      # Monitoring permissions
├── monitoring/            # Monitoring configuration
│   ├── grafana/          # Dashboard configurations
│   └── prometheus.yml    # Metrics scraping config
├── .github/workflows/     # CI/CD automation
│   └── ci-cd.yml         # GitHub Actions pipeline
├── docker-compose.yml     # Local development environment
├── docker-compose.monitoring.yml  # Monitoring stack
└── .env.example          # Environment variables template
```

## 🔧 Configuration

### Environment Variables
Create `.env` file from template:

```bash
# Security Configuration
SECRET_KEY=your-super-secure-jwt-secret-key
DATABASE_URL=sqlite:///./safevault.db

# AWS Secrets Manager
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=eu-west-1

# Email Alerts (Gmail SMTP)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-gmail-app-password
FROM_EMAIL=noreply@safevault.com
```

### GitHub Secrets (for CI/CD)
Required repository secrets:

- `DOCKER_USERNAME` - Docker Hub username
- `DOCKER_PASSWORD` - Docker Hub access token

## 🎯 Core Features

### User Management
- ✅ **User Registration** - Secure account creation with email validation
- ✅ **JWT Authentication** - Token-based secure sessions
- ✅ **Password Management** - Secure password changes with validation
- ✅ **Role-based Access** - User and admin permission levels

### Secret Management
- ✅ **Create Secrets** - Store sensitive data securely
- ✅ **Category Organization** - Group secrets by type (API keys, passwords, etc.)
- ✅ **AWS Integration** - Automatic sync with AWS Secrets Manager
- ✅ **Local Fallback** - Works offline with local database
- ✅ **Search & Filter** - Easy secret discovery and management

### Security & Monitoring
- ✅ **Security Logging** - Complete audit trail of all actions
- ✅ **Failed Login Alerts** - Email notifications for suspicious activity
- ✅ **Real-time Metrics** - Prometheus monitoring with Grafana dashboards
- ✅ **IP Tracking** - Monitor access patterns and locations
- ✅ **Session Management** - Secure token handling and expiration

### DevOps & Deployment
- ✅ **Docker Containerization** - Complete containerized deployment
- ✅ **Kubernetes Ready** - Production-ready K8s manifests
- ✅ **CI/CD Automation** - Automated builds, tests, and deployments
- ✅ **Multi-environment** - Development, staging, and production configs

## 📊 Monitoring & Analytics

### Prometheus Metrics
- HTTP request metrics (response times, status codes)
- Authentication events (successful/failed logins)
- AWS operations (create/read/delete secrets)
- Database connections and query performance
- Business metrics (user count, secrets count)

### Grafana Dashboards
- **System Overview** - Application health and performance
- **Security Dashboard** - Authentication and access patterns
- **Business Metrics** - User activity and secret usage
- **Infrastructure** - Container and database metrics

Access monitoring at:
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (admin/admin)

## 🚀 Production Deployment

### AWS EC2 Deployment
```bash
# On your EC2 instance
git clone https://github.com/apurvagargote/SafeVault-Lite.git
cd SafeVault-Lite

# Configure environment
cp .env.example .env
# Edit .env with production values

# Deploy with Docker Compose
docker-compose up -d

# Access application
# Frontend: http://your-ec2-ip:3000
# Backend: http://your-ec2-ip:8000
```

### Kubernetes Production
```bash
# Create AWS credentials secret
kubectl create secret generic aws-credentials \
  --from-literal=access-key-id=your-key \
  --from-literal=secret-access-key=your-secret

# Deploy application
kubectl apply -f k8s/deploy-all.yaml

# Verify deployment
kubectl get pods
kubectl get services
```

## 🔒 Security Best Practices

### Implemented Security Measures
- **Password Hashing** - Bcrypt with salt for secure password storage
- **JWT Tokens** - Secure, stateless authentication with expiration
- **Input Validation** - Comprehensive request validation and sanitization
- **SQL Injection Prevention** - SQLAlchemy ORM with parameterized queries
- **CORS Configuration** - Controlled cross-origin resource sharing
- **Rate Limiting** - Protection against brute force attacks
- **Security Headers** - Comprehensive HTTP security headers
- **Audit Logging** - Complete trail of all security events

### Recommended Production Setup
- Use HTTPS with valid SSL certificates
- Configure firewall rules for port access
- Set up database backups and encryption
- Enable AWS CloudTrail for API auditing
- Implement network segmentation
- Regular security updates and patches

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use ESLint for JavaScript code
- Write comprehensive tests
- Update documentation for new features
- Ensure security best practices

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Repository**: [https://github.com/apurvagargote/SafeVault-Lite](https://github.com/apurvagargote/SafeVault-Lite)
- **Docker Hub**: [https://hub.docker.com/u/apurva1025](https://hub.docker.com/u/apurva1025)
- **Live Demo**: [https://apurvagargote.github.io/SafeVault-Lite/](https://apurvagargote.github.io/SafeVault-Lite/)

---

**Built with ❤️ by [Apurva Gargote](https://github.com/apurvagargote)**