# SafeVault

A secure secrets management application with AWS Secrets Manager integration.

## Architecture

- **Backend**: FastAPI with AWS Secrets Manager integration
- **Frontend**: React UI for secrets management
- **Infrastructure**: Terraform for AWS provisioning
- **CI/CD**: GitHub Actions with ECR deployment

## Quick Start

1. **Local Development**:
   ```bash
   # Backend
   cd backend
   pip install -r requirements.txt
   uvicorn app:app --reload
   
   # Frontend
   cd frontend
   npm install
   npm start
   ```

2. **Docker**:
   ```bash
   docker-compose up
   ```

3. **Infrastructure**:
   ```bash
   cd terraform
   terraform init
   terraform plan
   terraform apply
   ```

## Features

- ✅ CRUD operations for secrets
- ✅ AWS Secrets Manager integration
- ✅ Role-based access control
- ✅ Docker containerization
- ✅ Terraform infrastructure
- ✅ CI/CD pipeline

## Security

- Secrets stored in AWS Secrets Manager (not in app)
- IAM roles with least privilege
- HTTPS ready (cert-manager integration needed)
- Token-based authentication (JWT implementation needed)