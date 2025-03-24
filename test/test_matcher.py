import pytest
import json
from unittest.mock import AsyncMock, patch
from app.matcher import generate_match_prompt, analyze_resume_job_match

# Sample data for tests
SAMPLE_RESUME = """
John Doe
Software Engineer

Experience:
- Senior Developer at Tech Co (2020-Present)
  * Led development of cloud-based applications
  * Implemented CI/CD pipelines
- Junior Developer at Startup Inc (2018-2020)
  * Developed frontend components using React
  * Worked on RESTful API design

Skills:
Python, JavaScript, React, Docker, AWS, CI/CD
"""

SAMPLE_JOB = """
Senior Software Engineer

We are looking for a Senior Software Engineer with strong experience in:
- Python development
- Cloud infrastructure (AWS preferred)
- CI/CD implementation
- Team leadership
- Microservices architecture

Required:
- 5+ years of software development experience
- Strong knowledge of Python
- Experience with AWS services
- CI/CD pipeline implementation
"""

SAMPLE_RESPONSE = {
    "score": 85,
    "highlights": [
        {
            "type": "match",
            "description": "Strong Python experience"
        },
        {
            "type": "match",
            "description": "Experience with AWS"
        },
        {
            "type": "gap",
            "description": "Limited leadership experience"
        }
    ],
    "summary": "Good overall match with strong technical alignment but some gaps in leadership experience."
}

def test_generate_match_prompt():
    """Test that the prompt generation function works correctly."""
    prompt = generate_match_prompt(SAMPLE_RESUME, SAMPLE_JOB)
    
    # Check that the prompt contains the resume and job description
    assert SAMPLE_RESUME in prompt
    assert SAMPLE_JOB in prompt
    
    # Check that the prompt asks for JSON format
    assert "JSON format" in prompt
    assert "score" in prompt
    assert "highlights" in prompt
    assert "summary" in prompt

@pytest.mark.asyncio
@patch('app.matcher.client.chat.completions.create')
async def test_analyze_resume_job_match_success(mock_create):
    """Test successful analysis with proper JSON response."""
    # Mock the OpenAI response
    mock_response = AsyncMock()
    mock_response.choices = [
        AsyncMock(
            message=AsyncMock(
                content=json.dumps(SAMPLE_RESPONSE)
            )
        )
    ]
    mock_create.return_value = mock_response
    
    # Call the function
    raw_output, parsed_output = await analyze_resume_job_match(SAMPLE_RESUME, SAMPLE_JOB)
    
    # Verify the results
    assert raw_output == json.dumps(SAMPLE_RESPONSE)
    assert parsed_output is not None
    assert parsed_output["score"] == 85
    assert len(parsed_output["highlights"]) == 3
    assert parsed_output["summary"] == "Good overall match with strong technical alignment but some gaps in leadership experience."

@pytest.mark.asyncio
@patch('app.matcher.client.chat.completions.create')
async def test_analyze_resume_job_match_markdown_json(mock_create):
    """Test analysis with JSON wrapped in markdown code blocks."""
    # Mock the OpenAI response with markdown-wrapped JSON
    markdown_response = f"```json\n{json.dumps(SAMPLE_RESPONSE)}\n```"
    mock_response = AsyncMock()
    mock_response.choices = [
        AsyncMock(
            message=AsyncMock(
                content=markdown_response
            )
        )
    ]
    mock_create.return_value = mock_response
    
    # Call the function
    raw_output, parsed_output = await analyze_resume_job_match(SAMPLE_RESUME, SAMPLE_JOB)
    
    # Verify the results
    assert raw_output == markdown_response
    assert parsed_output is not None
    assert parsed_output["score"] == 85
    assert len(parsed_output["highlights"]) == 3

@pytest.mark.asyncio
@patch('app.matcher.client.chat.completions.create')
async def test_analyze_resume_job_match_invalid_json(mock_create):
    """Test handling of invalid JSON response."""
    # Mock the OpenAI response with invalid JSON
    mock_response = AsyncMock()
    mock_response.choices = [
        AsyncMock(
            message=AsyncMock(
                content="This is not valid JSON"
            )
        )
    ]
    mock_create.return_value = mock_response
    
    # Call the function
    raw_output, parsed_output = await analyze_resume_job_match(SAMPLE_RESUME, SAMPLE_JOB)
    
    # Verify the results
    assert raw_output == "This is not valid JSON"
    assert parsed_output is None

@pytest.mark.asyncio
@patch('app.matcher.client.chat.completions.create')
async def test_analyze_resume_job_match_missing_fields(mock_create):
    """Test handling of JSON response with missing required fields."""
    # Create a response with missing fields
    incomplete_response = {
        "score": 85,
        # Missing highlights
        "summary": "Good overall match."
    }
    
    mock_response = AsyncMock()
    mock_response.choices = [
        AsyncMock(
            message=AsyncMock(
                content=json.dumps(incomplete_response)
            )
        )
    ]
    mock_create.return_value = mock_response
    
    # Call the function
    raw_output, parsed_output = await analyze_resume_job_match(SAMPLE_RESUME, SAMPLE_JOB)
    
    # Verify the results
    assert raw_output == json.dumps(incomplete_response)
    assert parsed_output is None  # Should be None because of missing fields

@pytest.mark.asyncio
@patch('app.matcher.client.chat.completions.create', side_effect=Exception("Test error"))
async def test_analyze_resume_job_match_error(mock_create):
    """Test error handling in the analyze function."""
    # Call the function and expect an exception
    with pytest.raises(Exception) as excinfo:
        await analyze_resume_job_match(SAMPLE_RESUME, SAMPLE_JOB)
    
    # Verify the error message
    assert "Error processing request" in str(excinfo.value)
