import os
import json
import asyncio
from typing import Dict, Any, Optional, Tuple
from dotenv import load_dotenv
from openai import OpenAI, APIError, RateLimitError, APITimeoutError

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_match_prompt(resume: str, job: str) -> str:
    return f"""
You are an expert career coach and talent assessor. Compare the resume and job description below.

Resume:
{resume}

Job Description:
{job}

Provide a comprehensive analysis in the following JSON format:

```json
{{
    "score": <number between 0-100 representing overall compatibility>,
    "strengths": [
        "<specific skill or qualification from the resume that matches the job>",
        "<another strength, be specific and reference actual content>"
    ],
    "gaps": [
        "<specific skill or qualification missing from the resume but required in the job>",
        "<another gap, be specific and actionable>"
    ],
    "actions": [
        "<specific, actionable recommendation to improve alignment>",
        "<another recommendation with concrete steps>"
    ],
    "summary": "<motivational insight that acknowledges strengths while encouraging growth in a supportive tone>"
}}
```

Ensure your response is valid JSON and follows this exact structure.
For strengths: Focus on 3-5 specific qualifications that align well with the job requirements.
For gaps: Identify 2-4 key missing qualifications or experience areas.
For actions: Provide 3-5 specific, actionable recommendations the candidate can take to improve their alignment.
For summary: Write an encouraging 2-3 sentence summary that reflects empathy and clarity.
"""

async def analyze_resume_job_match(resume: str, job_description: str) -> Tuple[str, Optional[Dict[str, Any]]]:
    """
    Analyze the match between a resume and job description using OpenAI.
    
    Args:
        resume: The resume text
        job_description: The job description text
        
    Returns:
        Tuple containing:
        - Raw output from OpenAI
        - Parsed JSON response (if parsing was successful, otherwise None)
    """
    prompt = generate_match_prompt(resume, job_description)
    
    try:
        # Use synchronous client with await_async=False
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Using gpt-3.5-turbo for faster response
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            timeout=30  # 30 second timeout
        )
        
        raw_output = response.choices[0].message.content
        
        # Try to parse the JSON response
        parsed_output = None
        try:
            # Extract JSON if it's wrapped in markdown code blocks
            if "```json" in raw_output and "```" in raw_output:
                json_content = raw_output.split("```json")[1].split("```")[0].strip()
                parsed_output = json.loads(json_content)
            else:
                # Try to parse the entire response as JSON
                parsed_output = json.loads(raw_output)
                
            # Validate the parsed output has the expected structure
            required_keys = ["score", "strengths", "gaps", "actions", "summary"]
            if not all(key in parsed_output for key in required_keys):
                parsed_output = None
                
        except (json.JSONDecodeError, IndexError):
            parsed_output = None
            
        return raw_output, parsed_output
        
    except RateLimitError:
        raise Exception("OpenAI API rate limit exceeded. Please try again later.")
    except APITimeoutError:
        raise Exception("OpenAI API request timed out. Please try again later.")
    except APIError as e:
        raise Exception(f"OpenAI API error: {str(e)}")
    except Exception as e:
        raise Exception(f"Error processing request: {str(e)}")
