import os
import json
import duckdb
from typing import Dict, Any, List, Optional
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize DuckDB connection
DB_PATH = os.getenv("DUCKDB_PATH", "job_matcher.duckdb")
conn = duckdb.connect(DB_PATH)

# Create tables if they don't exist
def init_db():
    """Initialize the database by creating necessary tables if they don't exist."""
    conn.execute("""
    CREATE TABLE IF NOT EXISTS match_history (
        id INTEGER PRIMARY KEY,
        timestamp TIMESTAMP,
        resume_text TEXT,
        job_description TEXT,
        raw_output TEXT,
        score INTEGER,
        summary TEXT,
        highlights JSON
    )
    """)
    
    # Create a sequence for auto-incrementing IDs if it doesn't exist
    conn.execute("""
    CREATE SEQUENCE IF NOT EXISTS match_history_id_seq
    """)

async def store_match_result(
    resume_text: str, 
    job_description: str, 
    raw_output: str, 
    parsed_output: Optional[Dict[str, Any]] = None
) -> int:
    """
    Store a match result in the database.
    
    Args:
        resume_text: The resume text
        job_description: The job description text
        raw_output: The raw output from OpenAI
        parsed_output: The parsed JSON output (optional)
        
    Returns:
        The ID of the inserted record
    """
    # Initialize the database if needed
    init_db()
    
    # Extract fields from parsed_output if available
    score = None
    summary = None
    highlights = None
    
    if parsed_output:
        score = parsed_output.get("score")
        summary = parsed_output.get("summary")
        highlights = json.dumps(parsed_output.get("highlights", []))
    
    # Insert the record
    conn.execute("""
    INSERT INTO match_history (
        id, timestamp, resume_text, job_description, raw_output, score, summary, highlights
    ) VALUES (
        nextval('match_history_id_seq'), ?, ?, ?, ?, ?, ?, ?
    )
    """, (
        datetime.now(), 
        resume_text, 
        job_description, 
        raw_output, 
        score, 
        summary, 
        highlights
    ))
    
    # Get the ID of the inserted record
    result = conn.execute("SELECT currval('match_history_id_seq')").fetchone()
    return result[0] if result else None

async def get_match_history(limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Get the match history from the database.
    
    Args:
        limit: Maximum number of records to return
        offset: Number of records to skip
        
    Returns:
        List of match history records
    """
    # Initialize the database if needed
    init_db()
    
    # Query the database
    result = conn.execute("""
    SELECT 
        id, 
        timestamp, 
        resume_text, 
        job_description, 
        raw_output, 
        score, 
        summary, 
        highlights
    FROM match_history
    ORDER BY timestamp DESC
    LIMIT ? OFFSET ?
    """, (limit, offset)).fetchall()
    
    # Convert the result to a list of dictionaries
    history = []
    for row in result:
        highlights_json = row[7]
        highlights = json.loads(highlights_json) if highlights_json else []
        
        history.append({
            "id": row[0],
            "timestamp": row[1].isoformat() if row[1] else None,
            "resume_text": row[2],
            "job_description": row[3],
            "raw_output": row[4],
            "score": row[5],
            "summary": row[6],
            "highlights": highlights
        })
    
    return history

async def get_match_by_id(match_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a specific match record by ID.
    
    Args:
        match_id: The ID of the match record
        
    Returns:
        The match record or None if not found
    """
    # Initialize the database if needed
    init_db()
    
    # Query the database
    result = conn.execute("""
    SELECT 
        id, 
        timestamp, 
        resume_text, 
        job_description, 
        raw_output, 
        score, 
        summary, 
        highlights
    FROM match_history
    WHERE id = ?
    """, (match_id,)).fetchone()
    
    if not result:
        return None
    
    # Convert the result to a dictionary
    highlights_json = result[7]
    highlights = json.loads(highlights_json) if highlights_json else []
    
    return {
        "id": result[0],
        "timestamp": result[1].isoformat() if result[1] else None,
        "resume_text": result[2],
        "job_description": result[3],
        "raw_output": result[4],
        "score": result[5],
        "summary": result[6],
        "highlights": highlights
    }
