# Job Matcher Microservice

A containerized microservice that compares resumes with job descriptions and returns a compatibility score and summary using OpenAI.

## Features

- **AI-Powered Analysis**: Uses OpenAI's GPT-4 to analyze the compatibility between resumes and job descriptions
- **Structured Output**: Returns a compatibility score, key matches, gaps, and a summary
- **Web Interface**: Simple and responsive frontend for easy interaction
- **File Upload Support**: Upload .docx and .txt resume files directly
- **History Tracking**: Stores previous matches in a DuckDB database
- **Error Handling**: Comprehensive error handling for API calls
- **Containerized**: Easy deployment with Docker

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Docker (optional, for containerized deployment)
- OpenAI API key

### Environment Setup

1. Clone the repository
2. Create a `.env` file in the root directory with your OpenAI API key:

```
OPENAI_API_KEY=your_openai_api_key_here
```

3. (Optional) Set a custom DuckDB path:

```
DUCKDB_PATH=/path/to/your/database.duckdb
```

### Installation

#### Local Development

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the application:

```bash
uvicorn app.main:app --reload
```

3. Open your browser and navigate to `http://localhost:8000`

#### Docker Deployment

1. Build the Docker image:

```bash
docker build -t job-matcher .
```

2. Run the container:

```bash
docker run -p 8000:8000 --env-file .env job-matcher
```

3. Open your browser and navigate to `http://localhost:8000`

## API Endpoints

### Match Resume with Job Description (Text)

```
POST /match
```

Request body:

```json
{
  "resume_text": "Your resume text here...",
  "job_description": "Job description text here..."
}
```

### Match Resume with Job Description (File Upload)

```
POST /match-file
```

Request body (multipart/form-data):
- `resume_file`: A .docx or .txt file containing the resume
- `job_description`: Job description text

### Response Format (Both Endpoints)

```json
{
  "raw_output": "Raw output from OpenAI",
  "parsed_output": {
    "score": 85,
    "highlights": [
      {
        "type": "match",
        "description": "Strong Python experience"
      },
      {
        "type": "gap",
        "description": "Limited leadership experience"
      }
    ],
    "summary": "Good overall match with strong technical alignment but some gaps in leadership experience."
  }
}
```

### Get Match History

```
GET /history?limit=10&offset=0
```

Parameters:
- `limit`: Maximum number of records to return (default: 10)
- `offset`: Number of records to skip (default: 0)

### Get Specific Match

```
GET /history/{match_id}
```

## Testing

Run tests with pytest:

```bash
pytest
```

## Project Structure

```
job-matcher/
├── app/
│   ├── main.py          # FastAPI application
│   ├── models.py        # Pydantic models
│   ├── matcher.py       # OpenAI integration
│   ├── database.py      # DuckDB integration
│   ├── file_utils.py    # File processing utilities
│   └── static/          # Frontend files
│       ├── index.html
│       ├── styles.css
│       └── script.js
├── test/
│   └── test_matcher.py  # Tests for matcher module
├── .env                 # Environment variables
├── .env.example         # Example environment variables
├── Dockerfile           # Docker configuration
└── requirements.txt     # Python dependencies
```

## License

MIT
