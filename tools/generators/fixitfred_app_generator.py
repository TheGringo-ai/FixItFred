#!/usr/bin/env python3
"""
FixItFred AI Development Platform - App Generator
Enhanced app generation with AI team integration for FixItFred

Features:
- AI-powered app scaffolding
- FixItFred-specific templates
- Integrated deployment automation
- Grok AI team collaboration
- Development workflow optimization
"""

import os
import json
import yaml
import argparse
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid
import asyncio

# Import our AI team for intelligent app generation
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from core.ai_brain.ai_team_integration import FixItFredAITeam

class FixItFredAppTemplate:
    """Enhanced base class for FixItFred app templates with AI integration"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.files = {}
        self.variables = {}
        self.ai_team = FixItFredAITeam()
    
    def add_file(self, path: str, content: str):
        """Add a file template"""
        self.files[path] = content
    
    def add_variable(self, name: str, description: str, default: Any = None, required: bool = True):
        """Add a template variable"""
        self.variables[name] = {
            "description": description,
            "default": default,
            "required": required
        }
    
    def render_file(self, content: str, variables: Dict[str, Any]) -> str:
        """Render file content with variables"""
        for var_name, var_value in variables.items():
            content = content.replace(f"{{{{ {var_name} }}}}", str(var_value))
        return content
    
    async def ai_enhance_template(self, app_name: str, variables: Dict[str, Any]) -> Dict[str, str]:
        """Use AI team to enhance template generation"""
        try:
            prompt = f"""
            Generate enhanced code templates for FixItFred application:
            
            App Name: {app_name}
            App Type: {self.name}
            Description: {self.description}
            Variables: {json.dumps(variables, indent=2)}
            
            Provide improvements for:
            1. Error handling and logging
            2. Security best practices
            3. Performance optimization
            4. FixItFred platform integration
            5. AI-powered features
            
            Focus on making the code production-ready and following FixItFred patterns.
            """
            
            responses = await self.ai_team.collaborate_with_ai_team(prompt, task_type="code_generation")
            best_response = max(responses.values(), key=lambda x: x.confidence)
            
            return {
                "enhanced_features": best_response.content,
                "suggestions": best_response.suggestions,
                "confidence": best_response.confidence
            }
        except Exception as e:
            print(f"⚠️  AI enhancement failed: {e}")
            return {"enhanced_features": "", "suggestions": [], "confidence": 0.0}
    
    async def generate_app(self, app_name: str, output_dir: Path, variables: Dict[str, Any]):
        """Generate app from template with AI enhancements"""
        app_dir = output_dir / app_name
        app_dir.mkdir(parents=True, exist_ok=True)
        
        # Add standard variables
        variables.update({
            "app_name": app_name,
            "app_name_lower": app_name.lower(),
            "app_name_upper": app_name.upper(),
            "created_at": datetime.now().isoformat(),
            "uuid": str(uuid.uuid4())
        })
        
        # Get AI enhancements
        print("🤖 AI team enhancing template...")
        ai_enhancements = await self.ai_enhance_template(app_name, variables)
        variables["ai_enhancements"] = ai_enhancements.get("enhanced_features", "")
        
        # Generate files
        for file_path, file_content in self.files.items():
            rendered_path = self.render_file(file_path, variables)
            full_path = app_dir / rendered_path
            
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            rendered_content = self.render_file(file_content, variables)
            with open(full_path, 'w') as f:
                f.write(rendered_content)
        
        # Create AI enhancement summary
        if ai_enhancements.get("suggestions"):
            enhancement_file = app_dir / "AI_ENHANCEMENTS.md"
            with open(enhancement_file, 'w') as f:
                f.write(f"# AI Enhancements for {app_name}\n\n")
                f.write(f"**Confidence Score:** {ai_enhancements.get('confidence', 0):.2f}\n\n")
                f.write("## AI Suggestions:\n\n")
                for suggestion in ai_enhancements.get("suggestions", []):
                    f.write(f"- {suggestion}\n")
                f.write(f"\n## Enhanced Features:\n\n{ai_enhancements.get('enhanced_features', '')}\n")
        
        print(f"✅ Generated {self.name} app: {app_name} in {app_dir}")
        print(f"🤖 AI confidence: {ai_enhancements.get('confidence', 0):.2f}")

class FixItFredMicroserviceTemplate(FixItFredAppTemplate):
    """Template for FixItFred microservices with AI integration"""
    
    def __init__(self):
        super().__init__("FixItFred Microservice", "AI-powered microservice for FixItFred platform")
        
        self.add_variable("service_description", "Description of the microservice", "FixItFred microservice")
        self.add_variable("ai_features", "AI features to include", "diagnosis,repair,optimization")
        self.add_variable("port", "Service port", 8100, required=False)
        
        # Service configuration
        self.add_file("service.yaml", '''# FixItFred Microservice Configuration
name: {{ app_name_lower }}
version: "1.0.0"
description: "{{ service_description }}"
type: "microservice"

# FixItFred Integration
fixitfred:
  ai_enabled: true
  features: {{ ai_features }}
  auto_scaling: true
  monitoring: true

# Service Configuration
service:
  port: {{ port }}
  health_endpoint: "/health"
  metrics_endpoint: "/metrics"
  
# AI Team Configuration
ai_team:
  providers: ["grok", "claude", "openai"]
  collaboration_mode: "parallel"
  confidence_threshold: 0.7

# Deployment
deployment:
  platform: "gcp_cloud_run"
  environment: "production"
  scaling:
    min_instances: 0
    max_instances: 10
  resources:
    memory: "1Gi"
    cpu: "1"

created_at: "{{ created_at }}"
''')
        
        # Main service implementation
        self.add_file("main.py", '''#!/usr/bin/env python3
"""
{{ app_name }} - FixItFred Microservice
{{ service_description }}

Enhanced with AI team integration for intelligent problem-solving.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import logging
import os
import sys
import asyncio
from datetime import datetime

# FixItFred AI Integration
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from core.ai_brain.ai_team_integration import FixItFredAITeam, FixItFredTaskType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models
class ServiceRequest(BaseModel):
    request_id: Optional[str] = None
    task_type: str = "analysis"
    description: str
    context: Optional[Dict[str, Any]] = None
    priority: str = "medium"

class ServiceResponse(BaseModel):
    request_id: str
    status: str
    result: Dict[str, Any]
    ai_provider: str
    confidence: float
    processing_time: float
    suggestions: List[str]

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    ai_team_status: Dict[str, Any]
    uptime: str

# Initialize FastAPI app
app = FastAPI(
    title="{{ app_name }} FixItFred Service",
    description="{{ service_description }}",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI team
ai_team = FixItFredAITeam()
service_start_time = datetime.now()

@app.on_event("startup")
async def startup():
    """Service startup initialization"""
    logger.info("🔧 Starting {{ app_name }} FixItFred Service")
    logger.info(f"🤖 AI Team initialized with providers: {[p.value for p in ai_team.get_available_providers()]}")

@app.on_event("shutdown")
async def shutdown():
    """Service shutdown cleanup"""
    logger.info("🔧 Shutting down {{ app_name }} FixItFred Service")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Comprehensive health check with AI team status"""
    uptime = datetime.now() - service_start_time
    
    return HealthResponse(
        status="healthy",
        service="{{ app_name }}",
        version="1.0.0",
        ai_team_status=ai_team.get_ai_team_status(),
        uptime=str(uptime)
    )

@app.post("/api/process", response_model=ServiceResponse)
async def process_request(request: ServiceRequest):
    """Process a FixItFred service request with AI team collaboration"""
    start_time = datetime.now()
    request_id = request.request_id or f"req_{int(start_time.timestamp())}"
    
    try:
        logger.info(f"🔧 Processing request {request_id}: {request.description[:100]}...")
        
        # Determine task type
        task_type_map = {
            "diagnosis": FixItFredTaskType.DIAGNOSIS,
            "repair": FixItFredTaskType.REPAIR,
            "optimization": FixItFredTaskType.OPTIMIZATION,
            "troubleshooting": FixItFredTaskType.TROUBLESHOOTING,
            "analysis": FixItFredTaskType.ANALYSIS
        }
        
        task_type = task_type_map.get(request.task_type, FixItFredTaskType.ANALYSIS)
        
        # Use AI team for processing
        if task_type == FixItFredTaskType.DIAGNOSIS:
            responses = await ai_team.diagnose_with_ai_team(
                request.description, 
                request.context
            )
        else:
            responses = await ai_team.collaborate_with_ai_team(
                request.description,
                task_type=task_type,
                include_reasoning=True
            )
        
        # Get best response
        best_response = max(responses.values(), key=lambda x: x.confidence)
        processing_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"✅ Request {request_id} completed in {processing_time:.2f}s")
        
        return ServiceResponse(
            request_id=request_id,
            status="completed",
            result={
                "content": best_response.content,
                "reasoning": best_response.reasoning,
                "fix_instructions": best_response.fix_instructions,
                "all_responses": {k: v.content for k, v in responses.items()}
            },
            ai_provider=best_response.provider.value,
            confidence=best_response.confidence,
            processing_time=processing_time,
            suggestions=best_response.suggestions
        )
        
    except Exception as e:
        processing_time = (datetime.now() - start_time).total_seconds()
        logger.error(f"❌ Request {request_id} failed: {e}")
        
        return ServiceResponse(
            request_id=request_id,
            status="failed",
            result={"error": str(e)},
            ai_provider="error",
            confidence=0.0,
            processing_time=processing_time,
            suggestions=["Check service logs", "Retry with different parameters"]
        )

@app.get("/api/diagnose/{problem_type}")
async def quick_diagnosis(problem_type: str, description: str):
    """Quick diagnosis endpoint for common FixItFred problems"""
    try:
        responses = await ai_team.diagnose_with_ai_team(
            f"{problem_type}: {description}",
            {"problem_type": problem_type}
        )
        
        best_response = max(responses.values(), key=lambda x: x.confidence)
        
        return {
            "diagnosis": best_response.content,
            "fix_steps": best_response.fix_instructions,
            "confidence": best_response.confidence,
            "ai_provider": best_response.provider.value
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/optimize/{system_type}")
async def optimize_system(system_type: str, current_config: str):
    """System optimization endpoint"""
    try:
        prompt = f"Optimize {system_type} system with current configuration: {current_config}"
        
        responses = await ai_team.collaborate_with_ai_team(
            prompt,
            task_type=FixItFredTaskType.OPTIMIZATION
        )
        
        best_response = max(responses.values(), key=lambda x: x.confidence)
        
        return {
            "optimizations": best_response.content,
            "implementation_steps": best_response.fix_instructions,
            "confidence": best_response.confidence,
            "suggestions": best_response.suggestions
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status")
async def service_status():
    """Detailed service status including AI team metrics"""
    return {
        "service": "{{ app_name }}",
        "status": "running",
        "ai_team": ai_team.get_ai_team_status(),
        "features": "{{ ai_features }}".split(","),
        "uptime": str(datetime.now() - service_start_time),
        "version": "1.0.0"
    }

@app.get("/metrics")
async def metrics():
    """Prometheus-style metrics endpoint"""
    ai_status = ai_team.get_ai_team_status()
    uptime_seconds = (datetime.now() - service_start_time).total_seconds()
    
    return {
        "fixitfred_service_uptime_seconds": uptime_seconds,
        "fixitfred_ai_providers_available": len(ai_status["available_providers"]),
        "fixitfred_active_tasks": ai_status["active_tasks"],
        "fixitfred_completed_tasks": ai_status["completed_tasks"],
        "fixitfred_fix_history_count": ai_status.get("fix_history_count", 0)
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", {{ port }}))
    logger.info(f"🚀 Starting {{ app_name }} on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
''')
        
        # Requirements file
        self.add_file("requirements.txt", '''fastapi>=0.104.0
uvicorn[standard]>=0.24.0
httpx>=0.25.0
pydantic>=2.4.0
PyYAML>=6.0
python-multipart>=0.0.6
''')
        
        # Dockerfile with FixItFred optimizations
        self.add_file("Dockerfile", '''FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Create non-root user
RUN useradd --create-home --shell /bin/bash fixitfred

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .
RUN chown -R fixitfred:fixitfred /app

# Switch to non-root user
USER fixitfred

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:{{ port }}/health || exit 1

EXPOSE {{ port }}

CMD ["python", "main.py"]
''')
        
        # GitHub Actions CI/CD
        self.add_file(".github/workflows/deploy.yml", '''name: Deploy {{ app_name }} to FixItFred

on:
  push:
    branches: [ main, dev ]
  pull_request:
    branches: [ main ]

env:
  PROJECT_ID: fredfix
  SERVICE_NAME: {{ app_name_lower }}
  REGION: us-central1

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-asyncio
    
    - name: Run tests
      run: pytest tests/ -v

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Google Cloud
      uses: google-github-actions/setup-gcloud@v1
      with:
        project_id: ${{ env.PROJECT_ID }}
        service_account_key: ${{ secrets.GCP_SA_KEY }}
        export_default_credentials: true
    
    - name: Configure Docker
      run: gcloud auth configure-docker gcr.io
    
    - name: Build and Push
      run: |
        docker build -t gcr.io/${{ env.PROJECT_ID }}/${{ env.SERVICE_NAME }}:${{ github.sha }} .
        docker push gcr.io/${{ env.PROJECT_ID }}/${{ env.SERVICE_NAME }}:${{ github.sha }}
    
    - name: Deploy to Cloud Run
      run: |
        gcloud run deploy ${{ env.SERVICE_NAME }} \\
          --image gcr.io/${{ env.PROJECT_ID }}/${{ env.SERVICE_NAME }}:${{ github.sha }} \\
          --region ${{ env.REGION }} \\
          --platform managed \\
          --allow-unauthenticated \\
          --memory 1Gi \\
          --cpu 1 \\
          --port {{ port }}
''')
        
        # README with FixItFred integration
        self.add_file("README.md", '''# {{ app_name }} - FixItFred Microservice

{{ service_description }}

## 🤖 AI-Powered Features

This microservice is enhanced with FixItFred AI team integration:

- **Multi-AI Collaboration**: Grok + Claude + OpenAI working together
- **Intelligent Diagnosis**: AI-powered problem analysis
- **Automated Repair**: Smart fix generation and implementation
- **Optimization Engine**: Performance and efficiency improvements
- **Real-time Troubleshooting**: Instant problem resolution

## 🚀 Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your-key"
export XAI_API_KEY="your-grok-key"
export ANTHROPIC_API_KEY="your-claude-key"

# Run the service
python main.py
```

### Docker

```bash
docker build -t {{ app_name_lower }} .
docker run -p {{ port }}:{{ port }} {{ app_name_lower }}
```

### FixItFred Platform

This service integrates seamlessly with the FixItFred platform:

1. **Auto-Discovery**: Automatically registered with the platform
2. **AI Team Access**: Shared AI resources for optimal performance
3. **Event Integration**: Real-time communication with other services
4. **Monitoring**: Built-in metrics and health checks

## 📋 API Endpoints

### Core Endpoints

- `POST /api/process` - Process requests with AI team collaboration
- `GET /api/diagnose/{problem_type}` - Quick diagnosis for common issues
- `GET /api/optimize/{system_type}` - System optimization recommendations
- `GET /health` - Health check with AI team status
- `GET /metrics` - Prometheus metrics

### Example Usage

```bash
# Diagnose a problem
curl -X POST "http://localhost:{{ port }}/api/process" \\
  -H "Content-Type: application/json" \\
  -d '{
    "task_type": "diagnosis",
    "description": "Application is running slowly",
    "context": {"system": "web_server", "load": "high"}
  }'

# Quick optimization
curl "http://localhost:{{ port }}/api/optimize/database?current_config=mysql_default"
```

## 🏗️ Architecture

```
{{ app_name }}
├── AI Team Integration
│   ├── Grok (Creative Problem Solving)
│   ├── Claude (Safety & Analysis)
│   └── OpenAI (Balanced Solutions)
├── FixItFred Platform
│   ├── Service Discovery
│   ├── Event System
│   └── Shared Resources
└── FastAPI Service
    ├── REST API
    ├── Health Monitoring
    └── Metrics Collection
```

## 🔧 Configuration

Service configuration is managed through `service.yaml`:

```yaml
# AI Team Configuration
ai_team:
  providers: ["grok", "claude", "openai"]
  collaboration_mode: "parallel"
  confidence_threshold: 0.7

# FixItFred Integration
fixitfred:
  ai_enabled: true
  features: {{ ai_features }}
  auto_scaling: true
  monitoring: true
```

## 🧪 Testing

```bash
# Run tests
pytest tests/ -v

# AI team integration tests
pytest tests/test_ai_integration.py -v

# Load testing
pytest tests/test_performance.py -v
```

## 📊 Monitoring

### Health Checks

The service provides comprehensive health monitoring:

- Service health status
- AI team availability
- Resource utilization
- Performance metrics

### Metrics

Prometheus-compatible metrics are available at `/metrics`:

- `fixitfred_service_uptime_seconds`
- `fixitfred_ai_providers_available`
- `fixitfred_active_tasks`
- `fixitfred_completed_tasks`

## 🚀 Deployment

### Google Cloud Platform

```bash
# Deploy using FixItFred deployment automation
python ../../scripts/deploy-with-secrets.py

# Or manual deployment
gcloud run deploy {{ app_name_lower }} \\
  --source . \\
  --region us-central1 \\
  --allow-unauthenticated
```

### FixItFred Platform

The service automatically integrates with the FixItFred platform when deployed.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

This service is part of the FixItFred platform and follows the platform's licensing terms.

---

**Generated by FixItFred AI Development Platform**  
**AI Enhancement Confidence: {{ ai_enhancements }}**
''')

class FixItFredWebAppTemplate(FixItFredAppTemplate):
    """Template for FixItFred web applications with AI dashboard"""
    
    def __init__(self):
        super().__init__("FixItFred Web App", "AI-powered web application for FixItFred platform")
        
        self.add_variable("app_description", "Description of the web application", "FixItFred web application")
        self.add_variable("include_ai_dashboard", "Include AI team dashboard", True, required=False)
        self.add_variable("port", "Application port", 8200, required=False)
        
        # Main web application with AI integration
        self.add_file("main.py", '''#!/usr/bin/env python3
"""
{{ app_name }} - FixItFred Web Application
{{ app_description }}

Features AI team integration and FixItFred platform connectivity.
"""

from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import logging
import os
import sys

# FixItFred AI Integration
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from core.ai_brain.ai_team_integration import FixItFredAITeam

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="{{ app_name }} FixItFred Web App",
    description="{{ app_description }}",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize AI team
ai_team = FixItFredAITeam()

# Pydantic models
class AIQuery(BaseModel):
    question: str
    context: Optional[Dict[str, Any]] = None

@app.on_event("startup")
async def startup():
    """Application startup"""
    logger.info("🔧 Starting {{ app_name }} FixItFred Web App")
    logger.info(f"🤖 AI Team: {[p.value for p in ai_team.get_available_providers()]}")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with AI integration"""
    ai_status = ai_team.get_ai_team_status()
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "app_name": "{{ app_name }}",
        "description": "{{ app_description }}",
        "ai_status": ai_status,
        "include_ai_dashboard": {{ include_ai_dashboard | lower }}
    })

{% if include_ai_dashboard %}
@app.get("/ai-dashboard", response_class=HTMLResponse)
async def ai_dashboard(request: Request):
    """AI team dashboard"""
    return templates.TemplateResponse("ai_dashboard.html", {
        "request": request,
        "app_name": "{{ app_name }}"
    })

@app.post("/api/ai/ask")
async def ask_ai_team(query: AIQuery):
    """Ask the AI team a question"""
    try:
        responses = await ai_team.collaborate_with_ai_team(query.question)
        best_response = max(responses.values(), key=lambda x: x.confidence)
        
        return {
            "question": query.question,
            "answer": best_response.content,
            "ai_provider": best_response.provider.value,
            "confidence": best_response.confidence,
            "suggestions": best_response.suggestions,
            "all_responses": {k: {"content": v.content, "confidence": v.confidence} 
                            for k, v in responses.items()}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/diagnose")
async def diagnose_problem(problem: dict):
    """Diagnose a problem using AI team"""
    try:
        responses = await ai_team.diagnose_with_ai_team(
            problem["description"], 
            problem.get("context")
        )
        
        best_response = max(responses.values(), key=lambda x: x.confidence)
        
        return {
            "diagnosis": best_response.content,
            "fix_instructions": best_response.fix_instructions,
            "confidence": best_response.confidence,
            "ai_provider": best_response.provider.value
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
{% endif %}

@app.get("/health")
async def health_check():
    """Health check with AI team status"""
    return {
        "status": "healthy",
        "app": "{{ app_name }}",
        "version": "1.0.0",
        "ai_team": ai_team.get_ai_team_status()
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", {{ port }}))
    uvicorn.run(app, host="0.0.0.0", port=port)
''')
        
        # Enhanced HTML template with AI integration
        self.add_file("templates/index.html", '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ app_name }} - FixItFred</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .hero-section {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            color: white;
            padding: 100px 0;
        }
        .ai-status-card {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
        }
        .feature-card {
            border: none;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s;
            border-radius: 15px;
        }
        .feature-card:hover {
            transform: translateY(-5px);
        }
        .ai-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .ai-online { background-color: #28a745; }
        .ai-offline { background-color: #dc3545; }
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="#"><i class="fas fa-wrench"></i> {{ app_name }}</a>
            <div class="navbar-nav ms-auto">
                {% if include_ai_dashboard %}
                <a class="nav-link" href="/ai-dashboard"><i class="fas fa-brain"></i> AI Dashboard</a>
                {% endif %}
                <a class="nav-link" href="/docs"><i class="fas fa-book"></i> API Docs</a>
                <a class="nav-link" href="/health"><i class="fas fa-heartbeat"></i> Health</a>
            </div>
        </div>
    </nav>

    <!-- Hero Section -->
    <section class="hero-section text-center">
        <div class="container">
            <h1 class="display-4 fw-bold"><i class="fas fa-robot"></i> {{ app_name }}</h1>
            <p class="lead">{{ description }}</p>
            <p class="lead">Powered by FixItFred AI Team</p>
            
            <!-- AI Status Card -->
            <div class="ai-status-card">
                <h5><i class="fas fa-brain"></i> AI Team Status</h5>
                <div class="row">
                    {% for provider in ai_status.available_providers %}
                    <div class="col-md-3">
                        <span class="ai-indicator ai-online"></span>{{ provider|upper }} Online
                    </div>
                    {% endfor %}
                </div>
                <small>Active Tasks: {{ ai_status.active_tasks }} | Completed: {{ ai_status.completed_tasks }}</small>
            </div>
            
            {% if include_ai_dashboard %}
            <a href="/ai-dashboard" class="btn btn-light btn-lg me-3">
                <i class="fas fa-brain"></i> AI Dashboard
            </a>
            {% endif %}
            <a href="/docs" class="btn btn-outline-light btn-lg">
                <i class="fas fa-book"></i> API Documentation
            </a>
        </div>
    </section>

    <!-- Features Section -->
    <section class="py-5">
        <div class="container">
            <div class="row">
                <div class="col-md-4">
                    <div class="card feature-card">
                        <div class="card-body text-center">
                            <i class="fas fa-diagnoses fa-3x text-primary mb-3"></i>
                            <h5 class="card-title">AI Diagnosis</h5>
                            <p class="card-text">Intelligent problem diagnosis using multi-AI collaboration</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card feature-card">
                        <div class="card-body text-center">
                            <i class="fas fa-tools fa-3x text-success mb-3"></i>
                            <h5 class="card-title">Auto Repair</h5>
                            <p class="card-text">Automated fix generation and implementation</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card feature-card">
                        <div class="card-body text-center">
                            <i class="fas fa-tachometer-alt fa-3x text-warning mb-3"></i>
                            <h5 class="card-title">Optimization</h5>
                            <p class="card-text">Performance and efficiency improvements</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Quick AI Interaction -->
    {% if include_ai_dashboard %}
    <section class="py-5 bg-light">
        <div class="container">
            <div class="row justify-content-center">
                <div class="col-md-8">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title"><i class="fas fa-comments"></i> Ask the AI Team</h5>
                            <div class="input-group mb-3">
                                <input type="text" class="form-control" id="aiQuestion" 
                                       placeholder="Ask anything about your system...">
                                <button class="btn btn-primary" onclick="askAI()">
                                    <i class="fas fa-paper-plane"></i> Ask
                                </button>
                            </div>
                            <div id="aiResponse" class="mt-3"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>
    {% endif %}

    <!-- Footer -->
    <footer class="bg-dark text-white text-center py-4">
        <div class="container">
            <p>&copy; 2024 {{ app_name }} - Powered by FixItFred AI Platform</p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    
    {% if include_ai_dashboard %}
    <script>
        async function askAI() {
            const question = document.getElementById('aiQuestion').value;
            const responseDiv = document.getElementById('aiResponse');
            
            if (!question.trim()) return;
            
            responseDiv.innerHTML = '<div class="spinner-border text-primary" role="status"></div> AI team is thinking...';
            
            try {
                const response = await fetch('/api/ai/ask', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({question: question})
                });
                
                const data = await response.json();
                
                responseDiv.innerHTML = `
                    <div class="alert alert-primary">
                        <h6><i class="fas fa-robot"></i> ${data.ai_provider.toUpperCase()} Response (${(data.confidence * 100).toFixed(1)}% confidence)</h6>
                        <p>${data.answer}</p>
                        ${data.suggestions.length > 0 ? '<hr><small><strong>Suggestions:</strong> ' + data.suggestions.join(', ') + '</small>' : ''}
                    </div>
                `;
            } catch (error) {
                responseDiv.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
            }
            
            document.getElementById('aiQuestion').value = '';
        }
        
        document.getElementById('aiQuestion').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') askAI();
        });
    </script>
    {% endif %}
</body>
</html>
''')

class FixItFredAppGenerator:
    """Enhanced app generator with AI-powered development"""
    
    def __init__(self):
        self.templates = {
            "microservice": FixItFredMicroserviceTemplate(),
            "webapp": FixItFredWebAppTemplate(),
            "service": FixItFredMicroserviceTemplate(),  # Alias
            "web": FixItFredWebAppTemplate()  # Alias
        }
        self.apps_dir = Path("apps")
        self.apps_dir.mkdir(parents=True, exist_ok=True)
        self.ai_team = FixItFredAITeam()
    
    def list_templates(self):
        """List available FixItFred templates"""
        print("🔧 FixItFred App Templates:")
        print("=" * 60)
        for name, template in self.templates.items():
            print(f"🤖 {name:15} - {template.description}")
        print()
    
    async def ai_suggest_template(self, app_description: str):
        """Use AI to suggest the best template"""
        try:
            prompt = f"""
            Based on this app description: "{app_description}"
            
            Recommend the best FixItFred template from these options:
            - microservice: For AI-powered backend services
            - webapp: For web applications with AI dashboards
            
            Explain your recommendation and suggest specific features to include.
            """
            
            responses = await self.ai_team.collaborate_with_ai_team(prompt)
            best_response = max(responses.values(), key=lambda x: x.confidence)
            
            return {
                "recommendation": best_response.content,
                "confidence": best_response.confidence,
                "suggestions": best_response.suggestions
            }
        except Exception as e:
            print(f"⚠️  AI suggestion failed: {e}")
            return None
    
    async def interactive_create(self):
        """AI-enhanced interactive app creation"""
        print("🤖 FixItFred AI Development Platform - Enhanced App Generator")
        print("=" * 70)
        
        # Get app description for AI suggestions
        app_description = input("📝 Describe your app: ").strip()
        if app_description:
            print("🤖 Getting AI recommendations...")
            ai_suggestion = await self.ai_suggest_template(app_description)
            if ai_suggestion:
                print(f"\n🧠 AI Recommendation (confidence: {ai_suggestion['confidence']:.2f}):")
                print(f"   {ai_suggestion['recommendation']}")
                print()
        
        # List templates
        self.list_templates()
        
        # Get template choice
        template_name = input("Choose a template: ").strip().lower()
        if template_name not in self.templates:
            print(f"❌ Invalid template: {template_name}")
            return False
        
        template = self.templates[template_name]
        print(f"\n🔧 Creating {template.name}")
        print(f"Description: {template.description}")
        print()
        
        # Get app name
        app_name = input("App name: ").strip()
        if not app_name:
            print("❌ App name is required")
            return False
        
        # Collect variables
        variables = {"app_description": app_description} if app_description else {}
        
        for var_name, var_info in template.variables.items():
            if var_name == "app_description" and app_description:
                variables[var_name] = app_description
                continue
                
            prompt = f"{var_info['description']}"
            if var_info["default"] is not None:
                prompt += f" [{var_info['default']}]"
            prompt += ": "
            
            value = input(prompt).strip()
            
            if not value and var_info["default"] is not None:
                value = var_info["default"]
            elif not value and var_info["required"]:
                print(f"❌ {var_name} is required")
                return False
            
            # Type conversion
            if isinstance(var_info["default"], bool):
                value = value.lower() in ['true', 'yes', 'y', '1']
            elif isinstance(var_info["default"], int):
                try:
                    value = int(value)
                except ValueError:
                    print(f"❌ {var_name} must be a number")
                    return False
            
            variables[var_name] = value
        
        # Generate the app with AI enhancements
        print(f"\n🔨 Generating {template.name}: {app_name}")
        await template.generate_app(app_name, self.apps_dir, variables)
        
        # Show next steps
        print(f"\n🎉 App '{app_name}' created successfully!")
        print("\n📋 Next steps:")
        print(f"1. cd apps/{app_name}")
        print("2. pip install -r requirements.txt")
        print("3. python main.py")
        print("4. Visit http://localhost:{port} to see your app")
        print(f"\n📚 Documentation: apps/{app_name}/README.md")
        print(f"🤖 AI Enhancements: apps/{app_name}/AI_ENHANCEMENTS.md")
        
        return True

async def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="FixItFred AI App Generator")
    parser.add_argument("command", choices=["create", "list", "info"], help="Command to execute")
    parser.add_argument("--template", "-t", help="Template name")
    parser.add_argument("--name", "-n", help="App name")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    
    args = parser.parse_args()
    
    generator = FixItFredAppGenerator()
    
    if args.command == "list":
        generator.list_templates()
    elif args.command == "create":
        if args.interactive or not args.template or not args.name:
            await generator.interactive_create()
        else:
            # Non-interactive creation would go here
            print("Non-interactive mode not yet implemented. Use --interactive flag.")

if __name__ == "__main__":
    asyncio.run(main())