#!/usr/bin/env python3
"""
FixItFred AI Development API
Enhanced development automation with AI team integration

This API provides development automation features powered by the AI team:
- Code generation and optimization
- Bug diagnosis and fixing
- Development workflow automation
- AI-powered troubleshooting
- Deployment automation
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import logging
import os
from typing import Optional, Dict, Any, List
from datetime import datetime
import json

# Import our AI team integration
from core.ai_brain.ai_team_integration import FixItFredAITeam, diagnose_problem, generate_fix

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="FixItFred AI Development API",
    description="AI-powered development automation for FixItFred",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI team for development tasks
ai_dev_team = FixItFredAITeam()

# Pydantic models
class CodeRequest(BaseModel):
    description: str
    language: str = "python"
    framework: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class BugReport(BaseModel):
    title: str
    description: str
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    reproduction_steps: Optional[List[str]] = None
    environment: Optional[Dict[str, str]] = None

class DeploymentRequest(BaseModel):
    service_name: str
    environment: str = "staging"
    config: Optional[Dict[str, Any]] = None

class OptimizationRequest(BaseModel):
    code: str
    language: str = "python"
    optimization_goals: List[str] = ["performance", "readability"]

@app.get("/", response_class=HTMLResponse)
async def development_dashboard():
    """FixItFred AI Development Dashboard"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>FixItFred AI Development Dashboard</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            color: white; min-height: 100vh; padding: 1rem;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 2rem; }
        .header h1 { font-size: 2.5rem; margin-bottom: 0.5rem; }
        .header p { opacity: 0.9; font-size: 1.1rem; }
        .dashboard-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 1.5rem; }
        .dev-card { 
            background: rgba(255,255,255,0.1); backdrop-filter: blur(10px);
            border-radius: 15px; padding: 1.5rem; border: 1px solid rgba(255,255,255,0.2);
            transition: transform 0.2s ease;
        }
        .dev-card:hover { transform: translateY(-5px); }
        .dev-card h3 { 
            margin-bottom: 1rem; color: #00f5ff; display: flex; align-items: center; gap: 0.5rem;
            font-size: 1.3rem;
        }
        .input-group { margin-bottom: 1rem; }
        .input-group label { display: block; margin-bottom: 0.5rem; font-weight: 600; }
        .input-group input, .input-group textarea, .input-group select { 
            width: 100%; padding: 0.75rem; border-radius: 8px; border: none;
            background: rgba(255,255,255,0.9); color: #333; font-size: 0.9rem;
        }
        .input-group textarea { min-height: 100px; resize: vertical; }
        .btn { 
            background: linear-gradient(45deg, #00f5ff, #ff6b6b); border: none; 
            padding: 0.75rem 1.5rem; border-radius: 8px; color: white; 
            font-weight: 600; cursor: pointer; transition: all 0.2s;
            display: inline-flex; align-items: center; gap: 0.5rem;
        }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.3); }
        .btn:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
        .response-area { 
            margin-top: 1rem; padding: 1rem; background: rgba(0,0,0,0.3); 
            border-radius: 8px; min-height: 150px; max-height: 400px; overflow-y: auto;
            font-family: monospace; font-size: 0.9rem; line-height: 1.4;
        }
        .ai-response { 
            margin-bottom: 1rem; padding: 0.75rem; background: rgba(255,255,255,0.1); 
            border-radius: 8px; border-left: 3px solid #00f5ff;
        }
        .ai-name { font-weight: 600; color: #00f5ff; margin-bottom: 0.5rem; }
        .confidence { font-size: 0.8rem; opacity: 0.8; margin-top: 0.5rem; }
        .status-badge { 
            display: inline-block; padding: 0.25rem 0.5rem; border-radius: 12px; 
            font-size: 0.8rem; font-weight: 600; margin-left: 0.5rem;
        }
        .status-success { background: rgba(76, 175, 80, 0.8); }
        .status-warning { background: rgba(255, 152, 0, 0.8); }
        .status-error { background: rgba(244, 67, 54, 0.8); }
        .loading { 
            display: inline-block; animation: spin 1s linear infinite; 
        }
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        .code-block { 
            background: rgba(0,0,0,0.5); padding: 1rem; border-radius: 8px; 
            margin: 0.5rem 0; overflow-x: auto; border-left: 3px solid #00f5ff;
        }
        .fix-steps { 
            background: rgba(76, 175, 80, 0.2); padding: 1rem; border-radius: 8px;
            margin: 0.5rem 0; border-left: 3px solid #4caf50;
        }
        .fix-steps ol { margin-left: 1.5rem; }
        .fix-steps li { margin-bottom: 0.5rem; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔧 FixItFred AI Development Dashboard</h1>
                <p>Powered by Claude + Grok AI Team for Faster Development</p>
            </div>
            
            <div class="dashboard-grid">
                <!-- Code Generation -->
                <div class="dev-card">
                    <h3>💻 AI Code Generation</h3>
                    <div class="input-group">
                        <label>Describe what you want to build:</label>
                        <textarea id="codeDesc" placeholder="Create a REST API endpoint for user authentication with JWT tokens..."></textarea>
                    </div>
                    <div class="input-group">
                        <label>Language:</label>
                        <select id="codeLang">
                            <option value="python">Python</option>
                            <option value="javascript">JavaScript</option>
                            <option value="typescript">TypeScript</option>
                            <option value="go">Go</option>
                            <option value="rust">Rust</option>
                        </select>
                    </div>
                    <div class="input-group">
                        <label>Framework (optional):</label>
                        <input type="text" id="codeFramework" placeholder="FastAPI, React, Express, etc.">
                    </div>
                    <button class="btn" onclick="generateCode()">🚀 Generate Code</button>
                    <div id="codeResponse" class="response-area">AI-generated code will appear here...</div>
                </div>
                
                <!-- Bug Diagnosis & Fix -->
                <div class="dev-card">
                    <h3>🐛 AI Bug Diagnosis & Fix</h3>
                    <div class="input-group">
                        <label>Bug Title:</label>
                        <input type="text" id="bugTitle" placeholder="Application crashes on startup">
                    </div>
                    <div class="input-group">
                        <label>Bug Description:</label>
                        <textarea id="bugDesc" placeholder="Describe the bug, when it occurs, and what you expect to happen..."></textarea>
                    </div>
                    <div class="input-group">
                        <label>Error Message (optional):</label>
                        <textarea id="bugError" placeholder="Paste any error messages or stack traces here..."></textarea>
                    </div>
                    <button class="btn" onclick="diagnoseBug()">🔍 Diagnose & Fix</button>
                    <div id="bugResponse" class="response-area">AI diagnosis and fix suggestions will appear here...</div>
                </div>
                
                <!-- Code Optimization -->
                <div class="dev-card">
                    <h3>⚡ AI Code Optimization</h3>
                    <div class="input-group">
                        <label>Code to Optimize:</label>
                        <textarea id="optimizeCode" placeholder="Paste your code here that needs optimization..."></textarea>
                    </div>
                    <div class="input-group">
                        <label>Optimization Goals:</label>
                        <select id="optimizeGoals" multiple>
                            <option value="performance">Performance</option>
                            <option value="readability">Readability</option>
                            <option value="memory">Memory Usage</option>
                            <option value="security">Security</option>
                        </select>
                    </div>
                    <button class="btn" onclick="optimizeCode()">⚡ Optimize Code</button>
                    <div id="optimizeResponse" class="response-area">Optimized code and suggestions will appear here...</div>
                </div>
                
                <!-- Deployment Automation -->
                <div class="dev-card">
                    <h3>🚀 AI Deployment Automation</h3>
                    <div class="input-group">
                        <label>Service Name:</label>
                        <input type="text" id="deployService" placeholder="fixitfred-api">
                    </div>
                    <div class="input-group">
                        <label>Environment:</label>
                        <select id="deployEnv">
                            <option value="development">Development</option>
                            <option value="staging">Staging</option>
                            <option value="production">Production</option>
                        </select>
                    </div>
                    <button class="btn" onclick="automate Deployment()">🚀 Automate Deployment</button>
                    <div id="deployResponse" class="response-area">Deployment automation steps will appear here...</div>
                </div>
                
                <!-- AI Team Status -->
                <div class="dev-card">
                    <h3>📊 AI Development Team Status</h3>
                    <button class="btn" onclick="getDevTeamStatus()">📊 Check Team Status</button>
                    <div id="statusResponse" class="response-area">
                        <div>Click "Check Team Status" to see available AI developers...</div>
                    </div>
                </div>
                
                <!-- Quick AI Consultation -->
                <div class="dev-card">
                    <h3>❓ Quick AI Dev Consultation</h3>
                    <div class="input-group">
                        <label>Development Question:</label>
                        <input type="text" id="quickQuestion" placeholder="What's the best way to implement real-time notifications?">
                    </div>
                    <button class="btn" onclick="askDevTeam()">❓ Ask AI Team</button>
                    <div id="quickResponse" class="response-area">AI development advice will appear here...</div>
                </div>
            </div>
        </div>
        
        <script>
        async function generateCode() {
            const desc = document.getElementById('codeDesc').value;
            const lang = document.getElementById('codeLang').value;
            const framework = document.getElementById('codeFramework').value;
            const response = document.getElementById('codeResponse');
            
            if (!desc.trim()) {
                response.innerHTML = '<div style="color: #ff6b6b;">Please describe what you want to build</div>';
                return;
            }
            
            response.innerHTML = '<div><span class="loading">🔄</span> AI team is generating code...</div>';
            
            try {
                const result = await fetch('/api/dev/generate-code', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        description: desc,
                        language: lang,
                        framework: framework || null
                    })
                });
                
                const data = await result.json();
                
                response.innerHTML = `
                    <div class="ai-response">
                        <div class="ai-name">Generated Code (${data.ai_provider})</div>
                        <div class="code-block">${data.code}</div>
                        <div class="confidence">Confidence: ${(data.confidence * 100).toFixed(1)}%</div>
                        ${data.suggestions ? `<div><strong>Suggestions:</strong><br>${data.suggestions.join('<br>')}</div>` : ''}
                    </div>
                `;
            } catch (error) {
                response.innerHTML = `<div style="color: #ff6b6b;">Error: ${error.message}</div>`;
            }
        }
        
        async function diagnoseBug() {
            const title = document.getElementById('bugTitle').value;
            const desc = document.getElementById('bugDesc').value;
            const error = document.getElementById('bugError').value;
            const response = document.getElementById('bugResponse');
            
            if (!title.trim() || !desc.trim()) {
                response.innerHTML = '<div style="color: #ff6b6b;">Please provide bug title and description</div>';
                return;
            }
            
            response.innerHTML = '<div><span class="loading">🔄</span> AI team is diagnosing the bug...</div>';
            
            try {
                const result = await fetch('/api/dev/diagnose-bug', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        title: title,
                        description: desc,
                        error_message: error || null
                    })
                });
                
                const data = await result.json();
                
                response.innerHTML = `
                    <div class="ai-response">
                        <div class="ai-name">Diagnosis (${data.ai_provider})</div>
                        <div><strong>Root Cause:</strong> ${data.diagnosis}</div>
                        <div class="fix-steps">
                            <strong>Fix Steps:</strong>
                            <ol>
                                ${data.fix_steps.map(step => `<li>${step}</li>`).join('')}
                            </ol>
                        </div>
                        <div class="confidence">Confidence: ${(data.confidence * 100).toFixed(1)}%</div>
                    </div>
                `;
            } catch (error) {
                response.innerHTML = `<div style="color: #ff6b6b;">Error: ${error.message}</div>`;
            }
        }
        
        async function optimizeCode() {
            const code = document.getElementById('optimizeCode').value;
            const goals = Array.from(document.getElementById('optimizeGoals').selectedOptions).map(o => o.value);
            const response = document.getElementById('optimizeResponse');
            
            if (!code.trim()) {
                response.innerHTML = '<div style="color: #ff6b6b;">Please provide code to optimize</div>';
                return;
            }
            
            response.innerHTML = '<div><span class="loading">🔄</span> AI team is optimizing your code...</div>';
            
            try {
                const result = await fetch('/api/dev/optimize-code', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        code: code,
                        optimization_goals: goals.length > 0 ? goals : ["performance", "readability"]
                    })
                });
                
                const data = await result.json();
                
                response.innerHTML = `
                    <div class="ai-response">
                        <div class="ai-name">Optimized Code (${data.ai_provider})</div>
                        <div class="code-block">${data.optimized_code}</div>
                        <div><strong>Improvements:</strong><br>${data.improvements.join('<br>')}</div>
                        <div class="confidence">Confidence: ${(data.confidence * 100).toFixed(1)}%</div>
                    </div>
                `;
            } catch (error) {
                response.innerHTML = `<div style="color: #ff6b6b;">Error: ${error.message}</div>`;
            }
        }
        
        async function automateDeployment() {
            const service = document.getElementById('deployService').value;
            const env = document.getElementById('deployEnv').value;
            const response = document.getElementById('deployResponse');
            
            if (!service.trim()) {
                response.innerHTML = '<div style="color: #ff6b6b;">Please provide service name</div>';
                return;
            }
            
            response.innerHTML = '<div><span class="loading">🔄</span> AI team is creating deployment automation...</div>';
            
            try {
                const result = await fetch('/api/dev/automate-deployment', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        service_name: service,
                        environment: env
                    })
                });
                
                const data = await result.json();
                
                response.innerHTML = `
                    <div class="ai-response">
                        <div class="ai-name">Deployment Automation (${data.ai_provider})</div>
                        <div class="code-block">${data.deployment_script}</div>
                        <div class="fix-steps">
                            <strong>Deployment Steps:</strong>
                            <ol>
                                ${data.steps.map(step => `<li>${step}</li>`).join('')}
                            </ol>
                        </div>
                        <div class="confidence">Confidence: ${(data.confidence * 100).toFixed(1)}%</div>
                    </div>
                `;
            } catch (error) {
                response.innerHTML = `<div style="color: #ff6b6b;">Error: ${error.message}</div>`;
            }
        }
        
        async function getDevTeamStatus() {
            const response = document.getElementById('statusResponse');
            response.innerHTML = '<div><span class="loading">🔄</span> Checking AI development team status...</div>';
            
            try {
                const result = await fetch('/api/dev/status');
                const data = await result.json();
                
                response.innerHTML = `
                    <div class="ai-response">
                        <div class="ai-name">AI Development Team Status</div>
                        <div><strong>Available AI Developers:</strong> ${data.available_providers.join(', ')}</div>
                        <div><strong>Active Dev Tasks:</strong> ${data.active_tasks}</div>
                        <div><strong>Completed Tasks:</strong> ${data.completed_tasks}</div>
                        <div><strong>Fix History:</strong> ${data.fix_history_count} fixes</div>
                        <div><strong>AI Team Uptime:</strong> <span class="status-badge status-success">Online</span></div>
                    </div>
                `;
            } catch (error) {
                response.innerHTML = `<div style="color: #ff6b6b;">Error: ${error.message}</div>`;
            }
        }
        
        async function askDevTeam() {
            const question = document.getElementById('quickQuestion').value;
            const response = document.getElementById('quickResponse');
            
            if (!question.trim()) {
                response.innerHTML = '<div style="color: #ff6b6b;">Please ask a development question</div>';
                return;
            }
            
            response.innerHTML = '<div><span class="loading">🔄</span> AI development team is consulting...</div>';
            
            try {
                const result = await fetch('/api/dev/ask', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: question})
                });
                
                const data = await result.json();
                
                let html = '';
                for (const [aiName, aiData] of Object.entries(data.responses)) {
                    html += `
                        <div class="ai-response">
                            <div class="ai-name">${aiName.toUpperCase()}</div>
                            <div>${aiData.content}</div>
                            <div class="confidence">Confidence: ${(aiData.confidence * 100).toFixed(1)}%</div>
                        </div>
                    `;
                }
                
                response.innerHTML = html;
            } catch (error) {
                response.innerHTML = `<div style="color: #ff6b6b;">Error: ${error.message}</div>`;
            }
            
            document.getElementById('quickQuestion').value = '';
        }
        
        // Allow Enter key to submit
        document.getElementById('quickQuestion').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') askDevTeam();
        });
        
        // Auto-load status on page load
        window.addEventListener('load', getDevTeamStatus);
        </script>
    </body>
    </html>
    """

@app.post("/api/dev/generate-code")
async def generate_code(request: CodeRequest):
    """Generate code using AI team"""
    try:
        prompt = f"""
        FIXITFRED CODE GENERATION REQUEST:
        
        Description: {request.description}
        Language: {request.language}
        Framework: {request.framework or 'None specified'}
        
        Generate clean, production-ready code with:
        1. Proper error handling
        2. Security best practices
        3. Clear documentation
        4. Unit test examples
        
        Provide the complete code implementation.
        """
        
        responses = await ai_dev_team.collaborate_with_ai_team(
            prompt,
            task_type="code_generation"
        )
        
        best_response = max(responses.values(), key=lambda x: x.confidence)
        
        return {
            "code": best_response.content,
            "ai_provider": best_response.provider.value,
            "confidence": best_response.confidence,
            "suggestions": best_response.suggestions,
            "language": request.language,
            "framework": request.framework
        }
    except Exception as e:
        logger.error(f"Code generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/dev/diagnose-bug")
async def diagnose_bug(bug: BugReport):
    """Diagnose and provide fix for bugs using AI team"""
    try:
        problem_desc = f"{bug.title}: {bug.description}"
        context = {
            "error_message": bug.error_message,
            "stack_trace": bug.stack_trace,
            "reproduction_steps": bug.reproduction_steps,
            "environment": bug.environment
        }
        
        diagnosis = await ai_dev_team.diagnose_with_ai_team(problem_desc, context)
        fix_plan = await ai_dev_team.generate_fix_plan(problem_desc, diagnosis)
        
        best_diagnosis = max(diagnosis.values(), key=lambda x: x.confidence)
        
        return {
            "diagnosis": best_diagnosis.content,
            "fix_steps": best_diagnosis.fix_instructions,
            "ai_provider": best_diagnosis.provider.value,
            "confidence": best_diagnosis.confidence,
            "fix_plan": fix_plan,
            "bug_id": f"bug_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }
    except Exception as e:
        logger.error(f"Bug diagnosis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/dev/optimize-code")
async def optimize_code(request: OptimizationRequest):
    """Optimize code using AI team"""
    try:
        prompt = f"""
        FIXITFRED CODE OPTIMIZATION REQUEST:
        
        Original Code:
        ```{request.language}
        {request.code}
        ```
        
        Optimization Goals: {', '.join(request.optimization_goals)}
        
        Provide:
        1. Optimized version of the code
        2. Explanation of improvements made
        3. Performance impact analysis
        4. Any additional recommendations
        """
        
        responses = await ai_dev_team.collaborate_with_ai_team(
            prompt,
            task_type="optimization"
        )
        
        best_response = max(responses.values(), key=lambda x: x.confidence)
        
        return {
            "original_code": request.code,
            "optimized_code": best_response.content,
            "improvements": best_response.suggestions,
            "ai_provider": best_response.provider.value,
            "confidence": best_response.confidence,
            "optimization_goals": request.optimization_goals
        }
    except Exception as e:
        logger.error(f"Code optimization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/dev/automate-deployment")
async def automate_deployment(request: DeploymentRequest):
    """Create deployment automation using AI team"""
    try:
        prompt = f"""
        FIXITFRED DEPLOYMENT AUTOMATION REQUEST:
        
        Service: {request.service_name}
        Environment: {request.environment}
        
        Generate:
        1. Complete deployment script
        2. Step-by-step deployment process
        3. Rollback procedures
        4. Health checks and monitoring
        5. Environment-specific configurations
        
        Focus on GCP Cloud Run deployment with proper CI/CD practices.
        """
        
        responses = await ai_dev_team.collaborate_with_ai_team(
            prompt,
            task_type="deployment"
        )
        
        best_response = max(responses.values(), key=lambda x: x.confidence)
        
        return {
            "deployment_script": best_response.content,
            "steps": best_response.fix_instructions,
            "ai_provider": best_response.provider.value,
            "confidence": best_response.confidence,
            "service_name": request.service_name,
            "environment": request.environment
        }
    except Exception as e:
        logger.error(f"Deployment automation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/dev/ask")
async def ask_dev_team(message: dict):
    """Quick consultation with AI development team"""
    try:
        responses = await ai_dev_team.collaborate_with_ai_team(
            message["message"],
            task_type="analysis"
        )
        
        return {
            "responses": {k: {
                "content": v.content,
                "confidence": v.confidence,
                "suggestions": v.suggestions
            } for k, v in responses.items()}
        }
    except Exception as e:
        logger.error(f"Ask dev team error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dev/status")
async def get_dev_team_status():
    """Get AI development team status"""
    try:
        return ai_dev_team.get_ai_team_status()
    except Exception as e:
        logger.error(f"Status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check for development API"""
    return {
        "status": "healthy",
        "service": "FixItFred AI Development API",
        "version": "1.0.0",
        "ai_team_available": len(ai_dev_team.get_available_providers()) > 0,
        "available_ai_developers": [p.value for p in ai_dev_team.get_available_providers()],
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    print("🔧 Starting FixItFred AI Development API")
    print("🤖 Claude + Grok AI Team for Development Automation")
    print("🌐 Visit http://localhost:8001 for the development dashboard")
    uvicorn.run(app, host="0.0.0.0", port=8001)