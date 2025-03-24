from pydantic import BaseModel, Field
from typing import List, Optional
from fastapi import UploadFile, File, Form

class MatchRequest(BaseModel):
    resume_text: str
    job_description: str

class FileMatchRequest(BaseModel):
    job_description: str

# Keeping the HighlightItem for backward compatibility
class HighlightItem(BaseModel):
    type: str = Field(..., description="Type of highlight: 'match' or 'gap'")
    description: str = Field(..., description="Description of the matching skill or gap")

class MatchDetails(BaseModel):
    score: int = Field(..., description="Compatibility score from 0-100", ge=0, le=100)
    strengths: List[str] = Field(..., description="List of candidate's strengths relative to the job")
    gaps: List[str] = Field(..., description="List of missing skills or qualifications")
    actions: List[str] = Field(..., description="List of actionable recommendations")
    summary: str = Field(..., description="Motivational insight and summary")
    
    # For backward compatibility
    @property
    def highlights(self) -> List[HighlightItem]:
        """Convert strengths and gaps to the old highlight format for backward compatibility"""
        result = []
        for strength in self.strengths:
            result.append(HighlightItem(type="match", description=strength))
        for gap in self.gaps:
            result.append(HighlightItem(type="gap", description=gap))
        return result

class MatchResponse(BaseModel):
    raw_output: str = Field(..., description="Raw output from the LLM")
    parsed_output: Optional[MatchDetails] = Field(None, description="Structured output if parsing was successful")
