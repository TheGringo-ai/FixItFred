#!/usr/bin/env python3
"""
FixItFred AI Assistant Service
Specialized OpenAI-powered assistants for different industries
"""

import os
from typing import Dict, List, Optional
from openai import AsyncOpenAI
from pydantic import BaseModel
import asyncio
import json
from datetime import datetime

class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: Optional[str] = None

class IndustryPrompts:
    """Custom prompts for different industries using OpenAI's cheapest model"""
    
    HOME_REPAIR = """You are FixItFred, an expert home repair and maintenance AI assistant. 
    You specialize in:
    - Diagnosing common household problems
    - Providing step-by-step repair instructions
    - Recommending tools and materials needed
    - Safety guidance for DIY repairs
    - When to call a professional
    
    Always be practical, safety-focused, and cost-effective in your recommendations.
    Keep responses clear and actionable."""
    
    CAR_REPAIR = """You are FixItFred Auto, an expert automotive repair AI assistant.
    You specialize in:
    - Vehicle diagnostics and troubleshooting
    - Maintenance scheduling and reminders
    - Parts identification and sourcing
    - Labor time estimates
    - Cost-effective repair strategies
    
    Always prioritize safety and provide accurate technical information."""
    
    MANUFACTURING = """You are FixItFred Manufacturing, an expert industrial AI assistant.
    You specialize in:
    - Production line optimization
    - Quality control processes
    - Equipment maintenance planning
    - Safety compliance monitoring
    - Efficiency improvements
    
    Focus on operational excellence and continuous improvement."""
    
    HEALTHCARE = """You are FixItFred Medical, a healthcare operations AI assistant.
    You specialize in:
    - Patient flow optimization
    - Compliance monitoring
    - Equipment maintenance schedules
    - Staff scheduling efficiency
    - Resource allocation
    
    Always maintain HIPAA compliance awareness and patient safety focus."""
    
    RETAIL = """You are FixItFred Retail, a retail operations AI assistant.
    You specialize in:
    - Inventory management optimization
    - Customer service improvement
    - Sales analytics and insights
    - Store operations efficiency
    - Loss prevention strategies
    
    Focus on customer satisfaction and profitability."""
    
    CONSTRUCTION = """You are FixItFred Construction, a construction project AI assistant.
    You specialize in:
    - Project planning and scheduling
    - Safety protocol compliance
    - Equipment and material management
    - Quality control inspections
    - Cost estimation and budgeting
    
    Prioritize safety, quality, and on-time delivery."""
    
    LOGISTICS = """You are FixItFred Logistics, a supply chain AI assistant.
    You specialize in:
    - Route optimization and planning
    - Fleet management efficiency
    - Warehouse operations
    - Delivery tracking and scheduling
    - Cost reduction strategies
    
    Focus on efficiency, reliability, and cost-effectiveness."""

class AIAssistantService:
    """OpenAI-powered assistant service using the most cost-effective model"""
    
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.model = "gpt-3.5-turbo"  # Most cost-effective model
        self.conversation_history: Dict[str, List[ChatMessage]] = {}
    
    def get_industry_prompt(self, industry: str) -> str:
        """Get the specialized prompt for an industry"""
        industry_upper = industry.upper().replace("-", "_")
        return getattr(IndustryPrompts, industry_upper, IndustryPrompts.HOME_REPAIR)
    
    async def chat_with_assistant(
        self, 
        industry: str, 
        user_message: str, 
        session_id: str = "default"
    ) -> Dict:
        """Chat with industry-specific AI assistant"""
        
        try:
            # Get or create conversation history
            if session_id not in self.conversation_history:
                self.conversation_history[session_id] = []
                # Add system prompt
                system_prompt = self.get_industry_prompt(industry)
                self.conversation_history[session_id].append(
                    ChatMessage(role="system", content=system_prompt)
                )
            
            # Add user message
            self.conversation_history[session_id].append(
                ChatMessage(
                    role="user", 
                    content=user_message, 
                    timestamp=datetime.now().isoformat()
                )
            )
            
            # Prepare messages for OpenAI
            messages = [
                {"role": msg.role, "content": msg.content} 
                for msg in self.conversation_history[session_id]
            ]
            
            # Call OpenAI API with cost-effective settings
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=500,  # Limit tokens to control cost
                temperature=0.7,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            
            # Extract assistant response
            assistant_message = response.choices[0].message.content
            
            # Add assistant response to history
            self.conversation_history[session_id].append(
                ChatMessage(
                    role="assistant", 
                    content=assistant_message,
                    timestamp=datetime.now().isoformat()
                )
            )
            
            # Calculate approximate cost (gpt-3.5-turbo pricing)
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            estimated_cost = (input_tokens * 0.0015 + output_tokens * 0.002) / 1000
            
            return {
                "success": True,
                "response": assistant_message,
                "industry": industry,
                "session_id": session_id,
                "tokens_used": {
                    "input": input_tokens,
                    "output": output_tokens,
                    "total": response.usage.total_tokens
                },
                "estimated_cost": round(estimated_cost, 6),
                "model": self.model,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "industry": industry,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_conversation_history(self, session_id: str) -> List[Dict]:
        """Get conversation history for a session"""
        if session_id not in self.conversation_history:
            return []
        
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp
            }
            for msg in self.conversation_history[session_id]
            if msg.role != "system"  # Don't include system prompts in history
        ]
    
    async def clear_conversation(self, session_id: str) -> bool:
        """Clear conversation history for a session"""
        if session_id in self.conversation_history:
            del self.conversation_history[session_id]
            return True
        return False
    
    def get_industry_info(self, industry: str) -> Dict:
        """Get information about an industry's AI capabilities"""
        industry_info = {
            "home-repair": {
                "name": "Home Repair & Maintenance",
                "icon": "🏠",
                "color": "orange",
                "capabilities": [
                    "Diagnostic troubleshooting",
                    "Step-by-step repair guides", 
                    "Tool and material recommendations",
                    "Safety guidelines",
                    "Cost estimation"
                ]
            },
            "car-repair": {
                "name": "Auto Repair & Service",
                "icon": "🚗",
                "color": "red",
                "capabilities": [
                    "Vehicle diagnostics",
                    "Maintenance scheduling",
                    "Parts identification",
                    "Labor estimates",
                    "Technical specifications"
                ]
            },
            "manufacturing": {
                "name": "Manufacturing & Production",
                "icon": "🏭",
                "color": "blue",
                "capabilities": [
                    "Production optimization",
                    "Quality control",
                    "Equipment maintenance",
                    "Safety compliance",
                    "Efficiency analysis"
                ]
            },
            "healthcare": {
                "name": "Healthcare Operations",
                "icon": "🏥",
                "color": "green",
                "capabilities": [
                    "Patient flow optimization",
                    "Compliance monitoring",
                    "Equipment scheduling",
                    "Resource allocation",
                    "Workflow improvement"
                ]
            },
            "retail": {
                "name": "Retail Operations",
                "icon": "🛍️",
                "color": "purple",
                "capabilities": [
                    "Inventory management",
                    "Customer service",
                    "Sales analytics",
                    "Operations efficiency",
                    "Loss prevention"
                ]
            },
            "construction": {
                "name": "Construction Management",
                "icon": "🏗️",
                "color": "yellow",
                "capabilities": [
                    "Project planning",
                    "Safety protocols",
                    "Material management",
                    "Quality inspections",
                    "Cost estimation"
                ]
            },
            "logistics": {
                "name": "Logistics & Transportation",
                "icon": "🚚",
                "color": "teal",
                "capabilities": [
                    "Route optimization",
                    "Fleet management",
                    "Warehouse operations",
                    "Delivery tracking",
                    "Cost reduction"
                ]
            }
        }
        
        return industry_info.get(industry, industry_info["home-repair"])

# Global AI assistant instance
ai_assistant = AIAssistantService()