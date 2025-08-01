# ControlTower CI/CD Workflows

This directory contains GitHub Actions workflows for the ControlTower service.

## Workflows

### 1. `docker-build-push.yml` - Docker Image Build and Push
Builds and pushes Docker images to Azure Container Registry.

**Triggers:**
- Push to `main` branch (with changes in ControlTower/)
- Pull requests to `main` branch
- Manual dispatch

**Features:**
- Multi-platform builds (linux/amd64, linux/arm64)
- Security scanning with Trivy
- Automatic tagging (branch, PR, SHA, latest)
- Deployment to staging environment
- Build caching for faster builds

**Required Secrets:**
- `ACR_USERNAME` - Azure Container Registry username
- `ACR_PASSWORD` - Azure Container Registry password
- `AZURE_RESOURCE_GROUP` - Azure resource group for staging deployment
- `SECRET_KEY` - Application secret key
- `DATABASE_URL_STAGING` - Staging database connection string

### 2. `deploy-production.yml` - Production Deployment
Manual deployment workflow for production releases.

**Triggers:**
- Manual dispatch only

**Features:**
- Choose specific image tag to deploy
- Select target environment (production/staging)
- Health checks after deployment
- Deployment status notifications

**Required Secrets:**
- `AZURE_CLIENT_ID` - Azure service principal client ID
- `AZURE_TENANT_ID` - Azure tenant ID
- `AZURE_SUBSCRIPTION_ID` - Azure subscription ID

### 3. `ci-cd.yml` - Continuous Integration
Runs tests, linting, and security checks.

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

**Features:**
- Python 3.11 testing
- Code formatting checks (black, isort)
- Linting with flake8
- Unit tests with pytest
- Coverage reporting
- Security scanning with bandit and safety

## Setup Instructions

### 1. Azure Container Registry Setup

```bash
# Get ACR credentials
az acr credential show --name agentiviseregistry-c4cme7esd7cvddhc
```

Add these as GitHub secrets:
- `ACR_USERNAME`: Registry username
- `ACR_PASSWORD`: Registry password

### 2. Azure Service Principal for OIDC

```bash
# Create service principal
az ad sp create-for-rbac --name "GitHubActions-ControlTower" \
  --role contributor \
  --scopes /subscriptions/YOUR_SUBSCRIPTION_ID

# Configure federated identity
az ad app federated-credential create \
  --id CLIENT_ID \
  --parameters '{
    "name": "GitHubActions-main",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:AgentiviseAI/agent-platform:ref:refs/heads/main",
    "audiences": ["api://AzureADTokenExchange"]
  }'
```

### 3. Environment Variables

Set these in Azure App Service Configuration:
```
DATABASE_URL=postgresql://user:pass@host:5432/db
SECRET_KEY=your-production-secret-key
ENVIRONMENT=production
DEBUG=false
HOST=0.0.0.0
PORT=8000
```

## Image Registry

Images are pushed to: `agentiviseregistry-c4cme7esd7cvddhc.azurecr.io/control-tower`

**Available tags:**
- `latest` - Latest main branch build
- `main-COMMIT_SHA` - Specific commit from main
- `pr-NUMBER` - Pull request builds

## Usage

### Building and Pushing Images
Push to main branch or create a PR. The workflow will automatically build and push the image.

### Deploying to Production
1. Go to Actions tab in GitHub
2. Select "Deploy ControlTower to Production"
3. Click "Run workflow"
4. Choose image tag and environment
5. Click "Run workflow"

### Monitoring
- Check workflow runs in the Actions tab
- View deployment logs in Azure App Service
- Monitor application health via health check endpoints
