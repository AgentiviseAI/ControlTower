# Control Tower

This is the backend API and control plane for the Agent Platform.

## Features
- FastAPI Python application
- SQLite database
- Docker support
- Azure App Service deployment
- Remote debugging support

## Development

### Prerequisites
- Python 3.11 or higher
- pip
- Docker (for containerized debugging)

### Installation
```bash
pip install -r requirements.txt
```

### Running the Application
```bash
python main.py
```

### Debug Mode

For troubleshooting and development, you can run ControlTower in debug mode with remote debugging support:

#### Quick Start (PowerShell)
```powershell
./setup-debug.ps1
```

#### Manual Setup
```bash
# Build and start debug container
docker-compose -f docker-compose.debug.yml up --build

# The service will be available at:
# - API: http://localhost:8001
# - Debug port: localhost:5679
```

#### IDE Debug Configuration
Configure your IDE to connect to remote debugger:
- **Host**: localhost
- **Port**: 5679
- **Path mappings**: Map your local code to `/app` in container

#### Testing Debug Setup
```bash
python debug_test.py
```

This script will test API endpoints and trigger authorization methods like `checkPermissions` where you can set breakpoints.

## Deployment

This repository is configured for automatic deployment to Azure App Service using GitHub Actions.

### Setup
1. Create an Azure App Service instance for Python
2. Download the publish profile
3. Add the publish profile as a GitHub secret named `AZURE_WEBAPP_PUBLISH_PROFILE`
4. Update the `AZURE_WEBAPP_NAME` in `.github/workflows/azure-deploy.yml`

The application will be automatically deployed when changes are pushed to the main branch.
