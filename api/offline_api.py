#!/usr/bin/env python3
"""
Offline-First API Endpoints for FixItFred
Handles network drops gracefully with intelligent sync
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import Dict, List, Any, Optional
import asyncio
from datetime import datetime
import uuid
import base64

from core.offline.offline_sync_engine import offline_sync_engine

router = APIRouter(prefix="/api/offline", tags=["offline"])

@router.post("/store-record")
async def store_offline_record(record_data: Dict[str, Any]):
    """Store any type of record for offline use"""
    
    try:
        record_id = await offline_sync_engine.store_offline_record(
            record_type=record_data.get("record_type"),
            data=record_data.get("data"),
            worker_id=record_data.get("worker_id"),
            device_id=record_data.get("device_id"),
            parent_record_id=record_data.get("parent_record_id"),
            operation=record_data.get("operation", "create")
        )
        
        return {
            "status": "success",
            "record_id": record_id,
            "message": "Record stored offline successfully",
            "will_sync_when_online": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/store-inspection")
async def store_inspection_offline(inspection_data: Dict[str, Any]):
    """Store quality inspection offline"""
    
    device_id = inspection_data.get("device_id", "unknown_device")
    worker_id = inspection_data.get("inspector_id", "unknown_worker")
    
    # Add offline-specific metadata
    inspection_data.update({
        "offline_created": True,
        "created_at": datetime.now().isoformat(),
        "offline_device_id": device_id
    })
    
    record_id = await offline_sync_engine.store_offline_record(
        record_type="inspection",
        data=inspection_data,
        worker_id=worker_id,
        device_id=device_id
    )
    
    return {
        "status": "success",
        "inspection_id": record_id,
        "message": "Inspection stored offline - will sync when network returns",
        "offline_mode": True
    }

@router.post("/store-measurement")
async def store_measurement_offline(measurement_data: Dict[str, Any]):
    """Store measurement data offline"""
    
    device_id = measurement_data.get("device_id", "unknown_device")
    worker_id = measurement_data.get("worker_id", "unknown_worker")
    
    record_id = await offline_sync_engine.store_offline_record(
        record_type="measurement",
        data=measurement_data,
        worker_id=worker_id,
        device_id=device_id,
        parent_record_id=measurement_data.get("inspection_id")
    )
    
    return {
        "status": "success",
        "measurement_id": record_id,
        "message": "Measurement stored offline",
        "parent_inspection": measurement_data.get("inspection_id")
    }

@router.post("/store-photo")
async def store_photo_offline(photo_file: UploadFile = File(...), 
                            record_id: str = None,
                            worker_id: str = None,
                            device_id: str = None):
    """Store photo offline"""
    
    try:
        photo_data = await photo_file.read()
        
        # Store photo using offline photo manager
        photo_id = await offline_sync_engine.photo_manager.store_photo_offline(
            photo_data=photo_data,
            record_id=record_id,
            worker_id=worker_id
        )
        
        # Also store photo metadata as offline record
        photo_metadata = {
            "photo_id": photo_id,
            "filename": photo_file.filename,
            "content_type": photo_file.content_type,
            "file_size": len(photo_data),
            "related_record_id": record_id,
            "created_at": datetime.now().isoformat()
        }
        
        metadata_record_id = await offline_sync_engine.store_offline_record(
            record_type="photo",
            data=photo_metadata,
            worker_id=worker_id,
            device_id=device_id,
            parent_record_id=record_id
        )
        
        return {
            "status": "success",
            "photo_id": photo_id,
            "metadata_record_id": metadata_record_id,
            "message": "Photo stored offline - will upload when online",
            "file_size": len(photo_data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/store-voice")
async def store_voice_offline(voice_data: Dict[str, Any]):
    """Store voice recording offline"""
    
    try:
        # Decode base64 audio data
        audio_data = base64.b64decode(voice_data.get("audio_data", ""))
        transcript = voice_data.get("transcript", "")
        worker_id = voice_data.get("worker_id")
        device_id = voice_data.get("device_id")
        
        # Store voice using offline voice recorder
        voice_id = await offline_sync_engine.voice_recorder.store_voice_offline(
            audio_data=audio_data,
            worker_id=worker_id,
            transcript=transcript
        )
        
        # Store voice metadata as offline record
        voice_metadata = {
            "voice_id": voice_id,
            "transcript": transcript,
            "duration": voice_data.get("duration", 0),
            "related_record_id": voice_data.get("record_id"),
            "created_at": datetime.now().isoformat()
        }
        
        metadata_record_id = await offline_sync_engine.store_offline_record(
            record_type="voice",
            data=voice_metadata,
            worker_id=worker_id,
            device_id=device_id
        )
        
        return {
            "status": "success",
            "voice_id": voice_id,
            "transcript": transcript,
            "message": "Voice recording stored offline",
            "will_process_when_online": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sync-when-online")
async def sync_offline_data():
    """Manually trigger sync when network comes back online"""
    
    try:
        sync_results = await offline_sync_engine.sync_when_online()
        
        return {
            "status": "success" if sync_results["failures"] == 0 else "partial",
            "sync_results": sync_results,
            "message": f"Synced {sync_results['synced']} records successfully"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Sync failed: {str(e)}",
            "recommendation": "Will retry automatically when network is stable"
        }

@router.get("/status/{device_id}")
async def get_offline_status(device_id: str):
    """Get current offline status for a device"""
    
    try:
        status = await offline_sync_engine.get_offline_status(device_id)
        return status
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conflicts")
async def get_sync_conflicts():
    """Get all unresolved sync conflicts"""
    
    try:
        import sqlite3
        conn = sqlite3.connect(offline_sync_engine.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT conflict_id, local_record_id, conflict_type, 
                   resolution_strategy, created_at 
            FROM sync_conflicts 
            WHERE resolved_at IS NULL
            ORDER BY created_at DESC
        ''')
        
        conflicts = []
        for row in cursor.fetchall():
            conflicts.append({
                "conflict_id": row[0],
                "local_record_id": row[1],
                "conflict_type": row[2],
                "resolution_strategy": row[3],
                "created_at": row[4]
            })
        
        conn.close()
        
        return {
            "conflicts": conflicts,
            "total_count": len(conflicts),
            "message": "Conflicts will be resolved automatically where possible"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/resolve-conflict/{conflict_id}")
async def resolve_sync_conflict(conflict_id: str, resolution: Dict[str, Any]):
    """Manually resolve a sync conflict"""
    
    try:
        resolution_strategy = resolution.get("strategy")  # 'local_wins', 'remote_wins', 'merge'
        
        # Apply the resolution
        await offline_sync_engine._apply_conflict_resolution(conflict_id, resolution_strategy)
        
        return {
            "status": "success",
            "conflict_id": conflict_id,
            "resolution": resolution_strategy,
            "message": "Conflict resolved successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/demo-offline-workflow")
async def demo_offline_workflow():
    """Demonstrate the offline workflow capabilities"""
    
    return {
        "offline_capabilities": {
            "data_storage": "SQLite database stores all work locally",
            "photo_management": "Photos saved to local storage with metadata",
            "voice_recordings": "Voice notes stored with automatic transcription",
            "intelligent_sync": "Smart conflict resolution when back online",
            "no_data_loss": "All work preserved even during extended outages"
        },
        "sync_strategies": {
            "safety_critical": "Remote data wins (latest expert system updates)",
            "field_measurements": "Local data wins (worker has most accurate info)",
            "status_changes": "Most recent timestamp wins",
            "notes_comments": "Automatic merge of text content",
            "complex_conflicts": "Flagged for manual review"
        },
        "sap_integration": {
            "conflict_detection": "Compares timestamps and checksums",
            "field_level_comparison": "Identifies specific conflicting fields",
            "smart_resolution": "Applies business rules for resolution",
            "audit_trail": "Complete history of all changes and conflicts"
        },
        "worker_experience": {
            "seamless_operation": "Works identically online and offline",
            "visual_indicators": "Clear network status and sync progress",
            "confidence": "Workers know their data is safe",
            "productivity": "No work stoppage during network issues"
        }
    }

@router.post("/simulate-network-drop")
async def simulate_network_drop_scenario():
    """Simulate a network drop scenario for demonstration"""
    
    # Simulate a technician working offline
    device_id = "TABLET-SHOP-FLOOR-01"
    worker_id = "W-54f05833"  # Emma Rodriguez
    
    # 1. Store inspection offline
    inspection_data = {
        "product_id": "PROD-OFFLINE-TEST",
        "batch_number": "BATCH-NETWORK-DROP",
        "inspector_id": worker_id,
        "device_id": device_id,
        "production_line": "Line-B",
        "shift": "Day",
        "notes": "Created during network outage - testing offline capability"
    }
    
    inspection_record_id = await offline_sync_engine.store_offline_record(
        record_type="inspection",
        data=inspection_data,
        worker_id=worker_id,
        device_id=device_id
    )
    
    # 2. Store measurement offline
    measurement_data = {
        "inspection_id": inspection_record_id,
        "measurements": {
            "length": {"value": 10.05, "spec": "10.0 ± 0.05", "status": "pass"},
            "width": {"value": 5.02, "spec": "5.0 ± 0.03", "status": "pass"}
        },
        "device_id": device_id,
        "worker_id": worker_id,
        "timestamp": datetime.now().isoformat()
    }
    
    measurement_record_id = await offline_sync_engine.store_offline_record(
        record_type="measurement",
        data=measurement_data,
        worker_id=worker_id,
        device_id=device_id,
        parent_record_id=inspection_record_id
    )
    
    # 3. Store defect report offline
    defect_data = {
        "inspection_id": inspection_record_id,
        "defect_type": "surface",
        "description": "Minor scratch on surface - documented offline",
        "location": "Top-left corner",
        "severity": "low",
        "device_id": device_id,
        "worker_id": worker_id
    }
    
    defect_record_id = await offline_sync_engine.store_offline_record(
        record_type="defect",
        data=defect_data,
        worker_id=worker_id,
        device_id=device_id,
        parent_record_id=inspection_record_id
    )
    
    # Get offline status
    status = await offline_sync_engine.get_offline_status(device_id)
    
    return {
        "scenario": "Network Drop Simulation",
        "worker": "Emma Rodriguez (Quality Inspector)",
        "device": device_id,
        "work_completed_offline": {
            "inspection": inspection_record_id,
            "measurements": measurement_record_id,
            "defect_report": defect_record_id
        },
        "offline_status": status,
        "message": "All work saved locally - will sync automatically when network returns",
        "data_protection": "Zero data loss guaranteed",
        "worker_productivity": "No interruption to inspection workflow"
    }