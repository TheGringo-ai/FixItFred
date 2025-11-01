#!/usr/bin/env python3
"""
FixItFred Code Generation Agent
Specialized AI agent for intelligent code scaffold generation and enhancement
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from ..ai_team_integration import FixItFredAITeam
from ..development_ai_framework import DevelopmentTaskType, AgentCapability


class CodeGenerationAgent:
    """Intelligent code generation agent with AI enhancement"""

    def __init__(self, ai_team: FixItFredAITeam):
        self.ai_team = ai_team
        self.agent_id = "code_gen"
        self.name = "Code Generation Agent"
        self.specializations = [
            DevelopmentTaskType.CODE_GENERATION,
            DevelopmentTaskType.REFACTORING,
        ]
        self.primary_ai = "grok"  # Creative and innovative
        self.fallback_ai = "claude"  # Structured and safe

        # Code generation templates and patterns
        self.templates = self._load_code_templates()
        self.best_practices = self._load_best_practices()

    def _load_code_templates(self) -> Dict[str, Any]:
        """Load code generation templates"""
        return {
            "fastapi_router": {
                "template": """
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import logging

router = APIRouter(prefix="/{module_name}", tags=["{module_name}"])

class {ModelName}Request(BaseModel):
    {request_fields}

class {ModelName}Response(BaseModel):
    {response_fields}

@router.post("/", response_model={ModelName}Response)
async def create_{module_name}(request: {ModelName}Request):
    \"\"\"Create new {module_name}\"\"\"
    try:
        # Implementation logic here
        return {ModelName}Response({response_example})
    except Exception as e:
        logging.error(f"Error creating {module_name}: {{e}}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{{item_id}}", response_model={ModelName}Response)
async def get_{module_name}(item_id: str):
    \"\"\"Get {module_name} by ID\"\"\"
    try:
        # Implementation logic here
        return {ModelName}Response({response_example})
    except Exception as e:
        logging.error(f"Error getting {module_name}: {{e}}")
        raise HTTPException(status_code=500, detail=str(e))
""",
                "required_vars": [
                    "module_name",
                    "ModelName",
                    "request_fields",
                    "response_fields",
                    "response_example",
                ],
            },
            "pydantic_model": {
                "template": """
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class {ModelName}(BaseModel):
    {fields}

    class Config:
        json_encoders = {{
            datetime: lambda v: v.isoformat()
        }}

    def to_dict(self) -> Dict[str, Any]:
        \"\"\"Convert model to dictionary\"\"\"
        return self.dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> '{ModelName}':
        \"\"\"Create model from dictionary\"\"\"
        return cls(**data)
""",
                "required_vars": ["ModelName", "fields"],
            },
            "ai_integration": {
                "template": """
async def get_ai_enhanced_{function_name}(
    self,
    {parameters}
) -> Dict[str, Any]:
    \"\"\"AI-enhanced {function_description}\"\"\"

    try:
        # Prepare context for AI
        context = {{
            {context_preparation}
        }}

        # Create prompt for AI team
        prompt = f\"\"\"
        {ai_prompt_template}

        Context: {{json.dumps(context, indent=2)}}

        Please provide:
        1. Analysis of the situation
        2. Recommended actions
        3. Expected outcomes
        4. Confidence level (0.0-1.0)
        \"\"\"

        # Use AI team for analysis
        ai_response = await self.ai_team.collaborate_on_task(
            task_description=prompt,
            task_type="{task_type}",
            preferred_provider="{preferred_ai}"
        )

        # Process AI response
        result = {{
            "ai_analysis": ai_response.get("response", ""),
            "confidence": ai_response.get("confidence", 0.0),
            "ai_provider": ai_response.get("ai_provider", "unknown"),
            "timestamp": datetime.now().isoformat(),
            {result_processing}
        }}

        return result

    except Exception as e:
        logging.error(f"AI-enhanced {function_name} failed: {{e}}")
        return {{
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }}
""",
                "required_vars": [
                    "function_name",
                    "function_description",
                    "parameters",
                    "context_preparation",
                    "ai_prompt_template",
                    "task_type",
                    "preferred_ai",
                    "result_processing",
                ],
            },
        }

    def _load_best_practices(self) -> Dict[str, List[str]]:
        """Load coding best practices by category"""
        return {
            "security": [
                "Never log sensitive information",
                "Use parameterized queries to prevent SQL injection",
                "Validate all input data",
                "Use HTTPS for all API endpoints",
                "Implement proper authentication and authorization",
                "Use environment variables for secrets",
            ],
            "performance": [
                "Use async/await for I/O operations",
                "Implement proper caching strategies",
                "Use connection pooling for databases",
                "Optimize database queries",
                "Implement pagination for large data sets",
                "Use lazy loading where appropriate",
            ],
            "maintainability": [
                "Write clear, descriptive function and variable names",
                "Add comprehensive docstrings",
                "Keep functions small and focused",
                "Use type hints",
                "Implement proper error handling",
                "Write unit tests for all functions",
            ],
            "reliability": [
                "Implement proper exception handling",
                "Use circuit breakers for external services",
                "Add retry logic with exponential backoff",
                "Implement health checks",
                "Log errors with sufficient context",
                "Use proper status codes for APIs",
            ],
        }

    async def generate_code_scaffold(
        self, module_type: str, module_name: str, requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate intelligent code scaffold based on requirements"""

        try:
            # Analyze requirements using AI
            analysis_prompt = f"""
            Analyze the following code generation requirements:

            Module Type: {module_type}
            Module Name: {module_name}
            Requirements: {json.dumps(requirements, indent=2)}

            Please provide:
            1. Architecture recommendations
            2. Required components and their relationships
            3. Data models needed
            4. API endpoints design
            5. Security considerations
            6. Performance optimizations
            7. Testing strategy

            Focus on creating production-ready, scalable code that follows industry best practices.
            """

            ai_analysis = await self.ai_team.collaborate_on_task(
                task_description=analysis_prompt,
                task_type="code_generation",
                preferred_provider=self.primary_ai,
            )

            # Generate code based on analysis
            code_components = await self._generate_code_components(
                module_type, module_name, requirements, ai_analysis
            )

            # Apply best practices
            enhanced_code = await self._enhance_with_best_practices(code_components)

            # Generate tests
            test_code = await self._generate_test_suite(enhanced_code, requirements)

            return {
                "success": True,
                "ai_analysis": ai_analysis,
                "code_components": enhanced_code,
                "tests": test_code,
                "documentation": await self._generate_documentation(enhanced_code),
                "deployment_config": await self._generate_deployment_config(
                    module_name
                ),
                "confidence": ai_analysis.get("confidence", 0.8),
                "ai_provider": ai_analysis.get("ai_provider", self.primary_ai),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logging.error(f"Code generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def _generate_code_components(
        self,
        module_type: str,
        module_name: str,
        requirements: Dict[str, Any],
        ai_analysis: Dict[str, Any],
    ) -> Dict[str, str]:
        """Generate individual code components"""

        components = {}

        # Generate main module file
        if module_type == "fastapi_service":
            components["main.py"] = await self._generate_fastapi_service(
                module_name, requirements, ai_analysis
            )
            components["models.py"] = await self._generate_pydantic_models(
                module_name, requirements, ai_analysis
            )
            components["routes.py"] = await self._generate_api_routes(
                module_name, requirements, ai_analysis
            )
            components["dependencies.py"] = await self._generate_dependencies(
                module_name, requirements, ai_analysis
            )

        elif module_type == "ai_assistant":
            components[
                f"{module_name}_assistant.py"
            ] = await self._generate_ai_assistant(
                module_name, requirements, ai_analysis
            )
            components["models.py"] = await self._generate_ai_models(
                module_name, requirements, ai_analysis
            )

        # Generate common components
        components["__init__.py"] = self._generate_init_file(module_name)
        components["config.py"] = await self._generate_config_file(
            module_name, requirements
        )

        return components

    async def _generate_fastapi_service(
        self,
        module_name: str,
        requirements: Dict[str, Any],
        ai_analysis: Dict[str, Any],
    ) -> str:
        """Generate FastAPI service code"""

        prompt = f"""
        Generate a complete FastAPI service for {module_name} with the following requirements:
        {json.dumps(requirements, indent=2)}

        AI Analysis: {ai_analysis.get('response', '')}

        Include:
        1. FastAPI app initialization
        2. Middleware setup (CORS, logging, error handling)
        3. Router inclusion
        4. Health check endpoint
        5. Startup/shutdown events
        6. Error handling
        7. Security middleware
        8. API documentation setup

        Follow these best practices:
        {json.dumps(self.best_practices, indent=2)}

        Make it production-ready with proper logging, error handling, and monitoring.
        """

        ai_response = await self.ai_team.collaborate_on_task(
            task_description=prompt,
            task_type="code_generation",
            preferred_provider=self.primary_ai,
        )

        return ai_response.get("response", "# AI generation failed")

    async def _generate_pydantic_models(
        self,
        module_name: str,
        requirements: Dict[str, Any],
        ai_analysis: Dict[str, Any],
    ) -> str:
        """Generate Pydantic models"""

        prompt = f"""
        Generate comprehensive Pydantic models for {module_name} module:

        Requirements: {json.dumps(requirements, indent=2)}

        Include:
        1. Request/Response models for all endpoints
        2. Database models if needed
        3. Configuration models
        4. Enum classes for constants
        5. Validation rules and custom validators
        6. Serialization methods
        7. Type hints for all fields
        8. Documentation strings

        Focus on data validation, type safety, and clear model relationships.
        """

        ai_response = await self.ai_team.collaborate_on_task(
            task_description=prompt,
            task_type="code_generation",
            preferred_provider="claude",  # Claude is excellent for structured data modeling
        )

        return ai_response.get("response", "# Model generation failed")

    async def _enhance_with_best_practices(
        self, code_components: Dict[str, str]
    ) -> Dict[str, str]:
        """Enhance generated code with best practices"""

        enhanced_components = {}

        for filename, code in code_components.items():
            enhancement_prompt = f"""
            Review and enhance the following {filename} code with industry best practices:

            {code}

            Apply these improvements:
            1. Security: {json.dumps(self.best_practices['security'], indent=2)}
            2. Performance: {json.dumps(self.best_practices['performance'], indent=2)}
            3. Maintainability: {json.dumps(self.best_practices['maintainability'], indent=2)}
            4. Reliability: {json.dumps(self.best_practices['reliability'], indent=2)}

            Return the enhanced code with:
            - Improved error handling
            - Better logging
            - Security enhancements
            - Performance optimizations
            - Clear documentation
            - Type hints
            """

            ai_response = await self.ai_team.collaborate_on_task(
                task_description=enhancement_prompt,
                task_type="code_review",
                preferred_provider="claude",  # Claude excels at code review and enhancement
            )

            enhanced_components[filename] = ai_response.get("response", code)

        return enhanced_components

    async def _generate_test_suite(
        self, code_components: Dict[str, str], requirements: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate comprehensive test suite"""

        test_files = {}

        for filename, code in code_components.items():
            if filename.endswith(".py") and filename != "__init__.py":
                test_prompt = f"""
                Generate comprehensive tests for {filename}:

                Code to test:
                {code}

                Requirements: {json.dumps(requirements, indent=2)}

                Include:
                1. Unit tests for all functions
                2. Integration tests for API endpoints
                3. Edge case testing
                4. Error condition testing
                5. Performance tests
                6. Security tests
                7. Mock external dependencies
                8. Test data fixtures

                Use pytest framework with async support.
                Aim for 90%+ code coverage.
                """

                ai_response = await self.ai_team.collaborate_on_task(
                    task_description=test_prompt,
                    task_type="testing",
                    preferred_provider="claude",  # Claude is systematic with testing
                )

                test_filename = f"test_{filename}"
                test_files[test_filename] = ai_response.get(
                    "response", f"# Test generation failed for {filename}"
                )

        return test_files

    async def _generate_documentation(
        self, code_components: Dict[str, str]
    ) -> Dict[str, str]:
        """Generate documentation for the generated code"""

        docs = {}

        # Generate README
        readme_prompt = f"""
        Generate a comprehensive README.md for this module with:

        Code components: {list(code_components.keys())}

        Include:
        1. Project description and purpose
        2. Installation instructions
        3. Usage examples
        4. API documentation
        5. Configuration guide
        6. Development setup
        7. Testing instructions
        8. Deployment guide
        9. Contributing guidelines
        10. License information

        Make it clear, professional, and comprehensive.
        """

        ai_response = await self.ai_team.collaborate_on_task(
            task_description=readme_prompt,
            task_type="documentation",
            preferred_provider="claude",
        )

        docs["README.md"] = ai_response.get(
            "response", "# Documentation generation failed"
        )

        # Generate API docs
        docs["API.md"] = await self._generate_api_documentation(code_components)

        return docs

    async def _generate_api_documentation(self, code_components: Dict[str, str]) -> str:
        """Generate API documentation"""

        prompt = f"""
        Generate detailed API documentation based on these code components:

        {json.dumps({k: v[:500] + "..." if len(v) > 500 else v for k, v in code_components.items()}, indent=2)}

        Include:
        1. Endpoint descriptions
        2. Request/response schemas
        3. Authentication requirements
        4. Error codes and messages
        5. Usage examples with curl commands
        6. Rate limiting information
        7. Pagination details
        8. Versioning information

        Format in clear markdown with examples.
        """

        ai_response = await self.ai_team.collaborate_on_task(
            task_description=prompt,
            task_type="documentation",
            preferred_provider="claude",
        )

        return ai_response.get("response", "# API documentation generation failed")

    async def _generate_deployment_config(self, module_name: str) -> Dict[str, str]:
        """Generate deployment configuration files"""

        configs = {}

        # Docker configuration
        dockerfile_prompt = f"""
        Generate a production-ready Dockerfile for {module_name} FastAPI service:

        Requirements:
        - Python 3.11 base image
        - Multi-stage build for optimization
        - Non-root user for security
        - Health check endpoint
        - Proper caching of dependencies
        - Environment variable support
        - Minimal attack surface
        """

        ai_response = await self.ai_team.collaborate_on_task(
            task_description=dockerfile_prompt,
            task_type="deployment",
            preferred_provider="openai",
        )

        configs["Dockerfile"] = ai_response.get(
            "response", "# Dockerfile generation failed"
        )

        # Docker Compose for development
        configs["docker-compose.yml"] = self._generate_docker_compose(module_name)

        # Requirements file
        configs["requirements.txt"] = self._generate_requirements()

        return configs

    def _generate_docker_compose(self, module_name: str) -> str:
        """Generate Docker Compose configuration"""
        return f"""
version: '3.8'

services:
  {module_name}:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=development
      - LOG_LEVEL=DEBUG
    volumes:
      - .:/app
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    restart: unless-stopped

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: {module_name}
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
"""

    def _generate_requirements(self) -> str:
        """Generate requirements.txt file"""
        return """
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
redis==5.0.1
asyncpg==0.29.0
sqlalchemy==2.0.23
alembic==1.12.1
httpx==0.25.2
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
black==23.11.0
isort==5.12.0
mypy==1.7.1
"""

    def _generate_init_file(self, module_name: str) -> str:
        """Generate __init__.py file"""
        return f'''"""
{module_name.title()} Module
AI-generated module for FixItFred platform
"""

__version__ = "1.0.0"
__author__ = "FixItFred AI Team"

from .models import *

__all__ = ["__version__", "__author__"]
'''

    async def _generate_config_file(
        self, module_name: str, requirements: Dict[str, Any]
    ) -> str:
        """Generate configuration file"""

        prompt = f"""
        Generate a configuration file for {module_name} module with:

        Requirements: {json.dumps(requirements, indent=2)}

        Include:
        1. Environment-specific settings
        2. Database configuration
        3. API settings
        4. Logging configuration
        5. Security settings
        6. External service configurations
        7. Feature flags
        8. Performance tuning parameters

        Use Pydantic BaseSettings for type safety and validation.
        Support environment variables and .env files.
        """

        ai_response = await self.ai_team.collaborate_on_task(
            task_description=prompt,
            task_type="code_generation",
            preferred_provider="claude",
        )

        return ai_response.get("response", "# Configuration generation failed")

    async def refactor_code(
        self, existing_code: str, refactoring_goals: List[str]
    ) -> Dict[str, Any]:
        """Refactor existing code based on specified goals"""

        prompt = f"""
        Refactor the following code to achieve these goals:
        {', '.join(refactoring_goals)}

        Existing code:
        {existing_code}

        Apply these best practices:
        {json.dumps(self.best_practices, indent=2)}

        Provide:
        1. Refactored code
        2. Explanation of changes made
        3. Before/after comparison
        4. Performance impact analysis
        5. Testing recommendations

        Ensure the refactored code is:
        - More maintainable
        - Better performing
        - More secure
        - Easier to test
        """

        try:
            ai_response = await self.ai_team.collaborate_on_task(
                task_description=prompt,
                task_type="refactoring",
                preferred_provider=self.primary_ai,
            )

            return {
                "success": True,
                "refactored_code": ai_response.get("response", ""),
                "confidence": ai_response.get("confidence", 0.0),
                "ai_provider": ai_response.get("ai_provider", self.primary_ai),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logging.error(f"Code refactoring failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def get_agent_status(self) -> Dict[str, Any]:
        """Get current status of the code generation agent"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "specializations": [spec.value for spec in self.specializations],
            "primary_ai": self.primary_ai,
            "fallback_ai": self.fallback_ai,
            "templates_available": len(self.templates),
            "best_practices_categories": list(self.best_practices.keys()),
            "status": "ready",
        }
