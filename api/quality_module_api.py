#!/usr/bin/env python3
"""
Quality Control Module API - Integrated into main dashboard
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Any, Optional
import asyncio
from datetime import datetime
import uuid
from enum import Enum

router = APIRouter(prefix="/api/quality", tags=["quality"])

# Quality-specific data models
class InspectionStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PASSED = "passed"
    FAILED = "failed"
    REQUIRES_REVIEW = "requires_review"

class DefectType(Enum):
    DIMENSIONAL = "dimensional"
    SURFACE = "surface"
    FUNCTIONAL = "functional"
    APPEARANCE = "appearance"
    MISSING_PART = "missing_part"
    CONTAMINATION = "contamination"

# In-memory storage for demo (would be database in production)
quality_inspections = {}
quality_defects = {}

# Quality AI Agent
class QualityAI:
    """AI agent specialized for quality control"""
    
    def __init__(self):
        self.capabilities = [
            "visual_inspection_guidance", "defect_pattern_recognition", 
            "quality_data_collection", "inspection_report_generation",
            "non_conformance_reporting", "corrective_action_tracking",
            "statistical_process_control", "supplier_quality_assessment"
        ]
    
    async def process_inspection_request(self, inspection_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process quality inspection with AI guidance"""
        
        if inspection_type == "visual_inspection":
            return {
                "guidance": """Visual Inspection AI Guidance:
                
1. Lighting: Ensure adequate lighting (500+ lux)
2. Surface Check: Look for scratches, dents, discoloration
3. Dimensional: Verify key measurements against spec
4. Functional: Test moving parts and connections
5. Documentation: Take photos of any defects found

Inspection checklist:
☐ Overall appearance assessment
☐ Surface quality check
☐ Dimensional verification
☐ Functional testing
☐ Photo documentation""",
                "expected_time": "15-20 minutes",
                "tools_needed": ["calipers", "surface_gauge", "camera"],
                "ai_recommendations": [
                    "Start with overall visual assessment",
                    "Document defects immediately with photos", 
                    "Use proper measuring tools for critical dimensions",
                    "Follow standardized inspection sequence"
                ]
            }
        
        elif inspection_type == "defect_analysis":
            defect_type = data.get("defect_type", "unknown")
            analyses = {
                "dimensional": "Dimensional defects suggest tooling wear or setup issues. Check machine calibration and tooling condition.",
                "surface": "Surface defects may indicate handling or processing problems. Review material handling procedures.",
                "functional": "Functional defects suggest assembly issues. Verify component specifications and assembly procedures."
            }
            
            return {
                "analysis": analyses.get(defect_type, "Defect requires detailed root cause analysis"),
                "suggested_actions": [
                    "Document defect location and characteristics",
                    "Investigate potential root causes",
                    "Implement corrective actions",
                    "Monitor for recurrence"
                ],
                "priority": self._determine_defect_priority(defect_type)
            }
        
        return {"response": f"AI guidance for {inspection_type} not yet implemented"}
    
    def _determine_defect_priority(self, defect_type: str) -> str:
        """Determine defect priority based on type"""
        priority_map = {
            "functional": "high",
            "dimensional": "medium", 
            "surface": "low",
            "appearance": "low"
        }
        return priority_map.get(defect_type, "medium")

quality_ai = QualityAI()

@router.post("/inspections")
async def create_inspection(inspection_data: Dict[str, Any]):
    """Create a new quality inspection"""
    
    inspection_id = f"QI-{uuid.uuid4().hex[:8]}"
    
    inspection = {
        "inspection_id": inspection_id,
        "product_id": inspection_data.get("product_id"),
        "batch_number": inspection_data.get("batch_number"),
        "inspector_id": inspection_data.get("inspector_id", "default_inspector"),
        "status": InspectionStatus.PENDING.value,
        "created_at": datetime.now().isoformat(),
        "measurements": {},
        "defects": [],
        "photos": [],
        "notes": "",
        "ai_guidance_requested": False,
        "custom_fields": {
            "production_line": inspection_data.get("production_line", ""),
            "shift": inspection_data.get("shift", ""),
            "temperature": inspection_data.get("temperature", ""),
            "humidity": inspection_data.get("humidity", ""),
            "inspector_notes": inspection_data.get("inspector_notes", ""),
            "customer_requirements": inspection_data.get("customer_requirements", []),
            "environmental_conditions": inspection_data.get("environmental_conditions", {}),
            "batch_size": inspection_data.get("batch_size", 0)
        }
    }
    
    quality_inspections[inspection_id] = inspection
    
    return {
        "status": "success",
        "inspection_id": inspection_id,
        "message": "Quality inspection created successfully",
        "custom_fields_available": True
    }

@router.get("/inspections/{inspection_id}")
async def get_inspection(inspection_id: str):
    """Get inspection details"""
    
    inspection = quality_inspections.get(inspection_id)
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    
    return inspection

@router.post("/inspections/{inspection_id}/ai-guidance")
async def get_ai_guidance(inspection_id: str, request: Dict[str, Any]):
    """Get AI guidance for inspection"""
    
    inspection = quality_inspections.get(inspection_id)
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    
    inspection_type = request.get("inspection_type", "visual_inspection")
    guidance = await quality_ai.process_inspection_request(inspection_type, request)
    
    # Mark that AI guidance was requested
    inspection["ai_guidance_requested"] = True
    inspection["last_ai_guidance"] = datetime.now().isoformat()
    
    return {
        "inspection_id": inspection_id,
        "guidance_type": inspection_type,
        **guidance
    }

@router.post("/inspections/{inspection_id}/measurements")
async def add_measurements(inspection_id: str, measurements: Dict[str, Any]):
    """Add measurements to inspection"""
    
    inspection = quality_inspections.get(inspection_id)
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    
    # Validate measurements and determine pass/fail
    for measurement_name, measurement_data in measurements.items():
        value = measurement_data.get("value")
        spec = measurement_data.get("spec")
        tolerance = measurement_data.get("tolerance", 0.05)
        
        # Simple pass/fail logic (would be more sophisticated in production)
        target = spec
        status = "pass" if abs(value - target) <= tolerance else "fail"
        
        measurement_data["status"] = status
        measurement_data["recorded_at"] = datetime.now().isoformat()
    
    inspection["measurements"].update(measurements)
    inspection["updated_at"] = datetime.now().isoformat()
    
    # Auto-update inspection status based on measurements
    failed_measurements = [m for m in measurements.values() if m.get("status") == "fail"]
    if failed_measurements:
        inspection["status"] = InspectionStatus.REQUIRES_REVIEW.value
    
    return {
        "status": "success",
        "inspection_id": inspection_id,
        "measurements_added": len(measurements),
        "failed_measurements": len(failed_measurements)
    }

@router.post("/inspections/{inspection_id}/defects")
async def add_defect(inspection_id: str, defect_data: Dict[str, Any]):
    """Add defect to inspection"""
    
    inspection = quality_inspections.get(inspection_id)
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    
    defect_id = f"QD-{uuid.uuid4().hex[:8]}"
    
    defect = {
        "defect_id": defect_id,
        "inspection_id": inspection_id,
        "defect_type": defect_data.get("defect_type", DefectType.SURFACE.value),
        "description": defect_data.get("description", ""),
        "location": defect_data.get("location", ""),
        "severity": defect_data.get("severity", "low"),
        "photo_urls": defect_data.get("photo_urls", []),
        "created_at": datetime.now().isoformat()
    }
    
    quality_defects[defect_id] = defect
    inspection["defects"].append(defect_id)
    
    # Update inspection status
    if defect["severity"] in ["high", "critical"]:
        inspection["status"] = InspectionStatus.FAILED.value
    elif inspection["status"] == InspectionStatus.PENDING.value:
        inspection["status"] = InspectionStatus.REQUIRES_REVIEW.value
    
    # Get AI analysis of defect
    ai_analysis = await quality_ai.process_inspection_request("defect_analysis", defect)
    
    return {
        "status": "success",
        "defect_id": defect_id,
        "inspection_status": inspection["status"],
        "ai_analysis": ai_analysis
    }

@router.put("/inspections/{inspection_id}/status")
async def update_inspection_status(inspection_id: str, status_update: Dict[str, Any]):
    """Update inspection status"""
    
    inspection = quality_inspections.get(inspection_id)
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    
    new_status = status_update.get("status")
    if new_status not in [s.value for s in InspectionStatus]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    inspection["status"] = new_status
    inspection["updated_at"] = datetime.now().isoformat()
    
    if "notes" in status_update:
        inspection["notes"] = status_update["notes"]
    
    return {
        "status": "success",
        "inspection_id": inspection_id,
        "new_status": new_status
    }

@router.get("/inspections")
async def list_inspections(status: Optional[str] = None, inspector_id: Optional[str] = None):
    """List quality inspections with optional filters"""
    
    inspections = list(quality_inspections.values())
    
    # Apply filters
    if status:
        inspections = [i for i in inspections if i["status"] == status]
    
    if inspector_id:
        inspections = [i for i in inspections if i["inspector_id"] == inspector_id]
    
    # Sort by creation date (newest first)
    inspections.sort(key=lambda x: x["created_at"], reverse=True)
    
    return {
        "inspections": inspections,
        "total_count": len(inspections),
        "filters": {"status": status, "inspector_id": inspector_id}
    }

@router.get("/defects")
async def list_defects(defect_type: Optional[str] = None, severity: Optional[str] = None):
    """List quality defects with optional filters"""
    
    defects = list(quality_defects.values())
    
    # Apply filters
    if defect_type:
        defects = [d for d in defects if d["defect_type"] == defect_type]
    
    if severity:
        defects = [d for d in defects if d["severity"] == severity]
    
    # Sort by creation date (newest first) 
    defects.sort(key=lambda x: x["created_at"], reverse=True)
    
    return {
        "defects": defects,
        "total_count": len(defects),
        "filters": {"defect_type": defect_type, "severity": severity}
    }

@router.get("/analytics/summary")
async def get_quality_summary():
    """Get quality analytics summary"""
    
    total_inspections = len(quality_inspections)
    total_defects = len(quality_defects)
    
    # Calculate pass/fail rates
    passed_inspections = len([i for i in quality_inspections.values() if i["status"] == InspectionStatus.PASSED.value])
    failed_inspections = len([i for i in quality_inspections.values() if i["status"] == InspectionStatus.FAILED.value])
    
    pass_rate = (passed_inspections / total_inspections * 100) if total_inspections > 0 else 0
    
    # Defect analysis
    defect_by_type = {}
    defect_by_severity = {}
    
    for defect in quality_defects.values():
        dtype = defect["defect_type"]
        severity = defect["severity"]
        
        defect_by_type[dtype] = defect_by_type.get(dtype, 0) + 1
        defect_by_severity[severity] = defect_by_severity.get(severity, 0) + 1
    
    return {
        "summary": {
            "total_inspections": total_inspections,
            "total_defects": total_defects,
            "pass_rate": round(pass_rate, 2),
            "passed_inspections": passed_inspections,
            "failed_inspections": failed_inspections
        },
        "defect_analysis": {
            "by_type": defect_by_type,
            "by_severity": defect_by_severity
        },
        "generated_at": datetime.now().isoformat()
    }

@router.post("/custom-fields")
async def add_custom_field(field_data: Dict[str, Any]):
    """Add a new custom field to the Quality module"""
    
    field_name = field_data.get("field_name")
    field_type = field_data.get("field_type", "text")  # text, number, boolean, select, date
    field_options = field_data.get("options", [])  # for select fields
    is_required = field_data.get("required", False)
    
    if not field_name:
        raise HTTPException(status_code=400, detail="Field name is required")
    
    # Store custom field definition (would be in database in production)
    if not hasattr(router, 'custom_fields'):
        router.custom_fields = {}
    
    router.custom_fields[field_name] = {
        "name": field_name,
        "type": field_type,
        "options": field_options,
        "required": is_required,
        "created_at": datetime.now().isoformat()
    }
    
    return {
        "status": "success",
        "message": f"Custom field '{field_name}' added successfully",
        "field": router.custom_fields[field_name]
    }

@router.get("/custom-fields")
async def get_custom_fields():
    """Get all custom fields for the Quality module"""
    
    if not hasattr(router, 'custom_fields'):
        router.custom_fields = {}
    
    return {
        "custom_fields": router.custom_fields,
        "total_count": len(router.custom_fields)
    }

@router.delete("/custom-fields/{field_name}")
async def remove_custom_field(field_name: str):
    """Remove a custom field from the Quality module"""
    
    if not hasattr(router, 'custom_fields') or field_name not in router.custom_fields:
        raise HTTPException(status_code=404, detail="Custom field not found")
    
    removed_field = router.custom_fields.pop(field_name)
    
    return {
        "status": "success",
        "message": f"Custom field '{field_name}' removed successfully",
        "removed_field": removed_field
    }

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    custom_field_count = len(getattr(router, 'custom_fields', {}))
    
    return {
        "status": "healthy",
        "module": "quality_control",
        "capabilities": quality_ai.capabilities,
        "active_inspections": len([i for i in quality_inspections.values() if i["status"] in [InspectionStatus.PENDING.value, InspectionStatus.IN_PROGRESS.value]]),
        "custom_fields_count": custom_field_count,
        "customization_enabled": True,
        "timestamp": datetime.now().isoformat()
    }