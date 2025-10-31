#!/usr/bin/env python3
"""
FixItFred Universal Memory & Document Management System
Core module that plugs into all companies for AI-customizable memory and storage
"""

import asyncio
import json
import sqlite3
import uuid
import hashlib
import mimetypes
import os
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import base64
from enum import Enum

class DocumentType(Enum):
    """Supported document types"""
    PDF = "pdf"
    WORD = "docx"
    EXCEL = "xlsx" 
    POWERPOINT = "pptx"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    TEXT = "txt"
    CSV = "csv"
    XML = "xml"
    JSON = "json"
    CAD = "cad"
    TECHNICAL_DRAWING = "dwg"
    MANUAL = "manual"
    POLICY = "policy"
    PROCEDURE = "procedure"
    FORM = "form"
    TEMPLATE = "template"

class StorageLocation(Enum):
    """Storage location options"""
    LOCAL_SQLITE = "local_sqlite"
    CLOUD_S3 = "cloud_s3"
    AZURE_BLOB = "azure_blob"
    GOOGLE_DRIVE = "google_drive"
    COMPANY_NAS = "company_nas"
    HYBRID = "hybrid"

@dataclass
class DocumentMetadata:
    """Document metadata and indexing"""
    document_id: str
    filename: str
    file_type: DocumentType
    size_bytes: int
    created_at: str
    modified_at: str
    uploaded_by: str
    company_id: str
    department: str
    
    # AI-powered metadata
    ai_summary: str
    ai_tags: List[str]
    ai_category: str
    ai_importance_score: float  # 0-1
    
    # Access and security
    access_level: str  # public, department, private, confidential
    permissions: Dict[str, List[str]]  # role -> [read, write, delete]
    encryption_status: bool
    
    # Version control
    version: str
    parent_document_id: Optional[str]
    is_latest_version: bool
    
    # Business context
    related_modules: List[str]  # quality, maintenance, safety, etc.
    related_processes: List[str]
    related_workers: List[str]
    
    # Search optimization
    search_keywords: List[str]
    full_text_content: str  # AI-extracted text content
    storage_location: StorageLocation
    storage_path: str

@dataclass
class MemoryContext:
    """AI memory context for intelligent retrieval"""
    context_id: str
    company_id: str
    context_type: str  # conversation, task, project, incident
    participants: List[str]  # worker_ids
    start_time: str
    end_time: Optional[str]
    
    # Memory content
    conversation_history: List[Dict[str, Any]]
    decision_points: List[Dict[str, Any]]
    action_items: List[Dict[str, Any]]
    referenced_documents: List[str]  # document_ids
    
    # AI analysis
    ai_summary: str
    ai_insights: List[str]
    ai_recommendations: List[str]
    importance_score: float
    
    # Relationships
    related_contexts: List[str]
    spawned_tasks: List[str]
    linked_incidents: List[str]

class UniversalMemorySystem:
    """Core memory and document management system for all companies"""
    
    def __init__(self, company_id: str):
        self.company_id = company_id
        self.db_path = f"data/memory_{company_id}.db"
        self.storage_path = Path(f"data/documents/{company_id}")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._initialize_database()
        
        # AI configuration - customizable per company
        self.ai_config = {
            "auto_tagging": True,
            "content_analysis": True,
            "smart_categorization": True,
            "relationship_detection": True,
            "duplicate_detection": True,
            "retention_policies": True
        }
    
    def _initialize_database(self):
        """Initialize SQLite database with optimized schema"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Documents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                document_id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                file_type TEXT NOT NULL,
                size_bytes INTEGER,
                created_at TEXT,
                modified_at TEXT,
                uploaded_by TEXT,
                company_id TEXT,
                department TEXT,
                ai_summary TEXT,
                ai_tags TEXT,  -- JSON array
                ai_category TEXT,
                ai_importance_score REAL,
                access_level TEXT,
                permissions TEXT,  -- JSON object
                encryption_status BOOLEAN,
                version TEXT,
                parent_document_id TEXT,
                is_latest_version BOOLEAN,
                related_modules TEXT,  -- JSON array
                related_processes TEXT,  -- JSON array
                related_workers TEXT,  -- JSON array
                search_keywords TEXT,  -- JSON array
                full_text_content TEXT,
                storage_location TEXT,
                storage_path TEXT
            )
        ''')
        
        # Memory contexts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memory_contexts (
                context_id TEXT PRIMARY KEY,
                company_id TEXT,
                context_type TEXT,
                participants TEXT,  -- JSON array
                start_time TEXT,
                end_time TEXT,
                conversation_history TEXT,  -- JSON array
                decision_points TEXT,  -- JSON array
                action_items TEXT,  -- JSON array
                referenced_documents TEXT,  -- JSON array
                ai_summary TEXT,
                ai_insights TEXT,  -- JSON array
                ai_recommendations TEXT,  -- JSON array
                importance_score REAL,
                related_contexts TEXT,  -- JSON array
                spawned_tasks TEXT,  -- JSON array
                linked_incidents TEXT  -- JSON array
            )
        ''')
        
        # Document versions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS document_versions (
                version_id TEXT PRIMARY KEY,
                document_id TEXT,
                version_number TEXT,
                created_at TEXT,
                created_by TEXT,
                change_summary TEXT,
                storage_path TEXT,
                FOREIGN KEY (document_id) REFERENCES documents (document_id)
            )
        ''')
        
        # Search index table for full-text search
        cursor.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS document_search 
            USING fts5(document_id, filename, content, tags, category)
        ''')
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_documents_company ON documents(company_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_documents_type ON documents(file_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_documents_department ON documents(department)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_documents_importance ON documents(ai_importance_score)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_contexts_company ON memory_contexts(company_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_contexts_type ON memory_contexts(context_type)')
        
        conn.commit()
        conn.close()
    
    async def upload_document(self, file_data: bytes, filename: str, 
                            uploaded_by: str, department: str,
                            custom_tags: List[str] = None,
                            ai_prompt: str = None) -> DocumentMetadata:
        """Upload and process document with AI analysis"""
        
        document_id = f"DOC-{uuid.uuid4().hex[:8]}"
        file_type = self._detect_file_type(filename)
        
        # Store file
        storage_path = self.storage_path / f"{document_id}_{filename}"
        with open(storage_path, 'wb') as f:
            f.write(file_data)
        
        # AI processing
        ai_analysis = await self._ai_analyze_document(file_data, filename, file_type, ai_prompt)
        
        # Create metadata
        metadata = DocumentMetadata(
            document_id=document_id,
            filename=filename,
            file_type=file_type,
            size_bytes=len(file_data),
            created_at=datetime.now().isoformat(),
            modified_at=datetime.now().isoformat(),
            uploaded_by=uploaded_by,
            company_id=self.company_id,
            department=department,
            ai_summary=ai_analysis["summary"],
            ai_tags=ai_analysis["tags"] + (custom_tags or []),
            ai_category=ai_analysis["category"],
            ai_importance_score=ai_analysis["importance_score"],
            access_level="department",  # Default, can be customized
            permissions=self._default_permissions(department),
            encryption_status=False,  # Can be enabled
            version="1.0",
            parent_document_id=None,
            is_latest_version=True,
            related_modules=ai_analysis["related_modules"],
            related_processes=ai_analysis["related_processes"],
            related_workers=[],
            search_keywords=ai_analysis["keywords"],
            full_text_content=ai_analysis["content"],
            storage_location=StorageLocation.LOCAL_SQLITE,
            storage_path=str(storage_path)
        )
        
        # Save to database
        await self._save_document_metadata(metadata)
        
        # Update search index
        await self._update_search_index(metadata)
        
        return metadata
    
    async def _ai_analyze_document(self, file_data: bytes, filename: str, 
                                 file_type: DocumentType, ai_prompt: str = None) -> Dict[str, Any]:
        """AI-powered document analysis and metadata extraction"""
        
        # Simulate AI analysis (replace with actual AI model)
        content = ""
        
        # Extract text content based on file type
        if file_type == DocumentType.PDF:
            content = self._extract_pdf_text(file_data)
        elif file_type == DocumentType.WORD:
            content = self._extract_docx_text(file_data)
        elif file_type == DocumentType.TEXT:
            content = file_data.decode('utf-8')
        elif file_type == DocumentType.JSON:
            content = json.dumps(json.loads(file_data.decode('utf-8')), indent=2)
        
        # AI analysis
        analysis = {
            "summary": f"AI-generated summary of {filename}",
            "tags": self._ai_generate_tags(content, filename),
            "category": self._ai_categorize_document(content, filename),
            "importance_score": self._ai_calculate_importance(content),
            "related_modules": self._ai_find_related_modules(content),
            "related_processes": self._ai_find_related_processes(content),
            "keywords": self._ai_extract_keywords(content),
            "content": content[:5000]  # First 5000 chars for search
        }
        
        # Apply custom AI prompt if provided
        if ai_prompt:
            analysis = await self._apply_custom_ai_prompt(analysis, ai_prompt, content)
        
        return analysis
    
    def _ai_generate_tags(self, content: str, filename: str) -> List[str]:
        """AI-generated tags based on content analysis"""
        tags = []
        
        # Basic keyword extraction
        keywords = content.lower().split()
        common_terms = {
            "quality": ["quality", "inspection", "defect", "compliance"],
            "safety": ["safety", "hazard", "risk", "incident"],
            "maintenance": ["maintenance", "repair", "equipment", "failure"],
            "training": ["training", "procedure", "manual", "guide"],
            "policy": ["policy", "procedure", "regulation", "standard"]
        }
        
        for category, terms in common_terms.items():
            if any(term in keywords for term in terms):
                tags.append(category)
        
        # Add file-based tags
        if "manual" in filename.lower():
            tags.append("manual")
        if "policy" in filename.lower():
            tags.append("policy")
        if "sop" in filename.lower():
            tags.append("standard_operating_procedure")
        
        return list(set(tags))
    
    def _ai_categorize_document(self, content: str, filename: str) -> str:
        """AI categorization of document"""
        content_lower = content.lower()
        filename_lower = filename.lower()
        
        if any(term in content_lower for term in ["policy", "regulation", "compliance"]):
            return "policy_document"
        elif any(term in content_lower for term in ["manual", "instruction", "guide"]):
            return "training_material"
        elif any(term in content_lower for term in ["quality", "inspection", "audit"]):
            return "quality_document"
        elif any(term in content_lower for term in ["safety", "hazard", "risk"]):
            return "safety_document"
        elif any(term in content_lower for term in ["maintenance", "repair", "equipment"]):
            return "maintenance_document"
        elif "form" in filename_lower or "template" in filename_lower:
            return "form_template"
        else:
            return "general_document"
    
    def _ai_calculate_importance(self, content: str) -> float:
        """AI-calculated importance score"""
        importance_indicators = {
            "critical": 1.0,
            "urgent": 0.9,
            "important": 0.8,
            "policy": 0.9,
            "safety": 0.95,
            "compliance": 0.85,
            "regulation": 0.9
        }
        
        content_lower = content.lower()
        max_score = 0.0
        
        for indicator, score in importance_indicators.items():
            if indicator in content_lower:
                max_score = max(max_score, score)
        
        # Base score for any document
        return max(max_score, 0.5)
    
    def _ai_find_related_modules(self, content: str) -> List[str]:
        """Find related FixItFred modules"""
        module_keywords = {
            "quality": ["quality", "inspection", "defect", "compliance", "audit"],
            "maintenance": ["maintenance", "repair", "equipment", "preventive"],
            "safety": ["safety", "hazard", "risk", "incident", "accident"],
            "operations": ["operation", "production", "workflow", "process"],
            "training": ["training", "education", "skill", "competency"],
            "analytics": ["data", "analysis", "metric", "kpi", "report"]
        }
        
        content_lower = content.lower()
        related = []
        
        for module, keywords in module_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                related.append(module)
        
        return related
    
    def _ai_find_related_processes(self, content: str) -> List[str]:
        """Find related business processes"""
        processes = []
        content_lower = content.lower()
        
        process_mapping = {
            "onboarding": ["onboard", "orientation", "new employee"],
            "inspection": ["inspect", "check", "verify", "examine"],
            "approval": ["approve", "authorize", "sign off"],
            "reporting": ["report", "document", "record"],
            "escalation": ["escalate", "urgent", "critical"]
        }
        
        for process, keywords in process_mapping.items():
            if any(keyword in content_lower for keyword in keywords):
                processes.append(process)
        
        return processes
    
    def _ai_extract_keywords(self, content: str) -> List[str]:
        """Extract searchable keywords"""
        # Simple keyword extraction (replace with advanced NLP)
        words = content.lower().split()
        
        # Filter out common words and get important terms
        stopwords = {"the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        keywords = [word for word in words if len(word) > 3 and word not in stopwords]
        
        # Get most frequent terms
        from collections import Counter
        word_freq = Counter(keywords)
        return [word for word, freq in word_freq.most_common(20)]
    
    async def _apply_custom_ai_prompt(self, analysis: Dict[str, Any], 
                                    ai_prompt: str, content: str) -> Dict[str, Any]:
        """Apply custom AI prompt for company-specific analysis"""
        
        # This would integrate with the company's preferred AI model
        # For now, we'll enhance the analysis based on prompt keywords
        
        prompt_lower = ai_prompt.lower()
        
        if "security" in prompt_lower:
            analysis["tags"].append("security_relevant")
            analysis["importance_score"] = min(1.0, analysis["importance_score"] + 0.2)
        
        if "confidential" in prompt_lower:
            analysis["tags"].append("confidential")
            analysis["importance_score"] = min(1.0, analysis["importance_score"] + 0.1)
        
        if "urgent" in prompt_lower:
            analysis["tags"].append("urgent")
            analysis["importance_score"] = min(1.0, analysis["importance_score"] + 0.3)
        
        # Custom categorization based on prompt
        if "training" in prompt_lower:
            analysis["category"] = "training_material"
            analysis["related_modules"].append("training")
        
        return analysis
    
    def _detect_file_type(self, filename: str) -> DocumentType:
        """Detect file type from filename"""
        ext = Path(filename).suffix.lower()
        
        type_mapping = {
            '.pdf': DocumentType.PDF,
            '.docx': DocumentType.WORD,
            '.doc': DocumentType.WORD,
            '.xlsx': DocumentType.EXCEL,
            '.xls': DocumentType.EXCEL,
            '.pptx': DocumentType.POWERPOINT,
            '.ppt': DocumentType.POWERPOINT,
            '.txt': DocumentType.TEXT,
            '.csv': DocumentType.CSV,
            '.xml': DocumentType.XML,
            '.json': DocumentType.JSON,
            '.jpg': DocumentType.IMAGE,
            '.jpeg': DocumentType.IMAGE,
            '.png': DocumentType.IMAGE,
            '.gif': DocumentType.IMAGE,
            '.mp4': DocumentType.VIDEO,
            '.avi': DocumentType.VIDEO,
            '.mp3': DocumentType.AUDIO,
            '.wav': DocumentType.AUDIO,
            '.dwg': DocumentType.TECHNICAL_DRAWING,
            '.cad': DocumentType.CAD
        }
        
        return type_mapping.get(ext, DocumentType.TEXT)
    
    def _extract_pdf_text(self, file_data: bytes) -> str:
        """Extract text from PDF (stub - implement with PyPDF2 or pdfplumber)"""
        return "PDF content would be extracted here using PyPDF2 or similar library"
    
    def _extract_docx_text(self, file_data: bytes) -> str:
        """Extract text from DOCX (stub - implement with python-docx)"""
        return "DOCX content would be extracted here using python-docx library"
    
    def _default_permissions(self, department: str) -> Dict[str, List[str]]:
        """Generate default permissions based on department"""
        return {
            "admin": ["read", "write", "delete"],
            "manager": ["read", "write"],
            department: ["read", "write"],
            "viewer": ["read"]
        }
    
    async def _save_document_metadata(self, metadata: DocumentMetadata):
        """Save document metadata to database"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO documents VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
        ''', (
            metadata.document_id, metadata.filename, metadata.file_type.value,
            metadata.size_bytes, metadata.created_at, metadata.modified_at,
            metadata.uploaded_by, metadata.company_id, metadata.department,
            metadata.ai_summary, json.dumps(metadata.ai_tags), metadata.ai_category,
            metadata.ai_importance_score, metadata.access_level,
            json.dumps(metadata.permissions), metadata.encryption_status,
            metadata.version, metadata.parent_document_id, metadata.is_latest_version,
            json.dumps(metadata.related_modules), json.dumps(metadata.related_processes),
            json.dumps(metadata.related_workers), json.dumps(metadata.search_keywords),
            metadata.full_text_content, metadata.storage_location.value, metadata.storage_path
        ))
        
        conn.commit()
        conn.close()
    
    async def _update_search_index(self, metadata: DocumentMetadata):
        """Update full-text search index"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO document_search VALUES (?, ?, ?, ?, ?)
        ''', (
            metadata.document_id,
            metadata.filename,
            metadata.full_text_content,
            ' '.join(metadata.ai_tags),
            metadata.ai_category
        ))
        
        conn.commit()
        conn.close()
    
    async def search_documents(self, query: str, filters: Dict[str, Any] = None) -> List[DocumentMetadata]:
        """AI-powered document search"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Full-text search
        cursor.execute('''
            SELECT document_id FROM document_search 
            WHERE document_search MATCH ?
            ORDER BY bm25(document_search)
        ''', (query,))
        
        search_results = [row[0] for row in cursor.fetchall()]
        
        # Get full metadata for results
        if search_results:
            placeholders = ','.join(['?' for _ in search_results])
            cursor.execute(f'''
                SELECT * FROM documents 
                WHERE document_id IN ({placeholders})
                ORDER BY ai_importance_score DESC
            ''', search_results)
            
            documents = []
            for row in cursor.fetchall():
                documents.append(self._row_to_document_metadata(row))
        else:
            documents = []
        
        conn.close()
        
        # Apply additional filters
        if filters:
            documents = self._apply_search_filters(documents, filters)
        
        return documents
    
    def _row_to_document_metadata(self, row) -> DocumentMetadata:
        """Convert database row to DocumentMetadata"""
        return DocumentMetadata(
            document_id=row[0],
            filename=row[1],
            file_type=DocumentType(row[2]),
            size_bytes=row[3],
            created_at=row[4],
            modified_at=row[5],
            uploaded_by=row[6],
            company_id=row[7],
            department=row[8],
            ai_summary=row[9],
            ai_tags=json.loads(row[10]),
            ai_category=row[11],
            ai_importance_score=row[12],
            access_level=row[13],
            permissions=json.loads(row[14]),
            encryption_status=row[15],
            version=row[16],
            parent_document_id=row[17],
            is_latest_version=row[18],
            related_modules=json.loads(row[19]),
            related_processes=json.loads(row[20]),
            related_workers=json.loads(row[21]),
            search_keywords=json.loads(row[22]),
            full_text_content=row[23],
            storage_location=StorageLocation(row[24]),
            storage_path=row[25]
        )
    
    def _apply_search_filters(self, documents: List[DocumentMetadata], 
                            filters: Dict[str, Any]) -> List[DocumentMetadata]:
        """Apply search filters"""
        
        filtered = documents
        
        if filters.get("department"):
            filtered = [d for d in filtered if d.department == filters["department"]]
        
        if filters.get("file_type"):
            filtered = [d for d in filtered if d.file_type.value == filters["file_type"]]
        
        if filters.get("importance_min"):
            filtered = [d for d in filtered if d.ai_importance_score >= filters["importance_min"]]
        
        if filters.get("tags"):
            required_tags = filters["tags"]
            filtered = [d for d in filtered if any(tag in d.ai_tags for tag in required_tags)]
        
        return filtered
    
    async def create_memory_context(self, context_type: str, participants: List[str],
                                  conversation_data: Dict[str, Any],
                                  ai_prompt: str = None) -> MemoryContext:
        """Create a new memory context for AI-powered recall"""
        
        context_id = f"CTX-{uuid.uuid4().hex[:8]}"
        
        # AI analysis of the context
        ai_analysis = await self._ai_analyze_context(conversation_data, ai_prompt)
        
        context = MemoryContext(
            context_id=context_id,
            company_id=self.company_id,
            context_type=context_type,
            participants=participants,
            start_time=datetime.now().isoformat(),
            end_time=None,
            conversation_history=[conversation_data],
            decision_points=ai_analysis["decisions"],
            action_items=ai_analysis["actions"],
            referenced_documents=ai_analysis["documents"],
            ai_summary=ai_analysis["summary"],
            ai_insights=ai_analysis["insights"],
            ai_recommendations=ai_analysis["recommendations"],
            importance_score=ai_analysis["importance"],
            related_contexts=[],
            spawned_tasks=[],
            linked_incidents=[]
        )
        
        # Save to database
        await self._save_memory_context(context)
        
        return context
    
    async def _ai_analyze_context(self, conversation_data: Dict[str, Any], 
                                ai_prompt: str = None) -> Dict[str, Any]:
        """AI analysis of conversation context"""
        
        # Extract key information
        content = str(conversation_data)
        
        analysis = {
            "summary": f"AI-generated summary of context",
            "decisions": [],
            "actions": [],
            "documents": [],
            "insights": ["AI-generated insight 1", "AI-generated insight 2"],
            "recommendations": ["AI recommendation 1", "AI recommendation 2"],
            "importance": 0.7
        }
        
        # Look for decision points
        if any(word in content.lower() for word in ["decide", "decision", "choose", "select"]):
            analysis["decisions"].append({
                "decision": "Decision point identified",
                "timestamp": datetime.now().isoformat(),
                "participants": ["AI_detected"]
            })
        
        # Look for action items
        if any(word in content.lower() for word in ["action", "task", "todo", "follow up"]):
            analysis["actions"].append({
                "action": "Action item identified",
                "assignee": "TBD",
                "due_date": None,
                "status": "open"
            })
        
        return analysis
    
    async def _save_memory_context(self, context: MemoryContext):
        """Save memory context to database"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO memory_contexts VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
        ''', (
            context.context_id, context.company_id, context.context_type,
            json.dumps(context.participants), context.start_time, context.end_time,
            json.dumps(context.conversation_history), json.dumps(context.decision_points),
            json.dumps(context.action_items), json.dumps(context.referenced_documents),
            context.ai_summary, json.dumps(context.ai_insights),
            json.dumps(context.ai_recommendations), context.importance_score,
            json.dumps(context.related_contexts), json.dumps(context.spawned_tasks),
            json.dumps(context.linked_incidents)
        ))
        
        conn.commit()
        conn.close()
    
    async def recall_memory(self, query: str, context_type: str = None) -> List[MemoryContext]:
        """AI-powered memory recall"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        base_query = '''
            SELECT * FROM memory_contexts 
            WHERE company_id = ? AND ai_summary LIKE ?
        '''
        params = [self.company_id, f'%{query}%']
        
        if context_type:
            base_query += ' AND context_type = ?'
            params.append(context_type)
        
        base_query += ' ORDER BY importance_score DESC LIMIT 10'
        
        cursor.execute(base_query, params)
        
        contexts = []
        for row in cursor.fetchall():
            contexts.append(self._row_to_memory_context(row))
        
        conn.close()
        return contexts
    
    def _row_to_memory_context(self, row) -> MemoryContext:
        """Convert database row to MemoryContext"""
        return MemoryContext(
            context_id=row[0],
            company_id=row[1],
            context_type=row[2],
            participants=json.loads(row[3]),
            start_time=row[4],
            end_time=row[5],
            conversation_history=json.loads(row[6]),
            decision_points=json.loads(row[7]),
            action_items=json.loads(row[8]),
            referenced_documents=json.loads(row[9]),
            ai_summary=row[10],
            ai_insights=json.loads(row[11]),
            ai_recommendations=json.loads(row[12]),
            importance_score=row[13],
            related_contexts=json.loads(row[14]),
            spawned_tasks=json.loads(row[15]),
            linked_incidents=json.loads(row[16])
        )
    
    async def get_document_by_id(self, document_id: str) -> Optional[DocumentMetadata]:
        """Retrieve document by ID"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM documents WHERE document_id = ?', (document_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return self._row_to_document_metadata(row)
        return None
    
    async def get_documents_by_module(self, module_name: str) -> List[DocumentMetadata]:
        """Get all documents related to a specific module"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM documents 
            WHERE related_modules LIKE ?
            ORDER BY ai_importance_score DESC
        ''', (f'%{module_name}%',))
        
        documents = []
        for row in cursor.fetchall():
            documents.append(self._row_to_document_metadata(row))
        
        conn.close()
        return documents
    
    async def smart_recommendations(self, worker_id: str, current_task: str) -> Dict[str, Any]:
        """AI-powered smart recommendations for documents and memory"""
        
        # Analyze current task to find relevant content
        task_keywords = current_task.lower().split()
        
        # Find related documents
        related_docs = []
        for keyword in task_keywords:
            docs = await self.search_documents(keyword)
            related_docs.extend(docs)
        
        # Find related memories
        related_memories = await self.recall_memory(current_task)
        
        # AI-powered recommendations
        recommendations = {
            "suggested_documents": related_docs[:5],  # Top 5 most relevant
            "related_memories": related_memories[:3],  # Top 3 contexts
            "ai_insights": [
                f"Based on similar tasks, workers typically reference documents about {task_keywords[0] if task_keywords else 'the process'}",
                "Consider reviewing recent safety protocols",
                "Check for updated procedures in the last 30 days"
            ],
            "quick_actions": [
                "Create memory context for this task",
                "Upload relevant photos/documents",
                "Tag colleagues for collaboration"
            ]
        }
        
        return recommendations

# API Routes for Memory System
from fastapi import APIRouter, UploadFile, File, Form

memory_router = APIRouter(prefix="/api/memory", tags=["memory"])

@memory_router.post("/upload")
async def upload_document_endpoint(
    company_id: str = Form(...),
    file: UploadFile = File(...),
    uploaded_by: str = Form(...),
    department: str = Form(...),
    ai_prompt: str = Form(None)
):
    """Upload document with AI processing"""
    
    memory_system = UniversalMemorySystem(company_id)
    file_data = await file.read()
    
    metadata = await memory_system.upload_document(
        file_data=file_data,
        filename=file.filename,
        uploaded_by=uploaded_by,
        department=department,
        ai_prompt=ai_prompt
    )
    
    return {
        "status": "success",
        "document_id": metadata.document_id,
        "ai_analysis": {
            "summary": metadata.ai_summary,
            "tags": metadata.ai_tags,
            "category": metadata.ai_category,
            "importance": metadata.ai_importance_score
        }
    }

@memory_router.get("/search/{company_id}")
async def search_documents_endpoint(company_id: str, query: str, filters: str = None):
    """Search documents with AI"""
    
    memory_system = UniversalMemorySystem(company_id)
    filter_dict = json.loads(filters) if filters else {}
    
    documents = await memory_system.search_documents(query, filter_dict)
    
    return {
        "results": [asdict(doc) for doc in documents],
        "count": len(documents)
    }

@memory_router.post("/memory/create")
async def create_memory_context_endpoint(request: Dict[str, Any]):
    """Create memory context"""
    
    memory_system = UniversalMemorySystem(request["company_id"])
    
    context = await memory_system.create_memory_context(
        context_type=request["context_type"],
        participants=request["participants"],
        conversation_data=request["conversation_data"],
        ai_prompt=request.get("ai_prompt")
    )
    
    return {
        "status": "success",
        "context_id": context.context_id,
        "ai_insights": context.ai_insights
    }

@memory_router.get("/memory/recall/{company_id}")
async def recall_memory_endpoint(company_id: str, query: str, context_type: str = None):
    """Recall relevant memories"""
    
    memory_system = UniversalMemorySystem(company_id)
    contexts = await memory_system.recall_memory(query, context_type)
    
    return {
        "memories": [asdict(ctx) for ctx in contexts],
        "count": len(contexts)
    }

@memory_router.get("/recommendations/{company_id}")
async def smart_recommendations_endpoint(company_id: str, worker_id: str, current_task: str):
    """Get AI-powered recommendations"""
    
    memory_system = UniversalMemorySystem(company_id)
    recommendations = await memory_system.smart_recommendations(worker_id, current_task)
    
    return recommendations