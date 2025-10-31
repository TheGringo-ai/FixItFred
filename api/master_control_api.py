#!/usr/bin/env python3
"""
Master Control API - For managing deployments to companies
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any, Optional
import asyncio
from datetime import datetime
import uuid
import json
import sqlite3

router = APIRouter(prefix="/api/master", tags=["master"])

@router.post("/deploy-company")
async def deploy_company(deployment_request: Dict[str, Any]):
    """Deploy FixItFred to a new company"""
    
    company_name = deployment_request.get("company_name")
    worker_count = deployment_request.get("worker_count", 50)
    modules = deployment_request.get("modules", ["quality", "maintenance"])
    industry = deployment_request.get("industry", "manufacturing")
    
    if not company_name:
        raise HTTPException(status_code=400, detail="Company name is required")
    
    # Import the deployment system
    from core.fred_master_deployment import fred_assistant
    
    # Deploy through Fred
    deployment = await fred_assistant.deploy_for_company(
        company_name=company_name,
        industry=industry,
        size="medium",
        modules=modules,
        worker_count=worker_count
    )
    
    return {
        "status": "success",
        "deployment": deployment,
        "message": f"Successfully deployed for {company_name}!"
    }

@router.post("/chat-with-fred")
async def chat_with_fred(message_request: Dict[str, Any]):
    """Chat with Fred assistant"""
    
    message = message_request.get("message")
    if not message:
        raise HTTPException(status_code=400, detail="Message is required")
    
    # Import Fred
    from core.fred_master_deployment import fred_assistant
    
    # Process message
    response = await fred_assistant.talk_to_fred(message)
    
    return {
        "fred_response": response.get("response"),
        "data": response.get("deployment") if "deployment" in response else None
    }

@router.get("/deployment-stats")
async def get_deployment_stats():
    """Get deployment statistics"""
    
    from core.fred_master_deployment import fred_assistant
    
    # Get stats
    status_response = await fred_assistant._get_deployment_status()
    revenue_response = await fred_assistant._get_revenue_report()
    
    # Parse the responses to extract numbers
    import re
    
    # Extract numbers from status response
    status_text = status_response["response"]
    total_deployments = int(re.search(r'Total Deployments: (\d+)', status_text).group(1)) if re.search(r'Total Deployments: (\d+)', status_text) else 0
    total_workers = int(re.search(r'Total Workers: ([\d,]+)', status_text.replace(',', '')).group(1)) if re.search(r'Total Workers: ([\d,]+)', status_text) else 0
    
    # Extract revenue numbers
    revenue_text = revenue_response["response"]
    total_revenue = float(re.search(r'Current Total: \$([\d,]+\.\d+)', revenue_text.replace(',', '')).group(1)) if re.search(r'Current Total: \$([\d,]+\.\d+)', revenue_text) else 0
    monthly_revenue = float(re.search(r'Monthly Recurring: \$([\d,]+\.\d+)', revenue_text.replace(',', '')).group(1)) if re.search(r'Monthly Recurring: \$([\d,]+\.\d+)', revenue_text) else 0
    
    return {
        "total_deployments": total_deployments,
        "total_workers": total_workers,
        "total_revenue": total_revenue,
        "monthly_revenue": monthly_revenue,
        "today_deployments": total_deployments,  # Would track daily in production
        "projected_200k": total_revenue * (200000 / max(total_deployments, 1))
    }

@router.get("/recent-deployments")
async def get_recent_deployments():
    """Get recent deployments"""
    
    try:
        conn = sqlite3.connect("fred_deployments.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT company_name, worker_count, modules, deployment_time, 
                   custom_domain, revenue_potential, created_at
            FROM deployments 
            ORDER BY created_at DESC 
            LIMIT 10
        ''')
        
        deployments = []
        for row in cursor.fetchall():
            deployments.append({
                "company": row[0],
                "workers": row[1],
                "modules": json.loads(row[2]),
                "deployment_time": row[3],
                "domain": row[4],
                "revenue": row[5],
                "created_at": row[6]
            })
        
        conn.close()
        
        return {"deployments": deployments}
        
    except Exception as e:
        return {"deployments": []}

@router.get("/available-modules")
async def get_available_modules():
    """Get list of available modules"""
    
    return {
        "modules": [
            {
                "id": "quality",
                "name": "Quality Control",
                "description": "AI-powered quality inspections and defect tracking",
                "price": 2000
            },
            {
                "id": "maintenance",
                "name": "Maintenance Management", 
                "description": "Predictive maintenance and work order management",
                "price": 2000
            },
            {
                "id": "safety",
                "name": "Safety Compliance",
                "description": "Safety incident tracking and compliance monitoring",
                "price": 2000
            },
            {
                "id": "operations",
                "name": "Operations Dashboard",
                "description": "Real-time operations monitoring and analytics",
                "price": 2000
            },
            {
                "id": "analytics",
                "name": "Analytics Platform",
                "description": "Advanced analytics and reporting capabilities",
                "price": 2500
            },
            {
                "id": "compliance",
                "name": "Compliance Management",
                "description": "Regulatory compliance and audit management",
                "price": 3000
            }
        ]
    }

@router.post("/bulk-deploy")
async def bulk_deploy(bulk_request: Dict[str, Any]):
    """Deploy to multiple companies at once"""
    
    companies = bulk_request.get("companies", [])
    if not companies:
        raise HTTPException(status_code=400, detail="No companies provided")
    
    from core.fred_master_deployment import fred_assistant
    
    results = []
    
    for company_data in companies:
        try:
            deployment = await fred_assistant.deploy_for_company(
                company_name=company_data.get("name"),
                industry=company_data.get("industry", "manufacturing"),
                size=company_data.get("size", "medium"),
                modules=company_data.get("modules", ["quality", "maintenance"]),
                worker_count=company_data.get("workers", 50)
            )
            
            results.append({
                "company": company_data.get("name"),
                "status": "success",
                "deployment": deployment
            })
            
        except Exception as e:
            results.append({
                "company": company_data.get("name"),
                "status": "failed",
                "error": str(e)
            })
    
    return {
        "status": "completed",
        "results": results,
        "successful": len([r for r in results if r["status"] == "success"]),
        "failed": len([r for r in results if r["status"] == "failed"])
    }

@router.get("/revenue-projection")
async def get_revenue_projection():
    """Get revenue projections at different scales"""
    
    # Get current average revenue per company
    stats = await get_deployment_stats()
    avg_revenue = stats["total_revenue"] / max(stats["total_deployments"], 1)
    
    projections = []
    scales = [100, 1000, 10000, 50000, 100000, 200000]
    
    for scale in scales:
        total_revenue = avg_revenue * scale
        monthly = total_revenue / 12
        
        projections.append({
            "companies": scale,
            "total_revenue": total_revenue,
            "monthly_revenue": monthly,
            "deployment_time": f"{scale * 9 / 60:.1f} minutes"  # 9 seconds per deployment
        })
    
    return {
        "current_avg_per_company": avg_revenue,
        "projections": projections
    }

@router.post("/simulate-growth")
async def simulate_growth():
    """Simulate rapid growth deployment"""
    
    from core.fred_master_deployment import fred_assistant
    
    # Simulate deploying to 10 major companies quickly
    major_companies = [
        ("Apple Manufacturing", 2000, ["quality", "operations", "analytics"]),
        ("Google Data Centers", 800, ["maintenance", "safety", "operations"]),
        ("Amazon Warehouses", 5000, ["quality", "operations", "analytics"]),
        ("Microsoft Cloud", 1200, ["maintenance", "operations", "analytics"]),
        ("Meta Infrastructure", 600, ["quality", "safety", "compliance"]),
        ("Netflix Production", 400, ["quality", "operations"]),
        ("Uber Technologies", 300, ["operations", "analytics"]),
        ("Airbnb Operations", 250, ["quality", "compliance"]),
        ("SpaceX Manufacturing", 1500, ["quality", "safety", "compliance"]),
        ("OpenAI Infrastructure", 200, ["operations", "analytics"])
    ]
    
    simulation_results = []
    total_revenue = 0
    
    for company, workers, modules in major_companies:
        # Calculate expected revenue
        base_price = 5000
        module_price = 2000 * len(modules)
        worker_price = 100 * workers
        revenue = base_price + module_price + worker_price
        
        simulation_results.append({
            "company": company,
            "workers": workers,
            "modules": modules,
            "revenue": revenue,
            "deployment_time": "9 seconds"
        })
        
        total_revenue += revenue
    
    return {
        "simulation": "Major Tech Companies Deployment",
        "companies": len(major_companies),
        "total_workers": sum(workers for _, workers, _ in major_companies),
        "total_revenue": total_revenue,
        "total_deployment_time": f"{len(major_companies) * 9} seconds",
        "results": simulation_results
    }