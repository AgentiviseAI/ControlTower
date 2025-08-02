# ControlTower CI/CD Pipeline

This directory contains a single, comprehensive GitHub Actions workflow for the ControlTower service.

## Single Workflow: `complete-pipeline.yml`

A unified CI/CD pipeline that handles everything from code quality to production deployment in logical stages.

### 🔄 **Pipeline Stages (Automatic Flow):**

1. **Quality Gates** 🧪
   - Code formatting (black, isort)
   - Linting (flake8)
   - Security scanning (bandit, safety)
   - Unit tests with coverage
   - **Runs on**: Every push/PR

2. **Build & Push** 🐳
   - Docker image build
   - Push to Azure Container Registry
   - Container security scan
   - **Runs on**: Main branch only (after quality gates pass)

3. **Staging Deployment** 🚀
   - Automatic deployment to staging
   - **Runs on**: Main branch only (after successful build)

4. **Production Deployment** 🎯
   - Manual deployment to production
   - Health checks and validation
   - **Runs on**: Manual trigger only

### 📋 **Triggers:**

**Automatic:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

**Manual (workflow_dispatch):**
- Deploy to production: `true/false`
- Custom image tag: `latest` (default) or specific tag

### 🎛️ **How to Use:**

#### For Development:
1. Create a PR → Quality gates run automatically
2. Merge to main → Quality gates + Build + Staging deployment

#### For Production:
1. Go to Actions tab → "ControlTower Complete CI/CD Pipeline"
2. Click "Run workflow"
3. Set "Deploy to production" to `true`
4. Choose image tag (leave empty for latest)
5. Click "Run workflow"

### 🔧 **Required Secrets:**

```
# Azure Container Registry
ACR_USERNAME=<registry-username>
ACR_PASSWORD=<registry-password>

# Azure Authentication (OIDC)
AZURE_CLIENT_ID=<service-principal-client-id>
AZURE_TENANT_ID=<azure-tenant-id>
AZURE_SUBSCRIPTION_ID=<azure-subscription-id>

# Azure Resources
AZURE_RESOURCE_GROUP=<resource-group-name>
```

### 🏗️ **Pipeline Flow:**

```
Developer Push/PR
       ↓
🧪 Quality Gates (always)
   ├─ Code formatting check
   ├─ Linting & security scan
   ├─ Unit tests
   └─ Coverage report
       ↓ (only on main branch)
🐳 Build & Push (conditional)
   ├─ Docker build
   ├─ Push to ACR
   └─ Container security scan
       ↓ (automatic on main)
🚀 Staging Deploy (automatic)
   └─ Deploy to staging environment
       ↓ (manual trigger only)
🎯 Production Deploy (manual)
   ├─ Deploy to production
   ├─ Health checks
   └─ Success notification
```

### 🎯 **Benefits of Single Workflow:**

✅ **Simplified**: One file to maintain instead of three  
✅ **Sequential**: Logical flow with proper dependencies  
✅ **Efficient**: Shares artifacts between stages  
✅ **Safe**: Production requires manual approval  
✅ **Smart**: Only builds when relevant files change  
✅ **Comprehensive**: All CI/CD needs in one place  

### 📊 **Image Registry:**

Images are pushed to: `agentiviseregistry-c4cme7esd7cvddhc.azurecr.io/control-tower`

**Available tags:**
- `latest` - Latest main branch build
- `main-COMMIT_SHA` - Specific commit builds
- `pr-NUMBER` - Pull request builds

### 🔍 **Monitoring:**

- **Workflow runs**: GitHub Actions tab
- **Code coverage**: Codecov integration
- **Security**: Bandit and Trivy scan results
- **Production health**: Automatic health checks post-deployment
