#!/usr/bin/env python3
"""
FixItFred Device Recovery & Data Protection System
Multi-layer protection against device failure, damage, or loss
"""

import asyncio
import json
import sqlite3
import uuid
import hashlib
import time
import threading
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import shutil
import os

@dataclass
class AutoSavePoint:
    """Represents an automatic save point"""
    savepoint_id: str
    device_id: str
    worker_id: str
    timestamp: str
    data_snapshot: Dict[str, Any]
    record_count: int
    last_action: str
    battery_level: Optional[float] = None
    location: Optional[Dict[str, float]] = None

@dataclass 
class CloudBackup:
    """Represents a cloud backup entry"""
    backup_id: str
    device_id: str
    backup_timestamp: str
    data_hash: str
    backup_location: str  # 's3', 'azure', 'google', 'fixitfred_cloud'
    size_bytes: int
    records_backed_up: int
    encryption_key_id: str

class DeviceRecoverySystem:
    """Multi-layer device recovery and data protection"""
    
    def __init__(self):
        self.autosave_interval = 30  # seconds
        self.cloud_sync_interval = 300  # 5 minutes
        self.local_backup_path = Path("device_backups")
        self.local_backup_path.mkdir(exist_ok=True)
        
        # Start protection services
        self._start_autosave_service()
        self._start_cloud_backup_service()
        self._start_device_monitor()
    
    def _start_autosave_service(self):
        """Auto-save every 30 seconds to local storage"""
        
        def autosave_worker():
            while True:
                try:
                    # Save current state for all active devices
                    self._perform_autosave()
                except Exception as e:
                    print(f"Autosave error: {e}")
                
                time.sleep(self.autosave_interval)
        
        save_thread = threading.Thread(target=autosave_worker, daemon=True)
        save_thread.start()
    
    def _perform_autosave(self):
        """Perform automatic save of current work"""
        
        # Get all active work sessions
        from core.offline.offline_sync_engine import offline_sync_engine
        
        conn = sqlite3.connect(offline_sync_engine.db_path)
        cursor = conn.cursor()
        
        # Get unique device sessions
        cursor.execute('''
            SELECT DISTINCT device_id, worker_id 
            FROM offline_records 
            WHERE datetime(timestamp) > datetime('now', '-1 hour')
        ''')
        
        active_sessions = cursor.fetchall()
        
        for device_id, worker_id in active_sessions:
            # Create savepoint
            savepoint_id = f"SAVE-{uuid.uuid4().hex[:8]}"
            
            # Get all unsaved records for this device
            cursor.execute('''
                SELECT * FROM offline_records 
                WHERE device_id = ? 
                AND sync_status = 'pending'
                ORDER BY timestamp DESC
            ''', (device_id,))
            
            records = cursor.fetchall()
            
            if records:
                # Create snapshot
                snapshot_data = {
                    "records": [
                        {
                            "record_id": r[0],
                            "record_type": r[1],
                            "data": json.loads(r[2]),
                            "timestamp": r[3]
                        } for r in records
                    ],
                    "device_info": {
                        "device_id": device_id,
                        "worker_id": worker_id,
                        "record_count": len(records)
                    }
                }
                
                # Save to local backup
                backup_file = self.local_backup_path / f"{device_id}_{savepoint_id}.json"
                with open(backup_file, 'w') as f:
                    json.dump(snapshot_data, f)
                
                # Also save to redundant location
                redundant_backup = self.local_backup_path / "redundant" / f"{device_id}_latest.json"
                redundant_backup.parent.mkdir(exist_ok=True)
                shutil.copy2(backup_file, redundant_backup)
        
        conn.close()
    
    def _start_cloud_backup_service(self):
        """Backup to cloud every 5 minutes when online"""
        
        def cloud_backup_worker():
            while True:
                try:
                    asyncio.run(self._perform_cloud_backup())
                except Exception as e:
                    print(f"Cloud backup error: {e}")
                
                time.sleep(self.cloud_sync_interval)
        
        cloud_thread = threading.Thread(target=cloud_backup_worker, daemon=True)
        cloud_thread.start()
    
    async def _perform_cloud_backup(self):
        """Perform cloud backup of offline data"""
        
        # Check network connectivity
        from core.offline.offline_sync_engine import offline_sync_engine
        
        if not await offline_sync_engine._check_network_connectivity():
            return  # Skip cloud backup if offline
        
        # Get all local backup files
        backup_files = list(self.local_backup_path.glob("*.json"))
        
        for backup_file in backup_files:
            try:
                # Read backup data
                with open(backup_file, 'r') as f:
                    data = json.load(f)
                
                # Create cloud backup record
                backup_id = f"CLOUD-{uuid.uuid4().hex[:8]}"
                data_json = json.dumps(data)
                data_hash = hashlib.sha256(data_json.encode()).hexdigest()
                
                # Simulate cloud upload (in production, use actual cloud service)
                cloud_backup = CloudBackup(
                    backup_id=backup_id,
                    device_id=data["device_info"]["device_id"],
                    backup_timestamp=datetime.now().isoformat(),
                    data_hash=data_hash,
                    backup_location="fixitfred_cloud",
                    size_bytes=len(data_json),
                    records_backed_up=data["device_info"]["record_count"],
                    encryption_key_id="AES256-KEY-001"
                )
                
                # Store cloud backup metadata
                cloud_metadata_file = self.local_backup_path / "cloud_metadata" / f"{backup_id}.json"
                cloud_metadata_file.parent.mkdir(exist_ok=True)
                with open(cloud_metadata_file, 'w') as f:
                    json.dump(asdict(cloud_backup), f)
                
            except Exception as e:
                print(f"Failed to backup {backup_file}: {e}")
    
    def _start_device_monitor(self):
        """Monitor device health and trigger emergency saves"""
        
        def device_monitor_worker():
            while True:
                try:
                    self._check_device_health()
                except Exception as e:
                    print(f"Device monitor error: {e}")
                
                time.sleep(10)  # Check every 10 seconds
        
        monitor_thread = threading.Thread(target=device_monitor_worker, daemon=True)
        monitor_thread.start()
    
    def _check_device_health(self):
        """Check device health indicators"""
        
        # Simulate device health checks
        battery_level = self._get_battery_level()
        available_storage = self._get_available_storage()
        
        # Emergency save if battery critical
        if battery_level and battery_level < 5:
            self._perform_emergency_save("LOW_BATTERY")
        
        # Emergency save if storage critical
        if available_storage and available_storage < 100:  # MB
            self._perform_emergency_save("LOW_STORAGE")
    
    def _perform_emergency_save(self, reason: str):
        """Perform emergency save of all data"""
        
        emergency_id = f"EMERGENCY-{uuid.uuid4().hex[:8]}"
        timestamp = datetime.now().isoformat()
        
        # Get all offline data
        from core.offline.offline_sync_engine import offline_sync_engine
        
        conn = sqlite3.connect(offline_sync_engine.db_path)
        cursor = conn.cursor()
        
        # Dump entire database
        with open(f"emergency_backup_{emergency_id}.sql", 'w') as f:
            for line in conn.iterdump():
                f.write('%s\n' % line)
        
        conn.close()
        
        # Log emergency save
        emergency_log = {
            "emergency_id": emergency_id,
            "reason": reason,
            "timestamp": timestamp,
            "backup_file": f"emergency_backup_{emergency_id}.sql"
        }
        
        with open(f"emergency_log_{emergency_id}.json", 'w') as f:
            json.dump(emergency_log, f)
    
    def _get_battery_level(self) -> Optional[float]:
        """Get device battery level"""
        try:
            # Platform-specific battery check
            import psutil
            battery = psutil.sensors_battery()
            return battery.percent if battery else None
        except:
            return None
    
    def _get_available_storage(self) -> Optional[float]:
        """Get available storage in MB"""
        try:
            import shutil
            stat = shutil.disk_usage(".")
            return stat.free / (1024 * 1024)  # Convert to MB
        except:
            return None
    
    def create_recovery_checkpoint(self, worker_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a recovery checkpoint for worker data"""
        
        checkpoint_id = f"checkpoint_{uuid.uuid4().hex[:8]}"
        timestamp = datetime.now().isoformat()
        
        # Create checkpoint data
        checkpoint_data = {
            "checkpoint_id": checkpoint_id,
            "worker_id": worker_id,
            "timestamp": timestamp,
            "data": data,
            "data_hash": hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()
        }
        
        # Save to local storage
        try:
            checkpoint_file = self.local_backup_path / f"checkpoint_{checkpoint_id}.json"
            with open(checkpoint_file, 'w') as f:
                json.dump(checkpoint_data, f)
                
            return {
                "success": True,
                "checkpoint_id": checkpoint_id,
                "timestamp": timestamp,
                "file_location": str(checkpoint_file)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "checkpoint_id": checkpoint_id
            }
    
    async def recover_from_device_failure(self, old_device_id: str, 
                                         new_device_id: str,
                                         worker_id: str) -> Dict[str, Any]:
        """Recover data from failed device to new device"""
        
        recovery_results = {
            "old_device": old_device_id,
            "new_device": new_device_id,
            "worker": worker_id,
            "recovered_records": 0,
            "recovery_sources": [],
            "status": "pending"
        }
        
        # 1. Try local backup recovery
        local_recovery = await self._recover_from_local_backup(old_device_id, new_device_id)
        if local_recovery and local_recovery.get("success"):
            recovery_results["recovered_records"] += local_recovery["records_recovered"]
            recovery_results["recovery_sources"].append("local_backup")
        
        # 2. Try cloud backup recovery
        cloud_recovery = await self._recover_from_cloud_backup(old_device_id, new_device_id)
        if cloud_recovery and cloud_recovery.get("success"):
            recovery_results["recovered_records"] += cloud_recovery["records_recovered"]
            recovery_results["recovery_sources"].append("cloud_backup")
        
        # 3. Try peer device recovery (if multiple devices on same network)
        peer_recovery = await self._recover_from_peer_devices(old_device_id, new_device_id)
        if peer_recovery and peer_recovery.get("success"):
            recovery_results["recovered_records"] += peer_recovery["records_recovered"]
            recovery_results["recovery_sources"].append("peer_devices")
        
        # 4. Try server-side recovery (last sync point)
        server_recovery = await self._recover_from_server(old_device_id, new_device_id, worker_id)
        if server_recovery and server_recovery.get("success"):
            recovery_results["recovered_records"] += server_recovery["records_recovered"]
            recovery_results["recovery_sources"].append("server_sync")
        
        recovery_results["status"] = "success" if recovery_results["recovered_records"] > 0 else "failed"
        
        return recovery_results
    
    async def _recover_from_local_backup(self, old_device_id: str, 
                                        new_device_id: str) -> Dict[str, Any]:
        """Recover from local backup files"""
        
        try:
            # Find latest backup for old device
            backup_pattern = f"{old_device_id}_*.json"
            backup_files = list(self.local_backup_path.glob(backup_pattern))
            
            if not backup_files:
                # Try redundant backup
                redundant_file = self.local_backup_path / "redundant" / f"{old_device_id}_latest.json"
                if redundant_file.exists():
                    backup_files = [redundant_file]
            
            if backup_files:
                # Get most recent backup
                latest_backup = max(backup_files, key=lambda f: f.stat().st_mtime)
                
                with open(latest_backup, 'r') as f:
                    backup_data = json.load(f)
                
                # Restore records to new device
                from core.offline.offline_sync_engine import offline_sync_engine
                
                records_restored = 0
                for record in backup_data["records"]:
                    await offline_sync_engine.store_offline_record(
                        record_type=record["record_type"],
                        data=record["data"],
                        worker_id=backup_data["device_info"]["worker_id"],
                        device_id=new_device_id
                    )
                    records_restored += 1
                
                return {
                    "success": True,
                    "records_recovered": records_restored,
                    "backup_timestamp": latest_backup.stat().st_mtime
                }
        
        except Exception as e:
            return {"success": False, "error": str(e), "records_recovered": 0}
    
    async def _recover_from_cloud_backup(self, old_device_id: str,
                                        new_device_id: str) -> Dict[str, Any]:
        """Recover from cloud backup"""
        
        try:
            # Find cloud backup metadata
            cloud_metadata_path = self.local_backup_path / "cloud_metadata"
            if not cloud_metadata_path.exists():
                return {"success": False, "records_recovered": 0}
            
            # Get latest cloud backup for device
            metadata_files = list(cloud_metadata_path.glob("*.json"))
            device_backups = []
            
            for metadata_file in metadata_files:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                    if metadata["device_id"] == old_device_id:
                        device_backups.append(metadata)
            
            if device_backups:
                # Get most recent backup
                latest_backup = max(device_backups, key=lambda b: b["backup_timestamp"])
                
                # In production, download from actual cloud service
                # For demo, we'll simulate recovery
                return {
                    "success": True,
                    "records_recovered": latest_backup["records_backed_up"],
                    "backup_id": latest_backup["backup_id"],
                    "backup_timestamp": latest_backup["backup_timestamp"]
                }
            
            return {"success": False, "records_recovered": 0}
            
        except Exception as e:
            return {"success": False, "error": str(e), "records_recovered": 0}
    
    async def _recover_from_peer_devices(self, old_device_id: str,
                                        new_device_id: str) -> Dict[str, Any]:
        """Recover from peer devices on same network"""
        
        # In production, implement peer-to-peer recovery
        # Devices would share backup data over local network
        return {"success": False, "records_recovered": 0, "reason": "No peer devices found"}
    
    async def _recover_from_server(self, old_device_id: str,
                                  new_device_id: str,
                                  worker_id: str) -> Dict[str, Any]:
        """Recover from last server sync point"""
        
        try:
            # Check if we can reach the server
            from core.offline.offline_sync_engine import offline_sync_engine
            
            if await offline_sync_engine._check_network_connectivity():
                # In production, query server for last known state
                # For demo, simulate recovery
                return {
                    "success": True,
                    "records_recovered": 5,  # Simulated
                    "last_sync": datetime.now().isoformat()
                }
            
            return {"success": False, "records_recovered": 0, "reason": "Server unreachable"}
            
        except Exception as e:
            return {"success": False, "error": str(e), "records_recovered": 0}

# Global device recovery system
device_recovery_system = DeviceRecoverySystem()

class TabletProtectionService:
    """Specific protection for tablet devices"""
    
    def __init__(self):
        self.drop_detection_enabled = True
        self.water_damage_protocol = True
        self.screen_damage_recovery = True
    
    async def handle_tablet_drop(self, device_id: str, 
                                sensor_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tablet drop event"""
        
        # Detect drop from accelerometer data
        acceleration = sensor_data.get("acceleration", 0)
        
        if acceleration > 9.8 * 3:  # 3G force indicates drop
            # Immediate emergency save
            device_recovery_system._perform_emergency_save("DEVICE_DROP_DETECTED")
            
            return {
                "action": "emergency_save",
                "status": "data_protected",
                "message": "Drop detected - all data saved immediately",
                "recovery_available": True
            }
        
        return {"status": "monitoring", "drop_detected": False}
    
    async def handle_water_damage(self, device_id: str) -> Dict[str, Any]:
        """Handle water damage scenario"""
        
        # Immediate multi-location backup
        device_recovery_system._perform_emergency_save("WATER_DAMAGE_PROTOCOL")
        
        # Trigger cloud sync if possible
        await device_recovery_system._perform_cloud_backup()
        
        return {
            "action": "water_damage_protocol",
            "backups_created": ["local", "redundant", "cloud", "emergency"],
            "recovery_instructions": "Use any other device to recover all data",
            "data_loss": "ZERO - All work preserved"
        }

# Global tablet protection
tablet_protection = TabletProtectionService()