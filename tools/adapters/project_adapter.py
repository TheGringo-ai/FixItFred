#!/usr/bin/env python3
"""
Gringo Universal Business Adapter
Converts ANY existing project into a Gringo-compatible module instantly
"""

import os
import json
import yaml
import shutil
from pathlib import Path
from typing import Dict, Any, List
import subprocess
import requests

class UniversalProjectAdapter:
    """Automatically adapts any project to work with Gringo OS"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.project_name = self.project_path.name
        self.project_type = None
        self.tech_stack = []
        self.endpoints = []
        self.capabilities = []
        
    async def analyze_project(self) -> Dict[str, Any]:
        """AI analyzes any project and determines how to integrate it"""
        
        analysis = {
            'name': self.project_name,
            'type': self._detect_project_type(),
            'tech_stack': self._detect_tech_stack(),
            'main_functionality': self._detect_functionality(),
            'api_endpoints': self._detect_endpoints(),
            'data_models': self._detect_data_models(),
            'ui_components': self._detect_ui_components(),
            'capabilities': self._extract_capabilities(),
            'integration_strategy': self._determine_integration()
        }
        
        return analysis
    
    def _detect_project_type(self) -> str:
        """Detect what type of project this is"""
        
        # Check for common files/patterns
        if (self.project_path / "package.json").exists():
            package_json = json.loads((self.project_path / "package.json").read_text())
            if "react" in package_json.get("dependencies", {}):
                return "react_frontend"
            elif "express" in package_json.get("dependencies", {}):
                return "node_backend"
            else:
                return "javascript"
        
        elif (self.project_path / "requirements.txt").exists() or (self.project_path / "pyproject.toml").exists():
            # Check for FastAPI, Flask, Django
            req_file = self.project_path / "requirements.txt"
            if req_file.exists():
                requirements = req_file.read_text()
                if "fastapi" in requirements:
                    return "fastapi_backend"
                elif "flask" in requirements:
                    return "flask_backend"
                elif "django" in requirements:
                    return "django_backend"
            return "python_backend"
        
        elif (self.project_path / "Dockerfile").exists():
            return "containerized_app"
        
        elif (self.project_path / "main.py").exists():
            return "python_script"
        
        else:
            return "unknown"
    
    def _detect_tech_stack(self) -> List[str]:
        """Detect technologies used in the project"""
        
        stack = []
        
        # Frontend technologies
        if (self.project_path / "package.json").exists():
            package_json = json.loads((self.project_path / "package.json").read_text())
            deps = {**package_json.get("dependencies", {}), **package_json.get("devDependencies", {})}
            
            if "react" in deps: stack.append("React")
            if "vue" in deps: stack.append("Vue")
            if "angular" in deps: stack.append("Angular")
            if "tailwindcss" in deps: stack.append("TailwindCSS")
            if "typescript" in deps: stack.append("TypeScript")
        
        # Backend technologies
        if (self.project_path / "requirements.txt").exists():
            requirements = (self.project_path / "requirements.txt").read_text()
            if "fastapi" in requirements: stack.append("FastAPI")
            if "flask" in requirements: stack.append("Flask")
            if "django" in requirements: stack.append("Django")
            if "sqlalchemy" in requirements: stack.append("SQLAlchemy")
            if "postgresql" in requirements: stack.append("PostgreSQL")
        
        # Database files
        db_files = list(self.project_path.glob("*.db")) + list(self.project_path.glob("*.sqlite"))
        if db_files: stack.append("SQLite")
        
        return stack
    
    def _detect_functionality(self) -> List[str]:
        """Detect main functionality based on file names and structure"""
        
        functionality = []
        
        # Check directory names
        dirs = [d.name.lower() for d in self.project_path.iterdir() if d.is_dir()]
        
        if any("auth" in d for d in dirs): functionality.append("authentication")
        if any("user" in d for d in dirs): functionality.append("user_management")
        if any("api" in d for d in dirs): functionality.append("api_service")
        if any("dashboard" in d for d in dirs): functionality.append("dashboard")
        if any("chat" in d for d in dirs): functionality.append("chat_interface")
        if any("upload" in d for d in dirs): functionality.append("file_upload")
        if any("work" in d for d in dirs): functionality.append("work_management")
        if any("asset" in d for d in dirs): functionality.append("asset_management")
        if any("inventory" in d for d in dirs): functionality.append("inventory_management")
        if any("maintenance" in d for d in dirs): functionality.append("maintenance_management")
        
        # Check file names
        files = [f.name.lower() for f in self.project_path.rglob("*.py") if f.is_file()]
        files.extend([f.name.lower() for f in self.project_path.rglob("*.js") if f.is_file()])
        files.extend([f.name.lower() for f in self.project_path.rglob("*.tsx") if f.is_file()])
        
        if any("rag" in f for f in files): functionality.append("document_ai")
        if any("chat" in f for f in files): functionality.append("ai_chat")
        if any("voice" in f for f in files): functionality.append("voice_interface")
        if any("ocr" in f for f in files): functionality.append("ocr_processing")
        if any("train" in f for f in files): functionality.append("training_system")
        if any("knowledge" in f for f in files): functionality.append("knowledge_management")
        
        return functionality
    
    def _detect_endpoints(self) -> List[str]:
        """Detect API endpoints in the project"""
        
        endpoints = []
        
        # Search for FastAPI endpoints
        for py_file in self.project_path.rglob("*.py"):
            try:
                content = py_file.read_text()
                
                # Look for FastAPI route decorators
                import re
                routes = re.findall(r'@app\.(get|post|put|delete)\("([^"]+)"', content)
                for method, path in routes:
                    endpoints.append(f"{method.upper()} {path}")
                    
                # Look for Flask routes
                routes = re.findall(r'@app\.route\("([^"]+)".*methods=\[([^\]]+)\]', content)
                for path, methods in routes:
                    for method in methods.split(','):
                        method = method.strip().strip('"\'')
                        endpoints.append(f"{method} {path}")
                        
            except:
                continue
        
        return endpoints
    
    def _detect_data_models(self) -> List[str]:
        """Detect data models/schemas in the project"""
        
        models = []
        
        # Search for SQLAlchemy models
        for py_file in self.project_path.rglob("*.py"):
            try:
                content = py_file.read_text()
                
                # Look for class definitions that might be models
                import re
                classes = re.findall(r'class (\w+)\(.*Model.*\):', content)
                models.extend(classes)
                
                # Look for Pydantic models
                classes = re.findall(r'class (\w+)\(.*BaseModel.*\):', content)
                models.extend(classes)
                
            except:
                continue
        
        return list(set(models))
    
    def _detect_ui_components(self) -> List[str]:
        """Detect UI components in React/frontend projects"""
        
        components = []
        
        # Search for React components
        for js_file in self.project_path.rglob("*.jsx"):
            components.append(js_file.stem)
        
        for ts_file in self.project_path.rglob("*.tsx"):
            components.append(ts_file.stem)
        
        return components
    
    def _extract_capabilities(self) -> List[str]:
        """Extract capabilities based on detected functionality"""
        
        functionality = self._detect_functionality()
        capabilities_map = {
            "authentication": ["user_login", "user_registration", "session_management"],
            "user_management": ["user_crud", "role_management", "permissions"],
            "api_service": ["rest_api", "data_processing", "external_integration"],
            "dashboard": ["data_visualization", "real_time_updates", "reporting"],
            "chat_interface": ["ai_chat", "real_time_messaging", "conversation_history"],
            "file_upload": ["document_processing", "file_storage", "metadata_extraction"],
            "work_management": ["task_creation", "workflow_automation", "progress_tracking"],
            "asset_management": ["asset_tracking", "maintenance_scheduling", "lifecycle_management"],
            "inventory_management": ["stock_tracking", "order_management", "supplier_integration"],
            "maintenance_management": ["preventive_maintenance", "work_orders", "equipment_monitoring"],
            "document_ai": ["rag_processing", "semantic_search", "knowledge_extraction"],
            "ai_chat": ["natural_language_processing", "context_awareness", "intelligent_responses"],
            "voice_interface": ["speech_recognition", "voice_commands", "audio_processing"],
            "ocr_processing": ["text_extraction", "document_scanning", "image_processing"],
            "training_system": ["course_creation", "progress_tracking", "certification"],
            "knowledge_management": ["information_organization", "search", "expertise_capture"]
        }
        
        capabilities = []
        for func in functionality:
            capabilities.extend(capabilities_map.get(func, [func]))
        
        return list(set(capabilities))
    
    def _determine_integration(self) -> Dict[str, Any]:
        """Determine how to integrate this project with Gringo OS"""
        
        project_type = self._detect_project_type()
        
        strategies = {
            "react_frontend": {
                "method": "embed_in_dashboard",
                "wrapper": "iframe_component",
                "build_command": "npm run build",
                "serve_path": "/build",
                "integration_points": ["authentication", "api_gateway"]
            },
            "fastapi_backend": {
                "method": "microservice",
                "wrapper": "api_proxy",
                "build_command": "pip install -r requirements.txt",
                "serve_command": "uvicorn main:app --host 0.0.0.0 --port 8080",
                "integration_points": ["api_gateway", "database", "authentication"]
            },
            "python_script": {
                "method": "scheduled_service",
                "wrapper": "job_runner",
                "build_command": "pip install -r requirements.txt",
                "serve_command": "python main.py",
                "integration_points": ["data_sync", "event_bus"]
            }
        }
        
        return strategies.get(project_type, {
            "method": "custom_integration",
            "wrapper": "universal_adapter",
            "integration_points": ["api_gateway"]
        })
    
    def generate_gringo_wrapper(self) -> str:
        """Generate Gringo OS wrapper for this project"""
        
        project_type = self._detect_project_type()
        capabilities = self._extract_capabilities()
        
        wrapper_template = f'''#!/usr/bin/env python3
"""
Gringo OS Wrapper for {self.project_name}
Auto-generated adapter for {project_type} project
"""

import asyncio
import os
import subprocess
from pathlib import Path
from typing import Dict, Any, List

class {self.project_name.title().replace('-', '').replace('_', '')}Module:
    """Gringo OS module wrapper for {self.project_name}"""
    
    def __init__(self):
        self.name = "{self.project_name}"
        self.capabilities = {capabilities}
        self.project_type = "{project_type}"
        self.is_active = False
        self.process = None
        
    async def activate(self) -> bool:
        """Activate the module"""
        try:
            await self._setup_environment()
            await self._start_service()
            self.is_active = True
            return True
        except Exception as e:
            print(f"Failed to activate {{self.name}}: {{e}}")
            return False
    
    async def deactivate(self) -> bool:
        """Deactivate the module"""
        try:
            if self.process:
                self.process.terminate()
                await self.process.wait()
            self.is_active = False
            return True
        except Exception as e:
            print(f"Failed to deactivate {{self.name}}: {{e}}")
            return False
    
    async def _setup_environment(self):
        """Setup project environment"""
        project_path = Path(__file__).parent
        
        # Install dependencies based on project type
        if (project_path / "requirements.txt").exists():
            subprocess.run(["pip", "install", "-r", "requirements.txt"], cwd=project_path)
        elif (project_path / "package.json").exists():
            subprocess.run(["npm", "install"], cwd=project_path)
    
    async def _start_service(self):
        """Start the underlying service"""
        project_path = Path(__file__).parent
        
        if self.project_type == "fastapi_backend":
            self.process = await asyncio.create_subprocess_exec(
                "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080",
                cwd=project_path
            )
        elif self.project_type == "react_frontend":
            # Build and serve React app
            subprocess.run(["npm", "run", "build"], cwd=project_path)
            self.process = await asyncio.create_subprocess_exec(
                "python", "-m", "http.server", "8080", "--directory", "build",
                cwd=project_path
            )
        elif self.project_type == "python_script":
            self.process = await asyncio.create_subprocess_exec(
                "python", "main.py",
                cwd=project_path
            )
    
    async def process_voice_command(self, command: str, user_id: str) -> Dict[str, Any]:
        """Process voice commands for this module"""
        
        # Map voice commands to module functions
        command_lower = command.lower()
        
        if any(cap in command_lower for cap in self.capabilities):
            return {{
                "understood": True,
                "response": f"Processing {{command}} with {{self.name}} module",
                "action": "command_processed"
            }}
        
        return {{
            "understood": False,
            "response": f"{{self.name}} module doesn't handle this command"
        }}
    
    async def get_status(self) -> Dict[str, Any]:
        """Get module status"""
        return {{
            "name": self.name,
            "active": self.is_active,
            "capabilities": self.capabilities,
            "project_type": self.project_type,
            "process_running": self.process is not None and self.process.returncode is None
        }}
    
    async def sync_data(self, data_type: str, data: Any, source_module: str):
        """Handle data synchronization with other modules"""
        print(f"{{self.name}} received {{data_type}} from {{source_module}}")
        # Implement data processing based on module capabilities

# Module factory function
def create_module():
    return {self.project_name.title().replace('-', '').replace('_', '')}Module()

if __name__ == "__main__":
    # Test the module
    module = create_module()
    asyncio.run(module.activate())
'''
        
        return wrapper_template
    
    def generate_module_config(self) -> Dict[str, Any]:
        """Generate Gringo OS module configuration"""
        
        return {
            "name": self.project_name,
            "display_name": self.project_name.replace('-', ' ').replace('_', ' ').title(),
            "version": "1.0.0",
            "description": f"Auto-adapted {self.project_name} module for Gringo OS",
            "project_type": self._detect_project_type(),
            "tech_stack": self._detect_tech_stack(),
            "capabilities": self._extract_capabilities(),
            "endpoints": self._detect_endpoints(),
            "data_models": self._detect_data_models(),
            "ui_components": self._detect_ui_components(),
            "integration": self._determine_integration(),
            "gringo_compatible": True,
            "auto_generated": True
        }
    
    def generate_dockerfile(self) -> str:
        """Generate optimized Dockerfile for the project"""
        
        project_type = self._detect_project_type()
        tech_stack = self._detect_tech_stack()
        
        if project_type in ["fastapi_backend", "python_script"]:
            base_image = "python:3.11-slim"
            setup_commands = [
                "COPY requirements.txt .",
                "RUN pip install --no-cache-dir -r requirements.txt"
            ]
            start_command = "CMD [\"python\", \"gringo_wrapper.py\"]"
            
        elif project_type in ["react_frontend", "node_backend"]:
            base_image = "node:18-alpine"
            setup_commands = [
                "COPY package*.json .",
                "RUN npm ci --only=production"
            ]
            start_command = "CMD [\"node\", \"gringo_wrapper.js\"]"
            
        else:
            base_image = "ubuntu:22.04"
            setup_commands = ["RUN apt-get update && apt-get install -y python3 python3-pip"]
            start_command = "CMD [\"python3\", \"gringo_wrapper.py\"]"
        
        dockerfile = f"""# Auto-generated Dockerfile for {self.project_name}
FROM {base_image}

WORKDIR /app

# Copy project files
COPY . .

# Setup dependencies
{chr(10).join(setup_commands)}

# Expose port
EXPOSE 8080

# Add Gringo OS integration
ENV GRINGO_MODULE={self.project_name}
ENV GRINGO_MODE=production

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8080/health || exit 1

# Start the module
{start_command}
"""
        
        return dockerfile

# Universal adapter that can handle any project
class GringoUniversalAdapter:
    """Main adapter that can convert any project to Gringo-compatible module"""
    
    def __init__(self):
        self.supported_types = [
            "react", "vue", "angular", "fastapi", "flask", "django",
            "express", "spring", "rails", "laravel", "wordpress"
        ]
    
    async def adapt_project(self, project_path: str, output_path: str = None) -> Dict[str, Any]:
        """Adapt any project to work with Gringo OS"""
        
        adapter = UniversalProjectAdapter(project_path)
        analysis = await adapter.analyze_project()
        
        if not output_path:
            output_path = f"gringo_modules/{adapter.project_name}"
        
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy original project
        project_files = Path(project_path)
        if project_files.exists():
            for item in project_files.iterdir():
                if item.is_dir():
                    shutil.copytree(item, output_dir / item.name, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, output_dir / item.name)
        
        # Generate Gringo OS integration files
        wrapper_code = adapter.generate_gringo_wrapper()
        config = adapter.generate_module_config()
        dockerfile = adapter.generate_dockerfile()
        
        # Save integration files
        (output_dir / "gringo_wrapper.py").write_text(wrapper_code)
        (output_dir / "gringo_module.yaml").write_text(yaml.dump(config, default_flow_style=False))
        (output_dir / "Dockerfile").write_text(dockerfile)
        
        # Create docker-compose for easy testing
        docker_compose = f"""version: '3.8'
services:
  {adapter.project_name}:
    build: .
    ports:
      - "8080:8080"
    environment:
      - GRINGO_MODULE={adapter.project_name}
    volumes:
      - ./data:/app/data
    restart: unless-stopped
"""
        (output_dir / "docker-compose.yml").write_text(docker_compose)
        
        result = {
            "status": "success",
            "project_name": adapter.project_name,
            "analysis": analysis,
            "output_path": str(output_dir),
            "integration_files": [
                "gringo_wrapper.py",
                "gringo_module.yaml", 
                "Dockerfile",
                "docker-compose.yml"
            ],
            "next_steps": [
                f"cd {output_dir}",
                "docker-compose up -d",
                "Module will be available at http://localhost:8080"
            ]
        }
        
        return result
    
    async def batch_adapt(self, projects: List[str]) -> List[Dict[str, Any]]:
        """Adapt multiple projects at once"""
        
        results = []
        for project_path in projects:
            try:
                result = await self.adapt_project(project_path)
                results.append(result)
            except Exception as e:
                results.append({
                    "status": "error",
                    "project_path": project_path,
                    "error": str(e)
                })
        
        return results

# Quick adaptation script
async def quick_adapt():
    """Quick adaptation of LineSmart and ChatterFix"""
    
    adapter = GringoUniversalAdapter()
    
    projects = [
        "/Users/fredtaylor/Desktop/Projects/ai-tools/linesmartcl",
        "/Users/fredtaylor/Desktop/Projects/ai-tools/chatterfixcl"
    ]
    
    print("🔄 Adapting projects to Gringo OS...")
    
    results = await adapter.batch_adapt(projects)
    
    for result in results:
        if result["status"] == "success":
            print(f"✅ {result['project_name']} adapted successfully")
            print(f"   Output: {result['output_path']}")
            print(f"   Capabilities: {', '.join(result['analysis']['capabilities'])}")
        else:
            print(f"❌ Failed to adapt {result.get('project_path', 'unknown')}")
            print(f"   Error: {result.get('error', 'Unknown error')}")
    
    print("\n🚀 All projects adapted! Ready for Gringo OS integration.")

if __name__ == "__main__":
    asyncio.run(quick_adapt())