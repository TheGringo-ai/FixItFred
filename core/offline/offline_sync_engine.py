#!/usr/bin/env python3
"""
FixItFred Offline-First Architecture with Intelligent Sync
Critical for manufacturing environments where network connectivity is unreliable
"""

import asyncio
import json
import sqlite3
import uuid
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import threading
import queue
import time

@dataclass
class OfflineRecord:
    """Represents a data record stored offline"""
    record_id: str
    record_type: str  # 'inspection', 'measurement', 'photo', 'defect', etc.
    data: Dict[str, Any]
    timestamp: str
    worker_id: str
    device_id: str
    checksum: str
    sync_status: str  # 'pending', 'synced', 'conflict', 'failed'
    parent_record_id: Optional[str] = None
    operation: str = 'create'  # 'create', 'update', 'delete'

@dataclass
class SyncConflict:
    """Represents a sync conflict that needs resolution"""
    conflict_id: str
    local_record: OfflineRecord
    remote_record: Dict[str, Any]
    conflict_type: str  # 'data', 'timing', 'permission'
    resolution_strategy: str  # 'local_wins', 'remote_wins', 'merge', 'manual'
    created_at: str

class OfflineSyncEngine:
    """Manages offline data storage and intelligent synchronization"""
    
    def __init__(self, db_path: str = "offline_data.db"):
        self.db_path = db_path
        self.sync_queue = queue.Queue()
        self.conflict_resolver = ConflictResolver()
        self.photo_manager = OfflinePhotoManager()
        self.voice_recorder = OfflineVoiceRecorder()
        self._init_database()
        self._start_background_sync()
    
    def _init_database(self):
        """Initialize offline SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Offline records table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS offline_records (
                record_id TEXT PRIMARY KEY,
                record_type TEXT NOT NULL,
                data TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                worker_id TEXT NOT NULL,
                device_id TEXT NOT NULL,
                checksum TEXT NOT NULL,
                sync_status TEXT DEFAULT 'pending',
                parent_record_id TEXT,
                operation TEXT DEFAULT 'create',
                retry_count INTEGER DEFAULT 0,
                last_sync_attempt TEXT
            )
        ''')
        
        # Sync conflicts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_conflicts (
                conflict_id TEXT PRIMARY KEY,
                local_record_id TEXT NOT NULL,
                remote_data TEXT NOT NULL,
                conflict_type TEXT NOT NULL,
                resolution_strategy TEXT,
                created_at TEXT NOT NULL,
                resolved_at TEXT,
                resolved_by TEXT
            )
        ''')
        
        # Device sync state table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS device_sync_state (
                device_id TEXT PRIMARY KEY,
                last_sync_timestamp TEXT,
                network_status TEXT DEFAULT 'offline',
                pending_records_count INTEGER DEFAULT 0,
                failed_syncs_count INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
    
    async def store_offline_record(self, record_type: str, data: Dict[str, Any], 
                                 worker_id: str, device_id: str, 
                                 parent_record_id: Optional[str] = None,
                                 operation: str = 'create') -> str:
        """Store a record for offline use"""
        
        record_id = f"OFFLINE-{uuid.uuid4().hex[:8]}"
        timestamp = datetime.now().isoformat()
        
        # Create checksum for data integrity
        data_json = json.dumps(data, sort_keys=True)
        checksum = hashlib.md5(data_json.encode()).hexdigest()
        
        record = OfflineRecord(
            record_id=record_id,
            record_type=record_type,
            data=data,
            timestamp=timestamp,
            worker_id=worker_id,
            device_id=device_id,
            checksum=checksum,
            sync_status='pending',
            parent_record_id=parent_record_id,
            operation=operation
        )
        
        # Store in SQLite
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO offline_records 
            (record_id, record_type, data, timestamp, worker_id, device_id, 
             checksum, sync_status, parent_record_id, operation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            record.record_id, record.record_type, json.dumps(record.data),
            record.timestamp, record.worker_id, record.device_id,
            record.checksum, record.sync_status, record.parent_record_id,
            record.operation
        ))
        conn.commit()
        conn.close()
        
        # Add to sync queue if network is available
        if await self._check_network_connectivity():
            self.sync_queue.put(record_id)
        
        return record_id
    
    async def sync_when_online(self) -> Dict[str, Any]:
        """Sync all pending offline records when network comes back"""
        
        if not await self._check_network_connectivity():
            return {"status": "offline", "message": "Network not available"}
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all pending records
        cursor.execute('''
            SELECT * FROM offline_records 
            WHERE sync_status = 'pending' 
            ORDER BY timestamp ASC
        ''')
        
        pending_records = cursor.fetchall()
        conn.close()
        
        sync_results = {
            "total_records": len(pending_records),
            "synced": 0,
            "conflicts": 0,
            "failures": 0,
            "details": []
        }
        
        for record_row in pending_records:
            record_id = record_row[0]
            record_type = record_row[1]
            data = json.loads(record_row[2])
            
            try:
                sync_result = await self._sync_single_record(record_id, record_type, data)
                
                if sync_result["status"] == "success":
                    sync_results["synced"] += 1
                    await self._mark_record_synced(record_id)
                elif sync_result["status"] == "conflict":
                    sync_results["conflicts"] += 1
                    await self._handle_sync_conflict(record_id, sync_result["conflict_data"])
                else:
                    sync_results["failures"] += 1
                    await self._mark_sync_failed(record_id, sync_result.get("error"))
                
                sync_results["details"].append({
                    "record_id": record_id,
                    "type": record_type,
                    "status": sync_result["status"]
                })
                
            except Exception as e:
                sync_results["failures"] += 1
                sync_results["details"].append({
                    "record_id": record_id,
                    "type": record_type,
                    "status": "error",
                    "error": str(e)
                })
        
        return sync_results
    
    async def _sync_single_record(self, record_id: str, record_type: str, 
                                data: Dict[str, Any]) -> Dict[str, Any]:
        """Sync a single record to the server"""
        
        # Different sync strategies based on record type
        if record_type == "inspection":
            return await self._sync_inspection_record(record_id, data)
        elif record_type == "measurement":
            return await self._sync_measurement_record(record_id, data)
        elif record_type == "photo":
            return await self._sync_photo_record(record_id, data)
        elif record_type == "defect":
            return await self._sync_defect_record(record_id, data)
        else:
            return await self._sync_generic_record(record_id, record_type, data)
    
    async def _sync_inspection_record(self, record_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sync inspection record with conflict detection"""
        
        # Check if inspection was modified remotely while offline
        inspection_id = data.get("inspection_id")
        if inspection_id and not inspection_id.startswith("OFFLINE-"):
            # This is an update to existing inspection
            remote_inspection = await self._fetch_remote_inspection(inspection_id)
            
            if remote_inspection:
                # Check for conflicts
                local_timestamp = datetime.fromisoformat(data.get("updated_at", data.get("created_at")))
                remote_timestamp = datetime.fromisoformat(remote_inspection.get("updated_at"))
                
                if remote_timestamp > local_timestamp:
                    # Potential conflict - remote was modified after our local copy
                    conflict_data = {
                        "local_data": data,
                        "remote_data": remote_inspection,
                        "conflict_fields": self._detect_field_conflicts(data, remote_inspection)
                    }
                    return {"status": "conflict", "conflict_data": conflict_data}
        
        # No conflict, proceed with sync
        try:
            if inspection_id and not inspection_id.startswith("OFFLINE-"):
                # Update existing inspection
                result = await self._update_remote_inspection(inspection_id, data)
            else:
                # Create new inspection
                result = await self._create_remote_inspection(data)
            
            return {"status": "success", "remote_id": result.get("inspection_id")}
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _detect_field_conflicts(self, local_data: Dict[str, Any], 
                              remote_data: Dict[str, Any]) -> List[str]:
        """Detect which fields have conflicts between local and remote data"""
        
        conflicts = []
        
        # Compare key fields that could cause conflicts
        conflict_fields = ["status", "measurements", "defects", "notes", "photos"]
        
        for field in conflict_fields:
            local_value = local_data.get(field)
            remote_value = remote_data.get(field)
            
            if local_value != remote_value:
                conflicts.append(field)
        
        return conflicts
    
    async def _handle_sync_conflict(self, record_id: str, conflict_data: Dict[str, Any]):
        """Handle sync conflict using intelligent resolution strategies"""
        
        conflict_id = f"CONFLICT-{uuid.uuid4().hex[:8]}"
        
        # Determine resolution strategy
        resolution_strategy = await self.conflict_resolver.determine_resolution_strategy(
            conflict_data["local_data"],
            conflict_data["remote_data"],
            conflict_data["conflict_fields"]
        )
        
        conflict = SyncConflict(
            conflict_id=conflict_id,
            local_record=await self._get_offline_record(record_id),
            remote_record=conflict_data["remote_data"],
            conflict_type="data",
            resolution_strategy=resolution_strategy,
            created_at=datetime.now().isoformat()
        )
        
        # Store conflict for review
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO sync_conflicts 
            (conflict_id, local_record_id, remote_data, conflict_type, 
             resolution_strategy, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            conflict.conflict_id, record_id, json.dumps(conflict_data["remote_data"]),
            conflict.conflict_type, conflict.resolution_strategy, conflict.created_at
        ))
        conn.commit()
        conn.close()
        
        # Apply automatic resolution if strategy is available
        if resolution_strategy in ["local_wins", "remote_wins", "merge"]:
            await self._apply_conflict_resolution(conflict_id, resolution_strategy)
    
    async def _check_network_connectivity(self) -> bool:
        """Check if network connection is available"""
        try:
            # Try to ping the FixItFred server
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get("http://localhost:8080/api/system/status", 
                                     timeout=aiohttp.ClientTimeout(total=5)) as response:
                    return response.status == 200
        except:
            return False
    
    def _start_background_sync(self):
        """Start background thread for automatic syncing"""
        def sync_worker():
            while True:
                try:
                    if asyncio.run(self._check_network_connectivity()):
                        # Process sync queue
                        while not self.sync_queue.empty():
                            record_id = self.sync_queue.get(timeout=1)
                            # Process sync in background
                            asyncio.run(self._process_background_sync(record_id))
                except:
                    pass
                
                time.sleep(30)  # Check every 30 seconds
        
        sync_thread = threading.Thread(target=sync_worker, daemon=True)
        sync_thread.start()
    
    async def get_offline_status(self, device_id: str) -> Dict[str, Any]:
        """Get current offline status for a device"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Count pending records
        cursor.execute('''
            SELECT COUNT(*) FROM offline_records 
            WHERE device_id = ? AND sync_status = 'pending'
        ''', (device_id,))
        pending_count = cursor.fetchone()[0]
        
        # Count conflicts
        cursor.execute('''
            SELECT COUNT(*) FROM sync_conflicts 
            WHERE resolved_at IS NULL
        ''')
        conflicts_count = cursor.fetchone()[0]
        
        # Get last sync time
        cursor.execute('''
            SELECT last_sync_timestamp FROM device_sync_state 
            WHERE device_id = ?
        ''', (device_id,))
        last_sync_row = cursor.fetchone()
        last_sync = last_sync_row[0] if last_sync_row else None
        
        conn.close()
        
        network_available = await self._check_network_connectivity()
        
        return {
            "device_id": device_id,
            "network_status": "online" if network_available else "offline",
            "pending_records": pending_count,
            "unresolved_conflicts": conflicts_count,
            "last_sync": last_sync,
            "can_work_offline": True,
            "data_protection": "All work saved locally with automatic sync when online"
        }

class ConflictResolver:
    """Intelligent conflict resolution for data synchronization"""
    
    async def determine_resolution_strategy(self, local_data: Dict[str, Any], 
                                          remote_data: Dict[str, Any], 
                                          conflict_fields: List[str]) -> str:
        """Determine the best strategy to resolve conflicts"""
        
        # Priority-based resolution rules
        
        # 1. Safety-critical fields: remote wins (latest from expert system)
        safety_fields = ["safety_status", "hazard_level", "compliance_status"]
        if any(field in conflict_fields for field in safety_fields):
            return "remote_wins"
        
        # 2. Measurement data: local wins (worker in field has best data)
        measurement_fields = ["measurements", "readings", "sensor_data"]
        if any(field in conflict_fields for field in measurement_fields):
            return "local_wins"
        
        # 3. Status changes: most recent wins
        status_fields = ["status", "completion_status", "approval_status"]
        if any(field in conflict_fields for field in status_fields):
            local_time = datetime.fromisoformat(local_data.get("updated_at", local_data.get("created_at")))
            remote_time = datetime.fromisoformat(remote_data.get("updated_at", remote_data.get("created_at")))
            return "local_wins" if local_time > remote_time else "remote_wins"
        
        # 4. Notes and comments: merge
        text_fields = ["notes", "comments", "observations"]
        if any(field in conflict_fields for field in text_fields):
            return "merge"
        
        # 5. Default: manual review required
        return "manual"

class OfflinePhotoManager:
    """Manages photos taken offline"""
    
    def __init__(self, storage_path: str = "offline_photos"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
    
    async def store_photo_offline(self, photo_data: bytes, 
                                record_id: str, worker_id: str) -> str:
        """Store photo offline with metadata"""
        
        photo_id = f"PHOTO-{uuid.uuid4().hex[:8]}"
        photo_path = self.storage_path / f"{photo_id}.jpg"
        
        # Save photo file
        with open(photo_path, 'wb') as f:
            f.write(photo_data)
        
        # Store metadata
        metadata = {
            "photo_id": photo_id,
            "record_id": record_id,
            "worker_id": worker_id,
            "timestamp": datetime.now().isoformat(),
            "file_path": str(photo_path),
            "file_size": len(photo_data),
            "sync_status": "pending"
        }
        
        metadata_path = self.storage_path / f"{photo_id}_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f)
        
        return photo_id

class OfflineVoiceRecorder:
    """Manages voice recordings taken offline"""
    
    def __init__(self, storage_path: str = "offline_voice"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
    
    async def store_voice_offline(self, audio_data: bytes, 
                                worker_id: str, transcript: str = "") -> str:
        """Store voice recording offline"""
        
        voice_id = f"VOICE-{uuid.uuid4().hex[:8]}"
        voice_path = self.storage_path / f"{voice_id}.wav"
        
        # Save audio file
        with open(voice_path, 'wb') as f:
            f.write(audio_data)
        
        # Store metadata with transcript
        metadata = {
            "voice_id": voice_id,
            "worker_id": worker_id,
            "timestamp": datetime.now().isoformat(),
            "file_path": str(voice_path),
            "transcript": transcript,
            "sync_status": "pending"
        }
        
        metadata_path = self.storage_path / f"{voice_id}_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f)
        
        return voice_id

# Global offline sync engine instance
offline_sync_engine = OfflineSyncEngine()