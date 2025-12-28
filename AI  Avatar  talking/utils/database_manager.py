"""
Database Manager for AI Avatar Studio
Handles SQLite operations with Docker volume support
"""

import sqlite3
import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    SQLite Database Manager with Docker volume support
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize database manager
        
        Args:
            db_path: Path to SQLite database file. 
                    If None, uses DATABASE_PATH env var or default path
        """
        if db_path is None:
            db_path = os.getenv('DATABASE_PATH', './data/database/projects.db')
        
        self.db_path = Path(db_path)
        self._ensure_directory()
        self._init_database()
        logger.info(f"Database initialized at: {self.db_path}")
    
    def _ensure_directory(self):
        """Ensure database directory exists"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections
        
        Usage:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM projects")
        """
        conn = sqlite3.connect(
            self.db_path,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
            timeout=30.0
        )
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()
    
    def _init_database(self):
        """Initialize database schema"""
        schema = """
        -- Projects table
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT CHECK(status IN ('draft', 'processing', 'completed', 'failed')) DEFAULT 'draft',
            notes TEXT
        );

        -- Generations table
        CREATE TABLE IF NOT EXISTS generations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            input_image_path TEXT NOT NULL,
            input_text TEXT NOT NULL,
            input_audio_path TEXT,
            output_video_path TEXT,
            thumbnail_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            processing_time_seconds REAL,
            status TEXT CHECK(status IN ('queued', 'processing', 'completed', 'failed')) DEFAULT 'queued',
            error_message TEXT,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        );

        -- Settings table
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            generation_id INTEGER,
            tts_engine TEXT DEFAULT 'coqui',
            tts_voice TEXT DEFAULT 'jenny',
            tts_speed REAL DEFAULT 1.0,
            tts_pitch REAL DEFAULT 1.0,
            video_resolution TEXT DEFAULT '1080p',
            video_format TEXT DEFAULT 'mp4',
            video_quality TEXT DEFAULT 'high',
            enable_background_removal BOOLEAN DEFAULT 0,
            enable_subtitles BOOLEAN DEFAULT 0,
            enable_audio_enhancement BOOLEAN DEFAULT 1,
            use_gpu BOOLEAN DEFAULT 1,
            FOREIGN KEY (generation_id) REFERENCES generations(id) ON DELETE CASCADE
        );

        -- Processing logs table
        CREATE TABLE IF NOT EXISTS processing_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            generation_id INTEGER,
            stage TEXT NOT NULL,
            status TEXT CHECK(status IN ('started', 'completed', 'failed')) DEFAULT 'started',
            duration_seconds REAL,
            memory_usage_mb REAL,
            error_details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (generation_id) REFERENCES generations(id) ON DELETE CASCADE
        );

        -- Model versions table
        CREATE TABLE IF NOT EXISTS model_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_type TEXT NOT NULL UNIQUE,
            version TEXT NOT NULL,
            download_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            file_size_mb REAL,
            checksum TEXT,
            is_active BOOLEAN DEFAULT 1
        );

        -- User preferences table
        CREATE TABLE IF NOT EXISTS user_preferences (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Batch queue table
        CREATE TABLE IF NOT EXISTS batch_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_path TEXT NOT NULL,
            text_content TEXT NOT NULL,
            audio_path TEXT,
            priority INTEGER DEFAULT 0,
            status TEXT CHECK(status IN ('pending', 'processing', 'completed', 'failed')) DEFAULT 'pending',
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            processed_at TIMESTAMP
        );

        -- Create indexes for performance
        CREATE INDEX IF NOT EXISTS idx_generations_project_id ON generations(project_id);
        CREATE INDEX IF NOT EXISTS idx_generations_status ON generations(status);
        CREATE INDEX IF NOT EXISTS idx_processing_logs_generation_id ON processing_logs(generation_id);
        CREATE INDEX IF NOT EXISTS idx_batch_queue_status ON batch_queue(status);
        CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
        CREATE INDEX IF NOT EXISTS idx_generations_created_at ON generations(created_at DESC);
        """
        
        with self.get_connection() as conn:
            conn.executescript(schema)
        
        logger.info("Database schema initialized successfully")
    
    # ===== PROJECT OPERATIONS =====
    
    def create_project(self, name: str, notes: Optional[str] = None, description: Optional[str] = None) -> int:
        """Create a new project"""
        # Use description as notes if notes not provided
        if description and not notes:
            notes = description
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO projects (name, notes) VALUES (?, ?)",
                (name, notes)
            )
            return cursor.lastrowid
    
    def get_project(self, project_id: int) -> Optional[Dict[str, Any]]:
        """Get project by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_all_projects(self) -> List[Dict[str, Any]]:
        """Get all projects"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM projects ORDER BY updated_at DESC"
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def update_project_status(self, project_id: int, status: str):
        """Update project status"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE projects SET status = ?, updated_at = ? WHERE id = ?",
                (status, datetime.now(), project_id)
            )
    
    def delete_project(self, project_id: int):
        """Delete project and all related data"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    
    # ===== GENERATION OPERATIONS =====
    
    def create_generation(
        self,
        project_id: Optional[int] = None,
        input_image_path: Optional[str] = None,
        input_text: Optional[str] = None,
        input_audio_path: Optional[str] = None,
        status: Optional[str] = 'queued',
        input_image: Optional[str] = None,
        output_video: Optional[str] = None,
        settings: Optional[Dict[str, Any]] = None
    ) -> int:
        """Create a new generation record"""
        # Handle alternate parameter names
        if input_image and not input_image_path:
            input_image_path = input_image
        if output_video and not input_text and settings:
            input_text = settings.get('text', '')
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO generations 
                (project_id, input_image_path, input_text, input_audio_path, status, output_video_path)
                VALUES (?, ?, ?, ?, ?, ?)""",
                (project_id, input_image_path or '', input_text or '', input_audio_path, status, output_video)
            )
            generation_id = cursor.lastrowid
            
            # Create settings record if provided
            if settings and generation_id:
                # Extract settings values with defaults
                tts_engine = settings.get('voice', 'coqui') if settings.get('voice') else 'coqui'
                video_quality = settings.get('quality', 'high')
                video_resolution = settings.get('resolution', '1080p')
                tts_speed = settings.get('speed', 1.0)
                
                cursor.execute(
                    """INSERT INTO settings 
                    (generation_id, tts_engine, tts_voice, tts_speed, video_resolution, video_quality)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    (generation_id, tts_engine, tts_engine, tts_speed, video_resolution, video_quality)
                )
            
            return generation_id
    
    def update_generation_status(
        self,
        generation_id: int,
        status: str,
        output_path: Optional[str] = None,
        error_message: Optional[str] = None
    ):
        """Update generation status"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE generations 
                SET status = ?, output_video_path = ?, error_message = ?
                WHERE id = ?""",
                (status, output_path, error_message, generation_id)
            )
    
    def update_generation_time(self, generation_id: int, time_seconds: float):
        """Update processing time"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE generations SET processing_time_seconds = ? WHERE id = ?",
                (time_seconds, generation_id)
            )
    
    def update_generation(
        self,
        generation_id: int,
        status: Optional[str] = None,
        output_path: Optional[str] = None,
        output_video: Optional[str] = None,
        error_message: Optional[str] = None,
        time_seconds: Optional[float] = None,
        metadata: Optional[dict] = None
    ):
        """Update generation record (unified method that wraps specific update methods)"""
        # Use output_video if provided, fallback to output_path
        final_output = output_video or output_path
        
        if status is not None or final_output is not None or error_message is not None:
            self.update_generation_status(generation_id, status or 'processing', final_output, error_message)
        if time_seconds is not None:
            self.update_generation_time(generation_id, time_seconds)
        # metadata is accepted but not stored (for compatibility)
    
    def get_generation(self, generation_id: int) -> Optional[Dict[str, Any]]:
        """Get generation by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM generations WHERE id = ?", (generation_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_project_generations(self, project_id: int) -> List[Dict[str, Any]]:
        """Get all generations for a project"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM generations WHERE project_id = ? ORDER BY created_at DESC",
                (project_id,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    # ===== SETTINGS OPERATIONS =====
    
    def save_generation_settings(self, generation_id: int, settings: Dict[str, Any]) -> int:
        """Save settings for a generation"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO settings 
                (generation_id, tts_engine, tts_voice, tts_speed, tts_pitch,
                 video_resolution, video_format, video_quality,
                 enable_background_removal, enable_subtitles, 
                 enable_audio_enhancement, use_gpu)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    generation_id,
                    settings.get('tts_engine', 'coqui'),
                    settings.get('tts_voice', 'jenny'),
                    settings.get('tts_speed', 1.0),
                    settings.get('tts_pitch', 1.0),
                    settings.get('video_resolution', '1080p'),
                    settings.get('video_format', 'mp4'),
                    settings.get('video_quality', 'high'),
                    settings.get('enable_background_removal', False),
                    settings.get('enable_subtitles', False),
                    settings.get('enable_audio_enhancement', True),
                    settings.get('use_gpu', True)
                )
            )
            return cursor.lastrowid
    
    # ===== PROCESSING LOG OPERATIONS =====
    
    def log_processing_stage(
        self,
        generation_id: int,
        stage: str,
        status: str,
        duration: Optional[float] = None,
        memory_usage: Optional[float] = None,
        error: Optional[str] = None
    ):
        """Log a processing stage"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO processing_logs 
                (generation_id, stage, status, duration_seconds, 
                 memory_usage_mb, error_details)
                VALUES (?, ?, ?, ?, ?, ?)""",
                (generation_id, stage, status, duration, memory_usage, error)
            )
    
    def get_processing_logs(self, generation_id: int) -> List[Dict[str, Any]]:
        """Get processing logs for a generation"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM processing_logs WHERE generation_id = ? ORDER BY timestamp",
                (generation_id,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    # ===== USER PREFERENCES =====
    
    def set_preference(self, key: str, value: str):
        """Set a user preference"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT OR REPLACE INTO user_preferences (key, value, updated_at)
                VALUES (?, ?, ?)""",
                (key, value, datetime.now())
            )
    
    def get_preference(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get a user preference"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM user_preferences WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row['value'] if row else default
    
    # ===== BATCH QUEUE OPERATIONS =====
    
    def add_to_batch_queue(
        self,
        image_path: str,
        text_content: str,
        audio_path: Optional[str] = None,
        priority: int = 0
    ) -> int:
        """Add item to batch processing queue"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO batch_queue 
                (image_path, text_content, audio_path, priority)
                VALUES (?, ?, ?, ?)""",
                (image_path, text_content, audio_path, priority)
            )
            return cursor.lastrowid
    
    def get_pending_batch_items(self) -> List[Dict[str, Any]]:
        """Get pending batch items"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT * FROM batch_queue 
                WHERE status = 'pending' 
                ORDER BY priority DESC, added_at ASC"""
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def update_batch_status(self, batch_id: int, status: str):
        """Update batch item status"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            processed_at = datetime.now() if status in ['completed', 'failed'] else None
            cursor.execute(
                "UPDATE batch_queue SET status = ?, processed_at = ? WHERE id = ?",
                (status, processed_at, batch_id)
            )
    
    # ===== STATISTICS & ANALYTICS =====
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total projects
            cursor.execute("SELECT COUNT(*) as count FROM projects")
            total_projects = cursor.fetchone()['count']
            
            # Total generations
            cursor.execute("SELECT COUNT(*) as count FROM generations")
            total_generations = cursor.fetchone()['count']
            
            # Completed generations
            cursor.execute(
                "SELECT COUNT(*) as count FROM generations WHERE status = 'completed'"
            )
            completed = cursor.fetchone()['count']
            
            # Failed generations
            cursor.execute(
                "SELECT COUNT(*) as count FROM generations WHERE status = 'failed'"
            )
            failed = cursor.fetchone()['count']
            
            # Average processing time
            cursor.execute(
                """SELECT AVG(processing_time_seconds) as avg_time 
                FROM generations WHERE status = 'completed'"""
            )
            avg_time = cursor.fetchone()['avg_time'] or 0
            
            return {
                'total_projects': total_projects,
                'total_generations': total_generations,
                'completed_generations': completed,
                'failed_generations': failed,
                'success_rate': (completed / total_generations * 100) if total_generations > 0 else 0,
                'average_processing_time_seconds': round(avg_time, 2)
            }
    
    def cleanup_old_data(self, days: int = 30):
        """Cleanup old failed/draft projects"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cutoff_date = datetime.now().timestamp() - (days * 86400)
            cursor.execute(
                """DELETE FROM projects 
                WHERE status IN ('draft', 'failed') 
                AND updated_at < ?""",
                (cutoff_date,)
            )
            logger.info(f"Cleaned up {cursor.rowcount} old projects")


# Example usage
if __name__ == "__main__":
    # Initialize database
    db = DatabaseManager()
    
    # Create a test project
    project_id = db.create_project("Test Project", "This is a test")
    print(f"Created project: {project_id}")
    
    # Get statistics
    stats = db.get_statistics()
    print(f"Statistics: {stats}")
