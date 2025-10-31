#!/usr/bin/env python3
"""
FixItFred AI Assistant API
Handles chat, voice commands, and platform building assistance
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Any, Optional
import asyncio
import json
import uuid
from datetime import datetime
from dataclasses import dataclass, asdict

# Import core components
from core.ai_brain.fine_tuning_engine import fine_tuning_engine
from core.modules.module_template_engine import universal_module_engine
from core.identity.ai_identity_core import ai_identity_core

router = APIRouter(prefix="/api/assistant", tags=["assistant"])

@dataclass
class ChatMessage:
    """Chat message structure"""
    id: str
    message: str
    response: str
    timestamp: datetime
    context: Dict[str, Any]
    actions: List[Dict[str, Any]] = None

class FixItFredAssistant:
    """AI Assistant for platform building and customization"""

    def __init__(self):
        self.conversation_history: Dict[str, List[ChatMessage]] = {}
        self.session_contexts: Dict[str, Dict[str, Any]] = {}

    async def process_chat_message(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process chat message and generate response with actions"""

        session_id = context.get("session_id", "default")
        user_context = context.get("user_context", {})

        # Analyze intent
        intent = await self._analyze_intent(message, user_context)

        # Generate response based on intent
        response_data = await self._generate_response(intent, message, user_context)

        # Store conversation
        chat_message = ChatMessage(
            id=str(uuid.uuid4()),
            message=message,
            response=response_data["response"],
            timestamp=datetime.now(),
            context=context,
            actions=response_data.get("actions", [])
        )

        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = []

        self.conversation_history[session_id].append(chat_message)

        return {
            "response": response_data["response"],
            "actions": response_data.get("actions", []),
            "intent": intent,
            "message_id": chat_message.id
        }
        
    async def process_chat_message(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process chat message and generate response with actions"""
        
        session_id = context.get("session_id", "default")
        user_context = context.get("user_context", {})
        
        # Analyze intent
        intent = await self._analyze_intent(message, user_context)
        
        # Generate response based on intent
        response_data = await self._generate_response(intent, message, user_context)
        
        # Store conversation
        chat_message = ChatMessage(
            id=str(uuid.uuid4()),
            message=message,
            response=response_data["response"],
            timestamp=datetime.now(),
            context=context,
            actions=response_data.get("actions", [])
        )
        
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = []
        
        self.conversation_history[session_id].append(chat_message)
        
        return {
            "response": response_data["response"],
            "actions": response_data.get("actions", []),
            "intent": intent,
            "message_id": chat_message.id
        }
    
    async def _analyze_intent(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user intent from message"""
        
        message_lower = message.lower()
        
        # Module creation intents
        if any(phrase in message_lower for phrase in ["create module", "new module", "build module"]):
            return {
                "type": "create_module",
                "confidence": 0.9,
                "parameters": await self._extract_module_parameters(message)
            }
        
        # Platform customization intents
        elif any(phrase in message_lower for phrase in ["customize", "modify", "change", "add field"]):
            return {
                "type": "customize_platform",
                "confidence": 0.8,
                "parameters": await self._extract_customization_parameters(message)
            }
        
        # LineSmart specific intents
        elif any(phrase in message_lower for phrase in ["linesmart", "training", "training platform"]):
            return {
                "type": "linesmart_assistance",
                "confidence": 0.9,
                "parameters": {"platform": "linesmart"}
            }
        
        # ChatterFix specific intents
        elif any(phrase in message_lower for phrase in ["chatterfix", "cmms", "maintenance platform", "work order"]):
            return {
                "type": "chatterfix_assistance",
                "confidence": 0.9,
                "parameters": {"platform": "chatterfix"}
            }
        
        # SAP integration intents
        elif any(phrase in message_lower for phrase in ["sap", "integration", "connect", "write-back"]):
            return {
                "type": "sap_integration",
                "confidence": 0.85,
                "parameters": await self._extract_sap_parameters(message)
            }
        
        # Voice command setup
        elif any(phrase in message_lower for phrase in ["voice", "commands", "hey fred"]):
            return {
                "type": "voice_setup",
                "confidence": 0.8,
                "parameters": {}
            }
        
        # View/list intents
        elif any(phrase in message_lower for phrase in ["show", "list", "view", "display"]):
            return {
                "type": "information_request",
                "confidence": 0.7,
                "parameters": await self._extract_view_parameters(message)
            }
        
        # AI model configuration
        elif any(phrase in message_lower for phrase in ["api key", "model", "llama", "openai", "claude"]):
            return {
                "type": "ai_model_config",
                "confidence": 0.8,
                "parameters": await self._extract_ai_model_parameters(message)
            }
        
        # General help
        else:
            return {
                "type": "general_help",
                "confidence": 0.5,
                "parameters": {}
            }
    
    async def _generate_response(self, intent: Dict[str, Any], message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate response based on intent"""

        intent_type = intent["type"]
        params = intent.get("parameters", {})

        if intent_type == "create_module":
            return await self._handle_create_module(params, message)

        elif intent_type == "customize_platform":
            return await self._handle_customize_platform(params, message)

        elif intent_type == "linesmart_assistance":
            return await self._handle_linesmart_assistance(params, message)

        elif intent_type == "chatterfix_assistance":
            return await self._handle_chatterfix_assistance(params, message)

        elif intent_type == "sap_integration":
            return await self._handle_sap_integration(params, message)

        elif intent_type == "voice_setup":
            return await self._handle_voice_setup(params, message)

        elif intent_type == "information_request":
            return await self._handle_information_request(params, message)

        elif intent_type == "ai_model_config":
            return await self._handle_ai_model_config(params, message)

        else:
            return await self._handle_general_help(message)

    async def _handle_create_module(self, params: Dict[str, Any], message: str) -> Dict[str, Any]:
        """Handle module creation requests"""
        
        # Get available templates
        templates = universal_module_engine.get_available_templates()
        
        # If specific template mentioned, create it
        template_name = params.get("template")
        if template_name and template_name in templates:
            
            # Special handling for premium modules
            if template_name == "chatterfix":
                return {
                    "response": f"""🔧 **Creating ChatterFix CMMS Premium Module**

This enterprise maintenance management system includes:

**🏭 Manufacturing Features:**
• AI-powered work order management with voice commands
• Predictive maintenance with failure analysis
• Mobile PWA for technicians (works offline)
• Real-time equipment monitoring and health scoring
• Parts inventory with demand forecasting

**🤖 AI Capabilities:**
• "Hey Fred" voice interface for hands-free operation
• Predictive failure analysis using equipment data
• Maintenance cost optimization recommendations
• Work order prioritization based on criticality

**📱 Mobile Excellence:**
• Progressive Web App (PWA) for offline operation
• Voice commands work on mobile devices
• Photo uploads and documentation
• Real-time sync when connection restored

Ready to deploy your enterprise CMMS?""",
                    "actions": [
                        {
                            "type": "create_premium_module",
                            "label": "Deploy ChatterFix CMMS",
                            "icon": "fas fa-tools",
                            "params": {
                                "template": "chatterfix",
                                "tenant": "default_tenant",
                                "premium": True,
                                "features": ["voice_interface", "predictive_maintenance", "mobile_pwa", "offline_sync"]
                            }
                        }
                    ]
                }
            
            elif template_name == "linesmart":
                return {
                    "response": f"""🎓 **Creating LineSmart Training Premium Module**

This AI-powered learning platform includes:

**📚 Content Intelligence:**
• RAG processing of your company documents (PDFs, manuals)
• AI-generated training content from existing materials
• Multi-language support (English, Spanish, French, Portuguese, German)
• Automatic content updates as documents change

**👥 Employee Development:**
• Personalized learning paths based on role and skills
• Custom employee fields (certifications, security clearance)
• Department-specific training programs
• Performance tracking and analytics

**🤖 AI Features:**
• Multiple AI model support (GPT-4, Claude-3, Gemini, Llama-2)
• Intelligent training recommendations
• Assessment automation and grading
• Knowledge extraction from documents

Ready to deploy your AI-powered training platform?""",
                    "actions": [
                        {
                            "type": "create_premium_module",
                            "label": "Deploy LineSmart Training",
                            "icon": "fas fa-graduation-cap",
                            "params": {
                                "template": "linesmart",
                                "tenant": "default_tenant",
                                "premium": True,
                                "features": ["rag_processing", "multilingual", "ai_content_generation", "personalized_learning"]
                            }
                        }
                    ]
                }
            
            else:
                return {
                    "response": f"""I'll create a {templates[template_name]} module for you! 
                    
This module will include:
• AI-powered workflows and automation
• Customizable forms and data fields
• Integration capabilities with your existing systems
• Voice command support
• Mobile-responsive interface

Would you like me to proceed with the creation?""",
                    "actions": [
                        {
                            "type": "create_module",
                            "label": f"Create {templates[template_name]}",
                            "icon": "fas fa-plus-circle",
                            "params": {
                                "template": template_name,
                                "tenant": "default_tenant",
                                "customization": {
                                    "industry": "manufacturing",
                                    "automation_preference": "high"
                                }
                            }
                        }
                    ]
                }
        
        # Otherwise show template options with premium modules highlighted
        core_templates = []
        premium_templates = []
        
        for name, desc in templates.items():
            if name in ["chatterfix", "linesmart"]:
                premium_templates.append(f"• **{name}**: {desc} ⭐ PREMIUM")
            else:
                core_templates.append(f"• **{name}**: {desc}")
        
        template_list = "\n".join(core_templates + premium_templates)
        
        return {
            "response": f"""I can create a module from these templates:

**🏗️ Core Business Modules:**
{chr(10).join(core_templates)}

**⭐ Premium Enhancement Modules:**
{chr(10).join(premium_templates)}

Which type of module would you like to create? You can also specify:
• Your industry (manufacturing, healthcare, retail, etc.)
• Company size
• Specific requirements or integrations needed

**Premium modules offer advanced AI features, specialized workflows, and enterprise integrations.**

Just say something like "Create ChatterFix for maintenance management" and I'll get started!""",
            "actions": [
                {
                    "type": "create_module",
                    "label": f"Create {templates[template]}",
                    "icon": "fas fa-plus-circle",
                    "params": {"template": template, "tenant": "default_tenant"}
                } for template in ["marketing", "sales", "hr"]
            ] + [
                {
                    "type": "create_premium_module",
                    "label": "Deploy ChatterFix CMMS ⭐",
                    "icon": "fas fa-tools",
                    "params": {"template": "chatterfix", "tenant": "default_tenant", "premium": True}
                },
                {
                    "type": "create_premium_module", 
                    "label": "Deploy LineSmart Training ⭐",
                    "icon": "fas fa-graduation-cap",
                    "params": {"template": "linesmart", "tenant": "default_tenant", "premium": True}
                }
            ]
        }
    
    async def _handle_linesmart_assistance(self, params: Dict[str, Any], message: str) -> Dict[str, Any]:
        """Handle LineSmart training platform assistance"""
        
        return {
            "response": """🎓 **Your LineSmart Training Platform** is already incredibly sophisticated!

Here's what you can customize easily:

**📚 Training Content:**
• Upload company documents (PDFs, manuals) for AI-powered training creation
• Multi-language support (English, Spanish, French, Portuguese, German)
• Industry-specific training templates

**👥 Employee Management:**
• Custom employee fields (equipment certifications, security clearance)
• Department-specific training paths
• Performance tracking and analytics

**🤖 AI Integration:**
• Multiple AI models supported (GPT-4, Claude-3, Gemini, Llama-2)
• RAG processing of your company documents
• Intelligent training recommendations

**🔧 Easy Customization:**
• Visual form builder - no coding required
• 30-second field additions
• Drag-and-drop training creation

Would you like me to show you specific customization options or help integrate LineSmart with your other FixItFred modules?""",
            "actions": [
                {
                    "type": "open_dashboard",
                    "label": "Open LineSmart Platform",
                    "icon": "fas fa-graduation-cap",
                    "params": {"url": "/dashboard/linesmart"}
                },
                {
                    "type": "customize_linesmart",
                    "label": "Customize Training Fields",
                    "icon": "fas fa-edit",
                    "params": {"action": "field_customization"}
                },
                {
                    "type": "integrate_linesmart",
                    "label": "Integrate with FixItFred",
                    "icon": "fas fa-link",
                    "params": {"action": "integration_setup"}
                }
            ]
        }
    
    async def _handle_chatterfix_assistance(self, params: Dict[str, Any], message: str) -> Dict[str, Any]:
        """Handle ChatterFix maintenance platform assistance"""
        
        return {
            "response": """🔧 **Your ChatterFix CMMS Platform** is enterprise-ready and incredibly powerful!

Here's what you can customize and deploy:

**🏭 Maintenance Management:**
• AI-powered work order creation and management
• Predictive maintenance with failure analysis
• Real-time equipment health monitoring
• Parts inventory with demand forecasting

**📱 Mobile Excellence:**
• Progressive Web App (PWA) for offline operation
• Voice commands with "Hey Fred" interface
• Photo uploads and documentation from mobile devices
• Real-time sync when connection restored

**🤖 AI Capabilities:**
• Predictive failure analysis using equipment data
• Maintenance cost optimization recommendations
• Work order prioritization based on criticality
• Voice recognition for hands-free operation

**🔧 Easy Deployment:**
• Ready-to-deploy CMMS module
• PostgreSQL database with enterprise features
• Voice interface integration
• Mobile-first design for technicians

Would you like me to deploy ChatterFix as a premium module or help integrate it with your existing FixItFred platform?""",
            "actions": [
                {
                    "type": "create_premium_module",
                    "label": "Deploy ChatterFix CMMS",
                    "icon": "fas fa-tools",
                    "params": {
                        "template": "chatterfix",
                        "tenant": "default_tenant",
                        "premium": True,
                        "features": ["voice_interface", "predictive_maintenance", "mobile_pwa", "offline_sync"]
                    }
                },
                {
                    "type": "open_dashboard",
                    "label": "Open ChatterFix Platform",
                    "icon": "fas fa-wrench",
                    "params": {"url": "/dashboard/chatterfix"}
                },
                {
                    "type": "integrate_chatterfix",
                    "label": "Integrate with FixItFred",
                    "icon": "fas fa-link",
                    "params": {"action": "integration_setup"}
                }
            ]
        }
    
    async def _handle_sap_integration(self, params: Dict[str, Any], message: str) -> Dict[str, Any]:
        """Handle SAP integration requests"""
        
        write_back_mentioned = any(phrase in message.lower() for phrase in ["write", "write-back", "post", "update"])
        
        if write_back_mentioned:
            response = """🔧 **SAP Write-Back Integration** 

I can help you set up enterprise-grade SAP write-back with:

**🛡️ Safety Controls:**
• Multi-level approval workflows
• Automatic error detection and rollback  
• Complete audit trails for compliance
• Real-time validation before SAP posting

**📊 Supported SAP Modules:**
• SAP FI (Finance) - GL entries, invoices, payments
• SAP HR (Human Resources) - employee data, time recording
• SAP MM (Materials) - purchase orders, goods receipts
• SAP PP (Production) - work orders, confirmations

**🚀 Deployment Options:**
• Start in read-only mode (zero risk)
• Add controlled write-back gradually
• Full bidirectional integration

Would you like me to start with read-only integration or set up controlled write-back with approval workflows?"""
        else:
            response = """🔗 **SAP Integration Options**

I can help you integrate with SAP in two modes:

**📖 Read-Only Integration (Recommended Start):**
• Zero risk to your SAP data
• Real-time data visualization and AI insights
• 35% productivity improvement from day 1
• Perfect for building confidence

**✍️ Write-Back Integration (Enterprise Mode):**
• Full bidirectional SAP integration
• Enterprise approval workflows
• Automatic error rollback
• Complete audit compliance

**⚡ Setup Time:** 47 seconds for read-only, 5 minutes for write-back

Which integration mode would you prefer?"""
        
        return {
            "response": response,
            "actions": [
                {
                    "type": "setup_sap_readonly",
                    "label": "Setup Read-Only SAP",
                    "icon": "fas fa-eye",
                    "params": {"mode": "read_only", "modules": ["FI", "HR", "MM"]}
                },
                {
                    "type": "setup_sap_writeback",
                    "label": "Setup Write-Back SAP",
                    "icon": "fas fa-edit",
                    "params": {"mode": "write_back", "approval_required": True}
                },
                {
                    "type": "view_sap_docs",
                    "label": "View SAP Integration Guide",
                    "icon": "fas fa-book",
                    "params": {"document": "sap_integration_guide"}
                }
            ]
        }
    
    async def _handle_information_request(self, params: Dict[str, Any], message: str) -> Dict[str, Any]:
        """Handle requests to view/list information"""
        
        if "module" in message.lower():
            return {
                "response": """📦 **Your Active Modules:**

I'll check what modules you currently have running. Here are the types available:

**🏭 Business Modules:**
• Marketing Suite - Campaign management, lead generation, analytics
• Sales Engine - Pipeline management, opportunity tracking, forecasting  
• HR Management - Employee data, recruitment, performance tracking
• Legal Management - Contract tracking, compliance monitoring
• Customer Success - Health scoring, onboarding, renewal management
• Product Management - Roadmap planning, feature tracking, analytics

**🎓 Training Platforms:**
• LineSmart - AI-powered training with RAG document processing

**🔗 Integration Modules:**
• SAP Connector - Read-only and write-back capabilities
• Universal Connector - Connect any system via API

Let me refresh the list of your currently active modules...""",
                "actions": [
                    {
                        "type": "refresh_modules",
                        "label": "Refresh Module List", 
                        "icon": "fas fa-sync-alt",
                        "params": {}
                    }
                ]
            }
        
        elif "platform" in message.lower():
            return {
                "response": """🚀 **Your FixItFred Platform Status:**

**Core Systems:**
• AI Identity Core - JWT authentication, RBAC/ABAC authorization
• Universal Module Engine - Generate business modules in 47 seconds
• Voice Command System - "Hey Fred" voice interface
• Dashboard Integration - Unified management interface

**AI Models Available:**
• Llama-3.2 (Default Local Model) - Fast, private, no API costs
• OpenAI GPT-4 - Premium responses (requires API key)
• Claude-3 - Anthropic's advanced model (requires API key)
• Google Gemini - Latest Google AI (requires API key)

**Integration Capabilities:**
• SAP (Read-only and Write-back)
• Salesforce, HubSpot, Google Workspace
• Custom APIs and webhooks
• Real-time data synchronization

Your platform is ready for enterprise deployment!""",
                "actions": [
                    {
                        "type": "open_dashboard",
                        "label": "Open Main Dashboard",
                        "icon": "fas fa-tachometer-alt", 
                        "params": {"url": "/dashboard"}
                    },
                    {
                        "type": "run_system_check",
                        "label": "Run System Health Check",
                        "icon": "fas fa-heartbeat",
                        "params": {"type": "full_system"}
                    }
                ]
            }
        
        else:
            return await self._handle_general_help(message)
    
    async def _handle_general_help(self, message: str) -> Dict[str, Any]:
        """Handle general help requests"""
        
        return {
            "response": """👋 **I'm here to help you build and customize your business platform!**

**🎯 What I can do:**
• **Create Modules**: "Create a quality management module for manufacturing"
• **Customize Platforms**: "Add equipment certification field to employee profiles"
• **Setup Integrations**: "Connect to SAP with write-back capabilities"
• **Configure Voice Commands**: "Setup 'Hey Fred' voice interface"
• **Manage AI Models**: "Configure OpenAI API key for premium responses"

**🎓 LineSmart Training:**
• Your LineSmart platform is already sophisticated with RAG AI processing
• I can help customize training content, employee fields, and workflows

**💡 Try asking me:**
• "Show me my active modules"
• "How do I customize the HR module?"
• "Setup SAP integration with approval workflows"
• "Configure voice commands for maintenance technicians"

What would you like to build or customize today?""",
            "actions": [
                {
                    "type": "show_tutorials",
                    "label": "Show Getting Started Guide",
                    "icon": "fas fa-play-circle",
                    "params": {"guide": "getting_started"}
                },
                {
                    "type": "open_examples",
                    "label": "View Example Commands",
                    "icon": "fas fa-lightbulb",
                    "params": {"type": "command_examples"}
                }
            ]
        }
    
    async def _extract_module_parameters(self, message: str) -> Dict[str, Any]:
        """Extract module creation parameters from message"""
        
        params = {}
        message_lower = message.lower()
        
        # Template detection including premium modules
        template_keywords = {
            "marketing": ["marketing", "campaign", "advertising", "promotion"],
            "sales": ["sales", "crm", "pipeline", "opportunity", "revenue"],
            "hr": ["hr", "human resources", "employee", "recruitment", "payroll"],
            "legal": ["legal", "contract", "compliance", "litigation"],
            "customer_success": ["customer success", "support", "retention", "churn"],
            "product": ["product", "roadmap", "feature", "development"],
            "chatterfix": ["chatterfix", "cmms", "maintenance", "work order", "technician", "equipment", "asset"],
            "linesmart": ["linesmart", "training", "learning", "education", "course", "skill", "certification"]
        }
        
        for template, keywords in template_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                params["template"] = template
                break
        
        # Industry detection
        if "manufacturing" in message_lower:
            params["industry"] = "manufacturing"
        elif "healthcare" in message_lower:
            params["industry"] = "healthcare"
        elif "retail" in message_lower:
            params["industry"] = "retail"
        
        return params
    
    async def _extract_customization_parameters(self, message: str) -> Dict[str, Any]:
        """Extract customization parameters from message"""
        
        params = {}
        message_lower = message.lower()
        
        if "field" in message_lower:
            params["type"] = "field_customization"
        elif "workflow" in message_lower:
            params["type"] = "workflow_customization"
        elif "form" in message_lower:
            params["type"] = "form_customization"
        
        return params
    
    async def _extract_sap_parameters(self, message: str) -> Dict[str, Any]:
        """Extract SAP integration parameters from message"""
        
        params = {}
        message_lower = message.lower()
        
        if any(phrase in message_lower for phrase in ["write", "write-back", "post"]):
            params["mode"] = "write_back"
        else:
            params["mode"] = "read_only"
        
        # Module detection
        sap_modules = []
        if "fi" in message_lower or "finance" in message_lower:
            sap_modules.append("FI")
        if "hr" in message_lower or "human" in message_lower:
            sap_modules.append("HR")
        if "mm" in message_lower or "material" in message_lower:
            sap_modules.append("MM")
        if "pp" in message_lower or "production" in message_lower:
            sap_modules.append("PP")
        
        if sap_modules:
            params["modules"] = sap_modules
        
        return params
    
    async def _extract_view_parameters(self, message: str) -> Dict[str, Any]:
        """Extract view/display parameters from message"""
        
        params = {}
        message_lower = message.lower()
        
        if "module" in message_lower:
            params["target"] = "modules"
        elif "platform" in message_lower:
            params["target"] = "platform_status"
        elif "integration" in message_lower:
            params["target"] = "integrations"
        
        return params
    
    async def _extract_ai_model_parameters(self, message: str) -> Dict[str, Any]:
        """Extract AI model configuration parameters"""
        
        params = {}
        message_lower = message.lower()
        
        if "openai" in message_lower or "gpt" in message_lower:
            params["provider"] = "openai"
        elif "claude" in message_lower:
            params["provider"] = "claude"
        elif "gemini" in message_lower:
            params["provider"] = "gemini"
        elif "llama" in message_lower:
            params["provider"] = "llama"
        
        return params
    
    async def _handle_voice_setup(self, params: Dict[str, Any], message: str) -> Dict[str, Any]:
        """Handle voice command setup"""
        
        return {
            "response": """🎤 **Voice Command Setup**

I can help you configure "Hey Fred" voice commands for your team:

**🏭 Manufacturing Voice Commands:**
• "Hey Fred, show me equipment status"
• "Hey Fred, create maintenance work order for pump P-101"
• "Hey Fred, log 3 hours on work order WO-12345"
• "Hey Fred, schedule preventive maintenance"

**📊 Analytics Voice Commands:**
• "Hey Fred, what's our OEE for line 2?"
• "Hey Fred, show me today's production metrics"
• "Hey Fred, who needs safety training?"

**🔧 Setup Requirements:**
• Microphone access in browser
• Voice recognition service (built-in)
• User training (5 minutes per person)

Voice commands work with all your modules and integrate with SAP!""",
            "actions": [
                {
                    "type": "setup_voice",
                    "label": "Enable Voice Commands",
                    "icon": "fas fa-microphone",
                    "params": {"enable_voice": True}
                },
                {
                    "type": "train_voice",
                    "label": "Voice Command Training",
                    "icon": "fas fa-graduation-cap",
                    "params": {"training_type": "voice_commands"}
                }
            ]
        }
    
    async def _handle_ai_model_config(self, params: Dict[str, Any], message: str) -> Dict[str, Any]:
        """Handle AI model configuration"""
        
        provider = params.get("provider", "general")
        
        if provider == "llama":
            response = """🦙 **Llama Model Configuration**

Llama-3.2 is your default local AI model and requires no setup:

**✅ Already Configured:**
• Fast local inference (no internet required)
• Complete privacy (data never leaves your server)
• No API costs
• Business context understanding

**🚀 Performance:**
• Response time: < 2 seconds
• Handles manufacturing, safety, and technical queries
• Supports voice commands and document processing

Llama is perfect for day-to-day operations and provides enterprise-grade AI without external dependencies!"""
        
        elif provider in ["openai", "claude", "gemini"]:
            response = f"""🔑 **{provider.title()} API Configuration**

To use {provider.title()} models, you'll need to configure your API key:

**📋 Steps:**
1. Get your API key from {provider.title()}
2. Click "Configure API Keys" in the sidebar
3. Enter your API key securely
4. Test the connection

**💡 Benefits of {provider.title()}:**
• Premium AI responses for complex queries
• Advanced reasoning capabilities  
• Specialized business knowledge
• Fallback to Llama if unavailable

**🛡️ Security:**
• API keys are encrypted and stored securely
• Only used for your requests
• Llama remains as local fallback"""
        
        else:
            response = """🤖 **AI Model Options**

**🦙 Llama-3.2 (Default - Already Active):**
• Local model, no API key needed
• Fast, private, zero cost
• Perfect for daily operations

**☁️ Premium Models (Require API Keys):**
• **OpenAI GPT-4**: Industry-leading responses
• **Claude-3**: Excellent for analysis and reasoning  
• **Google Gemini**: Latest Google AI technology

**🔄 Smart Fallback:**
• Premium models for complex queries
• Automatic fallback to Llama if needed
• Best of both worlds: speed + intelligence

Which model would you like to configure?"""
        
        return {
            "response": response,
            "actions": [
                {
                    "type": "configure_api_key",
                    "label": f"Configure {provider.title()} API Key",
                    "icon": "fas fa-key",
                    "params": {"provider": provider}
                } if provider != "llama" else {
                    "type": "test_llama",
                    "label": "Test Llama Model",
                    "icon": "fas fa-play",
                    "params": {"model": "llama-default"}
                }
            ]
        }

# Global assistant instance
assistant = FixItFredAssistant()

# API Endpoints
@router.post("/chat")
async def chat_with_assistant(request: Dict[str, Any]):
    """Chat with the AI assistant"""
    
    message = request.get("message", "")
    context = request.get("context", {})
    
    if not message:
        raise HTTPException(status_code=400, detail="Message is required")
    
    try:
        response = await assistant.process_chat_message(message, context)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Assistant error: {str(e)}")

@router.post("/intent")
async def process_voice_intent(request: Dict[str, Any]):
    """Process voice command intent"""
    
    utterance = request.get("utterance", "")
    user_context = request.get("user_context", {})
    
    if not utterance:
        raise HTTPException(status_code=400, detail="Utterance is required")
    
    try:
        # Convert voice to chat message
        context = {
            "type": "voice_command",
            "user_context": user_context
        }
        
        response = await assistant.process_chat_message(utterance, context)
        
        return {
            "understood": True,
            "intent": response["intent"],
            "response": response["response"],
            "actions": response.get("actions", [])
        }
        
    except Exception as e:
        return {
            "understood": False,
            "error": str(e),
            "response": "I'm having trouble understanding that command. Could you try rephrasing?"
        }

@router.get("/conversation/{session_id}")
async def get_conversation_history(session_id: str):
    """Get conversation history for a session"""
    
    history = assistant.conversation_history.get(session_id, [])
    
    return {
        "session_id": session_id,
        "message_count": len(history),
        "messages": [asdict(msg) for msg in history[-20:]]  # Last 20 messages
    }

@router.delete("/conversation/{session_id}")
async def clear_conversation(session_id: str):
    """Clear conversation history for a session"""
    
    if session_id in assistant.conversation_history:
        del assistant.conversation_history[session_id]
    
    return {"status": "cleared", "session_id": session_id}

@router.get("/capabilities")
async def get_assistant_capabilities():
    """Get assistant capabilities and supported intents"""
    
    return {
        "supported_intents": [
            "create_module",
            "customize_platform", 
            "linesmart_assistance",
            "chatterfix_assistance",
            "sap_integration",
            "voice_setup",
            "information_request",
            "ai_model_config",
            "general_help"
        ],
        "module_templates": universal_module_engine.get_available_templates(),
        "ai_models": {
            "default": "llama-3.2",
            "supported": ["llama-3.2", "gpt-4", "claude-3", "gemini-pro"],
            "local": ["llama-3.2"],
            "cloud": ["gpt-4", "claude-3", "gemini-pro"]
        },
        "features": [
            "voice_commands",
            "module_generation",
            "sap_integration",
            "platform_customization",
            "ai_model_configuration"
        ]
    }