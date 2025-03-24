import os
from fastapi import FastAPI, HTTPException, Query, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List, Dict, Any, Optional
from app.models import MatchRequest, MatchResponse, MatchDetails, FileMatchRequest
from app.matcher import analyze_resume_job_match
from app.database import store_match_result, get_match_history, get_match_by_id
from app.file_utils import process_resume_file
from app.storage import setup_db, save_match_to_db

app = FastAPI(
    title="Job Matcher API",
    description="API for matching resumes with job descriptions using AI",
    version="1.0.0"
)

# Initialize the database
setup_db()

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Mount static files directory
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.post("/match", response_model=MatchResponse)
async def match_resume_job(data: MatchRequest):
    """
    Match a resume with a job description and return compatibility analysis.
    
    Returns both the raw LLM output and a structured parsed version if available.
    Also stores the result in the database.
    """
    try:
        raw_output, parsed_output = await analyze_resume_job_match(
            data.resume_text, 
            data.job_description
        )
        
        # Convert parsed output to MatchDetails if it exists
        structured_output = None
        if parsed_output:
            # Check if we have the new format or the old format
            if all(key in parsed_output for key in ["strengths", "gaps", "actions"]):
                # New format
                structured_output = MatchDetails(
                    score=parsed_output["score"],
                    strengths=parsed_output["strengths"],
                    gaps=parsed_output["gaps"],
                    actions=parsed_output["actions"],
                    summary=parsed_output["summary"]
                )
            elif "highlights" in parsed_output:
                # Old format - convert highlights to strengths and gaps
                strengths = []
                gaps = []
                for highlight in parsed_output["highlights"]:
                    if highlight["type"] == "match":
                        strengths.append(highlight["description"])
                    elif highlight["type"] == "gap":
                        gaps.append(highlight["description"])
                
                structured_output = MatchDetails(
                    score=parsed_output["score"],
                    strengths=strengths,
                    gaps=gaps,
                    actions=["Update your resume to address the identified gaps"],
                    summary=parsed_output["summary"]
                )
        
        # Store the result in the database
        match_id = await store_match_result(
            data.resume_text,
            data.job_description,
            raw_output,
            parsed_output
        )
        
        # Also save to the new storage format
        if structured_output:
            save_match_to_db(
                data.resume_text,
                data.job_description,
                structured_output.score,
                structured_output.strengths,
                structured_output.gaps,
                structured_output.actions,
                structured_output.summary
            )
            
        return MatchResponse(
            raw_output=raw_output,
            parsed_output=structured_output
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history", response_model=List[Dict[str, Any]])
async def get_history(
    limit: int = Query(10, ge=1, le=100, description="Maximum number of records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip")
):
    """
    Get the match history from the database.
    """
    try:
        history = await get_match_history(limit, offset)
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history/{match_id}", response_model=Dict[str, Any])
async def get_match(match_id: int):
    """
    Get a specific match record by ID.
    """
    try:
        match = await get_match_by_id(match_id)
        if not match:
            raise HTTPException(status_code=404, detail="Match not found")
        return match
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """
    Serve the frontend HTML file.
    """
    return FileResponse("app/static/index.html")

@app.post("/match-file", response_model=MatchResponse)
async def match_resume_file(
    resume_file: UploadFile = File(...),
    job_description: str = Form(...)
):
    """
    Match a resume file with a job description and return compatibility analysis.
    
    Supports .docx and .txt files.
    """
    try:
        # Read the file content
        file_content = await resume_file.read()
        
        # Process the file
        resume_text = process_resume_file(file_content, resume_file.filename)
        
        if not resume_text:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file format: {resume_file.filename}. Only .docx and .txt files are supported."
            )
        
        # Analyze the match
        raw_output, parsed_output = await analyze_resume_job_match(
            resume_text, 
            job_description
        )
        
        # Convert parsed output to MatchDetails if it exists
        structured_output = None
        if parsed_output:
            # Check if we have the new format or the old format
            if all(key in parsed_output for key in ["strengths", "gaps", "actions"]):
                # New format
                structured_output = MatchDetails(
                    score=parsed_output["score"],
                    strengths=parsed_output["strengths"],
                    gaps=parsed_output["gaps"],
                    actions=parsed_output["actions"],
                    summary=parsed_output["summary"]
                )
            elif "highlights" in parsed_output:
                # Old format - convert highlights to strengths and gaps
                strengths = []
                gaps = []
                for highlight in parsed_output["highlights"]:
                    if highlight["type"] == "match":
                        strengths.append(highlight["description"])
                    elif highlight["type"] == "gap":
                        gaps.append(highlight["description"])
                
                structured_output = MatchDetails(
                    score=parsed_output["score"],
                    strengths=strengths,
                    gaps=gaps,
                    actions=["Update your resume to address the identified gaps"],
                    summary=parsed_output["summary"]
                )
        
        # Store the result in the database
        match_id = await store_match_result(
            resume_text,
            job_description,
            raw_output,
            parsed_output
        )
        
        # Also save to the new storage format
        if structured_output:
            save_match_to_db(
                resume_text,
                job_description,
                structured_output.score,
                structured_output.strengths,
                structured_output.gaps,
                structured_output.actions,
                structured_output.summary
            )
            
        return MatchResponse(
            raw_output=raw_output,
            parsed_output=structured_output
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/info")
async def api_info():
    """
    API information endpoint.
    """
    return {
        "name": "Job Matcher API",
        "version": "1.0.0",
        "description": "API for matching resumes with job descriptions using AI"
    }
