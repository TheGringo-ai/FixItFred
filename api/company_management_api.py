#!/usr/bin/env python3
"""
Company Management API - View and manage all deployed companies
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any, Optional
import sqlite3
import json
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/companies", tags=["companies"])

@router.get("/list")
async def list_companies(
    industry: Optional[str] = None,
    size: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    limit: int = 20
):
    """Get list of all deployed companies with filters"""
    
    try:
        conn = sqlite3.connect("fred_deployments.db")
        cursor = conn.cursor()
        
        # Base query
        query = '''
            SELECT deployment_id, company_name, industry, size, 
                   modules, worker_count, deployment_status, 
                   custom_domain, revenue_potential, created_at
            FROM deployments
            WHERE 1=1
        '''
        params = []
        
        # Apply filters
        if industry:
            query += " AND industry = ?"
            params.append(industry)
        
        if size:
            query += " AND size = ?"
            params.append(size)
        
        if status:
            query += " AND deployment_status = ?"
            params.append(status)
        
        if search:
            query += " AND (company_name LIKE ? OR custom_domain LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%"])
        
        # Add pagination
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, (page - 1) * limit])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        companies = []
        for row in rows:
            # Calculate last activity (simulated)
            created = datetime.fromisoformat(row[9])
            hours_ago = max(1, min(48, hash(row[0]) % 48))
            last_activity = f"{hours_ago} hours ago" if hours_ago > 1 else "1 hour ago"
            
            companies.append({
                "id": row[0],
                "name": row[1],
                "industry": row[2],
                "size": row[3],
                "modules": json.loads(row[4]),
                "workers": row[5],
                "status": row[6],
                "domain": row[7],
                "revenue": row[8],
                "deployedDate": row[9],
                "lastActivity": last_activity,
                "apiKey": f"fif_{row[1].lower().replace(' ', '_')[:10]}_{row[0][-8:]}"
            })
        
        # Get total count for pagination
        count_query = '''
            SELECT COUNT(*) FROM deployments WHERE 1=1
        '''
        count_params = []
        
        if industry:
            count_query += " AND industry = ?"
            count_params.append(industry)
        
        if size:
            count_query += " AND size = ?"
            count_params.append(size)
        
        if status:
            count_query += " AND deployment_status = ?"
            count_params.append(status)
        
        if search:
            count_query += " AND (company_name LIKE ? OR custom_domain LIKE ?)"
            count_params.extend([f"%{search}%", f"%{search}%"])
        
        cursor.execute(count_query, count_params)
        total_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "companies": companies,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total_count,
                "pages": (total_count + limit - 1) // limit
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{company_id}")
async def get_company_details(company_id: str):
    """Get detailed information about a specific company"""
    
    try:
        conn = sqlite3.connect("fred_deployments.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM deployments WHERE deployment_id = ?
        ''', (company_id,))
        
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Company not found")
        
        # Simulate additional metrics
        workers = row[5]
        modules = json.loads(row[4])
        
        # Generate worker breakdown
        worker_breakdown = {
            "inspector": max(1, workers // 4),
            "technician": max(1, workers // 3),
            "operator": max(1, workers // 5),
            "supervisor": max(1, workers // 10),
            "manager": max(1, workers // 20)
        }
        
        # Generate module usage stats
        module_stats = {}
        for module in modules:
            # Simulate usage statistics
            module_stats[module] = {
                "active_users": max(1, workers // len(modules)),
                "daily_actions": max(10, workers * 5),
                "uptime": 99.7,
                "satisfaction": 4.8
            }
        
        company_details = {
            "id": row[0],
            "name": row[1],
            "industry": row[2],
            "size": row[3],
            "modules": modules,
            "workers": workers,
            "status": row[6],
            "domain": row[8],
            "revenue": row[9],
            "deployedDate": row[10],
            "apiKeys": json.loads(row[7]),
            "workerBreakdown": worker_breakdown,
            "moduleStats": module_stats,
            "performanceMetrics": {
                "productivity_increase": "35%",
                "error_reduction": "67%",
                "time_saved_daily": f"{workers * 45} minutes",
                "worker_satisfaction": 4.7,
                "roi": "340%"
            },
            "recentActivity": [
                {"action": "Quality inspection completed", "user": "John Smith", "time": "15 mins ago"},
                {"action": "Maintenance task assigned", "user": "Sarah Johnson", "time": "23 mins ago"},
                {"action": "Safety report submitted", "user": "Mike Chen", "time": "1 hour ago"},
                {"action": "New worker onboarded", "user": "System", "time": "2 hours ago"}
            ]
        }
        
        conn.close()
        
        return company_details
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{company_id}/suspend")
async def suspend_company(company_id: str):
    """Suspend a company's access"""
    
    try:
        conn = sqlite3.connect("fred_deployments.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE deployments 
            SET deployment_status = 'suspended'
            WHERE deployment_id = ?
        ''', (company_id,))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Company not found")
        
        conn.commit()
        conn.close()
        
        return {"status": "success", "message": "Company suspended successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{company_id}/activate")
async def activate_company(company_id: str):
    """Activate a suspended company"""
    
    try:
        conn = sqlite3.connect("fred_deployments.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE deployments 
            SET deployment_status = 'active'
            WHERE deployment_id = ?
        ''', (company_id,))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Company not found")
        
        conn.commit()
        conn.close()
        
        return {"status": "success", "message": "Company activated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{company_id}/workers")
async def get_company_workers(company_id: str):
    """Get worker list for a company"""
    
    try:
        conn = sqlite3.connect("fred_deployments.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT company_name, worker_count FROM deployments 
            WHERE deployment_id = ?
        ''', (company_id,))
        
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Company not found")
        
        company_name, worker_count = row
        
        # Generate worker list (simulated)
        workers = []
        roles = ["inspector", "technician", "operator", "supervisor", "manager"]
        
        for i in range(min(worker_count, 50)):  # Limit to 50 for demo
            role = roles[i % len(roles)]
            workers.append({
                "id": f"W-{company_id[-4:]}-{i+1:03d}",
                "name": f"Worker {i+1}",
                "role": role,
                "department": "production" if role in ["inspector", "operator"] else "management",
                "status": "active",
                "lastLogin": f"{(i % 24) + 1} hours ago",
                "tasksCompleted": max(5, (i + 1) * 3),
                "aiAgentId": f"Fred-{role}-{i+1}",
                "performance": {
                    "efficiency": min(100, 75 + (i % 25)),
                    "quality": min(100, 80 + (i % 20)),
                    "safety": min(100, 85 + (i % 15))
                }
            })
        
        conn.close()
        
        return {
            "company": company_name,
            "totalWorkers": worker_count,
            "workers": workers,
            "summary": {
                "active": len([w for w in workers if w["status"] == "active"]),
                "avgEfficiency": sum(w["performance"]["efficiency"] for w in workers) / len(workers),
                "totalTasks": sum(w["tasksCompleted"] for w in workers)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{company_id}/analytics")
async def get_company_analytics(company_id: str):
    """Get analytics for a company"""
    
    try:
        conn = sqlite3.connect("fred_deployments.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT company_name, worker_count, modules, revenue_potential, created_at
            FROM deployments WHERE deployment_id = ?
        ''', (company_id,))
        
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Company not found")
        
        company_name, workers, modules_json, revenue, created_at = row
        modules = json.loads(modules_json)
        
        # Generate analytics data (simulated)
        days_active = (datetime.now() - datetime.fromisoformat(created_at)).days
        
        analytics = {
            "company": company_name,
            "overview": {
                "daysActive": days_active,
                "totalWorkers": workers,
                "activeModules": len(modules),
                "totalRevenue": revenue
            },
            "productivity": {
                "tasksCompleted": workers * days_active * 4,
                "avgTaskTime": "12 minutes",
                "efficiencyGain": "35%",
                "timesSaved": f"{workers * 45} minutes/day"
            },
            "usage": {
                "dailyActiveUsers": int(workers * 0.85),
                "avgSessionTime": "6.2 hours",
                "voiceCommandsUsed": workers * days_active * 15,
                "aiInteractions": workers * days_active * 8
            },
            "quality": {
                "defectsReduced": "67%",
                "inspectionAccuracy": "97.8%",
                "complianceScore": "98.5%",
                "customerSatisfaction": 4.8
            },
            "modulePerformance": {
                module: {
                    "usage": f"{max(50, 100 - (hash(module) % 30))}%",
                    "satisfaction": round(4.2 + (hash(module) % 8) / 10, 1),
                    "roi": f"{max(200, 150 + (hash(module) % 200))}%"
                }
                for module in modules
            }
        }
        
        conn.close()
        
        return analytics
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/overview")
async def get_overview_stats():
    """Get overview statistics for all companies"""
    
    try:
        conn = sqlite3.connect("fred_deployments.db")
        cursor = conn.cursor()
        
        # Total companies
        cursor.execute("SELECT COUNT(*) FROM deployments")
        total_companies = cursor.fetchone()[0]
        
        # Active companies
        cursor.execute("SELECT COUNT(*) FROM deployments WHERE deployment_status = 'active'")
        active_companies = cursor.fetchone()[0]
        
        # Total workers
        cursor.execute("SELECT SUM(worker_count) FROM deployments")
        total_workers = cursor.fetchone()[0] or 0
        
        # Total revenue
        cursor.execute("SELECT SUM(revenue_potential) FROM deployments")
        total_revenue = cursor.fetchone()[0] or 0
        
        # Industry breakdown
        cursor.execute('''
            SELECT industry, COUNT(*), SUM(worker_count), SUM(revenue_potential)
            FROM deployments 
            GROUP BY industry
        ''')
        
        industries = []
        for row in cursor.fetchall():
            industries.append({
                "industry": row[0],
                "companies": row[1],
                "workers": row[2],
                "revenue": row[3]
            })
        
        conn.close()
        
        return {
            "overview": {
                "totalCompanies": total_companies,
                "activeCompanies": active_companies,
                "totalWorkers": total_workers,
                "totalRevenue": total_revenue,
                "avgRevenuePerCompany": total_revenue / max(total_companies, 1),
                "avgWorkersPerCompany": total_workers / max(total_companies, 1)
            },
            "industries": industries,
            "projections": {
                "at10k": total_revenue * (10000 / max(total_companies, 1)),
                "at50k": total_revenue * (50000 / max(total_companies, 1)),
                "at200k": total_revenue * (200000 / max(total_companies, 1))
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))