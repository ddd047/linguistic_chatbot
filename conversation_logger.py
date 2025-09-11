import sqlite3
import json
import os
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional
import asyncio

class ConversationLogger:
    def __init__(self, db_path: str = "../data/conversations.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the SQLite database with required tables"""
        # Ensure the data directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    message_count INTEGER DEFAULT 0,
                    languages_used TEXT DEFAULT '[]'
                )
            ''')
            
            # Create conversations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_message TEXT NOT NULL,
                    bot_response TEXT NOT NULL,
                    language TEXT NOT NULL,
                    confidence REAL DEFAULT 0.0,
                    category TEXT,
                    needs_human BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (session_id) REFERENCES sessions (session_id)
                )
            ''')
            
            # Create daily_stats table for analytics
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_stats (
                    date TEXT PRIMARY KEY,
                    total_conversations INTEGER DEFAULT 0,
                    total_sessions INTEGER DEFAULT 0,
                    languages_breakdown TEXT DEFAULT '{}',
                    categories_breakdown TEXT DEFAULT '{}',
                    avg_confidence REAL DEFAULT 0.0,
                    human_handoff_count INTEGER DEFAULT 0
                )
            ''')
            
            conn.commit()
    
    async def log_conversation(self, session_id: str, user_message: str, 
                             bot_response: str, language: str, confidence: float,
                             category: Optional[str] = None, needs_human: bool = False):
        """Log a conversation turn"""
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Insert or update session
            cursor.execute('''
                INSERT INTO sessions (session_id, languages_used, message_count)
                VALUES (?, ?, 1)
                ON CONFLICT(session_id) DO UPDATE SET
                    updated_at = CURRENT_TIMESTAMP,
                    message_count = message_count + 1,
                    languages_used = CASE 
                        WHEN json_extract(languages_used, '$') LIKE '%' || ? || '%' 
                        THEN languages_used
                        ELSE json_insert(languages_used, '$[#]', ?)
                    END
            ''', (session_id, json.dumps([language]), language, language))
            
            # Insert conversation
            cursor.execute('''
                INSERT INTO conversations 
                (session_id, user_message, bot_response, language, confidence, category, needs_human)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (session_id, user_message, bot_response, language, confidence, category, needs_human))
            
            conn.commit()
        
        # Update daily stats
        await self._update_daily_stats(language, category, confidence, needs_human)
    
    async def _update_daily_stats(self, language: str, category: str, 
                                confidence: float, needs_human: bool):
        """Update daily statistics"""
        today = date.today().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get current stats
            cursor.execute('SELECT * FROM daily_stats WHERE date = ?', (today,))
            row = cursor.fetchone()
            
            if row:
                # Update existing record
                languages_breakdown = json.loads(row[3])
                categories_breakdown = json.loads(row[4])
                
                languages_breakdown[language] = languages_breakdown.get(language, 0) + 1
                if category:
                    categories_breakdown[category] = categories_breakdown.get(category, 0) + 1
                
                new_total = row[1] + 1
                new_avg_confidence = ((row[5] * row[1]) + confidence) / new_total
                new_handoff_count = row[6] + (1 if needs_human else 0)
                
                cursor.execute('''
                    UPDATE daily_stats SET
                        total_conversations = ?,
                        languages_breakdown = ?,
                        categories_breakdown = ?,
                        avg_confidence = ?,
                        human_handoff_count = ?
                    WHERE date = ?
                ''', (new_total, json.dumps(languages_breakdown), json.dumps(categories_breakdown),
                     new_avg_confidence, new_handoff_count, today))
            else:
                # Insert new record
                languages_breakdown = {language: 1}
                categories_breakdown = {category: 1} if category else {}
                
                cursor.execute('''
                    INSERT INTO daily_stats 
                    (date, total_conversations, total_sessions, languages_breakdown, 
                     categories_breakdown, avg_confidence, human_handoff_count)
                    VALUES (?, 1, 0, ?, ?, ?, ?)
                ''', (today, json.dumps(languages_breakdown), json.dumps(categories_breakdown),
                     confidence, 1 if needs_human else 0))
            
            conn.commit()
    
    async def get_session_info(self, session_id: str) -> Optional[Dict]:
        """Get information about a specific session"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT s.*, COUNT(c.id) as actual_message_count
                FROM sessions s
                LEFT JOIN conversations c ON s.session_id = c.session_id
                WHERE s.session_id = ?
                GROUP BY s.session_id
            ''', (session_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return {
                "session_id": row[0],
                "created_at": row[1],
                "updated_at": row[2],
                "message_count": row[4],
                "languages_used": json.loads(row[5]),
                "actual_message_count": row[6]
            }
    
    async def get_daily_logs(self, date_str: str) -> List[Dict]:
        """Get all conversations for a specific date"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT c.*, s.created_at as session_start
                FROM conversations c
                JOIN sessions s ON c.session_id = s.session_id
                WHERE DATE(c.timestamp) = ?
                ORDER BY c.timestamp DESC
            ''', (date_str,))
            
            rows = cursor.fetchall()
            
            conversations = []
            for row in rows:
                conversations.append({
                    "id": row[0],
                    "session_id": row[1],
                    "timestamp": row[2],
                    "user_message": row[3],
                    "bot_response": row[4],
                    "language": row[5],
                    "confidence": row[6],
                    "category": row[7],
                    "needs_human": bool(row[8]),
                    "session_start": row[9]
                })
            
            return conversations
    
    async def get_daily_stats(self, date_str: str) -> Optional[Dict]:
        """Get daily statistics for a specific date"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM daily_stats WHERE date = ?', (date_str,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return {
                "date": row[0],
                "total_conversations": row[1],
                "total_sessions": row[2],
                "languages_breakdown": json.loads(row[3]),
                "categories_breakdown": json.loads(row[4]),
                "avg_confidence": row[5],
                "human_handoff_count": row[6]
            }
    
    async def get_conversation_history(self, session_id: str) -> List[Dict]:
        """Get full conversation history for a session"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM conversations 
                WHERE session_id = ? 
                ORDER BY timestamp ASC
            ''', (session_id,))
            
            rows = cursor.fetchall()
            
            history = []
            for row in rows:
                history.append({
                    "id": row[0],
                    "timestamp": row[2],
                    "user_message": row[3],
                    "bot_response": row[4],
                    "language": row[5],
                    "confidence": row[6],
                    "category": row[7],
                    "needs_human": bool(row[8])
                })
            
            return history
    
    async def export_logs(self, start_date: str, end_date: str, format: str = "json") -> str:
        """Export conversation logs for a date range"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT c.*, s.created_at as session_start
                FROM conversations c
                JOIN sessions s ON c.session_id = s.session_id
                WHERE DATE(c.timestamp) BETWEEN ? AND ?
                ORDER BY c.timestamp DESC
            ''', (start_date, end_date))
            
            rows = cursor.fetchall()
            
            conversations = []
            for row in rows:
                conversations.append({
                    "id": row[0],
                    "session_id": row[1],
                    "timestamp": row[2],
                    "user_message": row[3],
                    "bot_response": row[4],
                    "language": row[5],
                    "confidence": row[6],
                    "category": row[7],
                    "needs_human": bool(row[8]),
                    "session_start": row[9]
                })
            
            if format == "json":
                return json.dumps(conversations, indent=2, ensure_ascii=False)
            else:
                # Could add CSV format here
                return json.dumps(conversations, indent=2, ensure_ascii=False)
    
    def cleanup_old_logs(self, days_to_keep: int = 30):
        """Clean up old conversation logs to save space"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Delete old conversations
            cursor.execute('''
                DELETE FROM conversations 
                WHERE timestamp < ?
            ''', (cutoff_date.isoformat(),))
            
            # Delete old sessions with no conversations
            cursor.execute('''
                DELETE FROM sessions 
                WHERE session_id NOT IN (
                    SELECT DISTINCT session_id FROM conversations
                )
            ''')
            
            # Delete old daily stats
            cursor.execute('''
                DELETE FROM daily_stats 
                WHERE date < ?
            ''', (cutoff_date.date().isoformat(),))
            
            conn.commit()
