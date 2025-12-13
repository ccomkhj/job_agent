# Job Agent Backend - Multi-Agent FastAPI Server

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/LangChain-000000?style=for-the-badge)](https://www.langchain.com/)
[![OpenRouter](https://img.shields.io/badge/OpenRouter-FF6B35?style=for-the-badge)](https://openrouter.ai/)

The backend component of Job Agent, a sophisticated multi-agent system built with FastAPI and LangChain for intelligent job application assistance.

## 🏗️ Architecture Overview

### Multi-Agent Pipeline

```
User Request → API Gateway → Data Collector Agent → Writer Agent → Feedback Agent → Modificator Agent → Response
```

The system uses **4 specialized AI agents**, each with a single responsibility:

1. **Data Collector Agent**: Analyzes job descriptions and filters relevant user profile data
2. **Writer Agent**: Generates professional cover letters and HR question answers
3. **Feedback Agent**: Reviews generated content and suggests improvements
4. **Modificator Agent**: Applies user-selected feedback to refine content

### Core Components

```
backend/
├── main.py                 # FastAPI application & server setup
├── api/routes.py          # REST API endpoints
├── agents/                # LangChain-powered AI agents
│   ├── data_collector.py  # Profile-job matching logic
│   ├── writer.py          # Content generation
│   ├── feedback.py        # Quality assessment
│   └── modificator.py     # Content refinement
├── chains/                # Orchestration pipelines
│   ├── cover_letter_chain.py    # Cover letter workflow
│   └── question_answer_chain.py # HR question workflow
├── loaders/               # Data ingestion utilities
│   └── job_description_loader.py # Web scraping & parsing
├── schemas/               # Data models & validation
│   └── models.py          # Pydantic schemas
├── prompts/               # LLM prompt templates
│   ├── data_collector.txt # Profile filtering prompts
│   ├── writer.txt         # Content generation prompts
│   ├── feedback.txt       # Review & feedback prompts
│   └── modificator.txt    # Refinement prompts
├── utils/                 # Helper utilities
│   └── profile_normalizer.py # Profile processing
└── pyproject.toml         # Python dependencies
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- OpenRouter API key

### Installation

1. **Install dependencies**
   ```bash
   uv sync
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your OpenRouter API key
   ```

3. **Run the server**
   ```bash
   python main.py
   ```

The server will start on `http://localhost:8000` with automatic reloading in development mode.

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Required: OpenRouter API Configuration
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxx

# Optional: Server Configuration
PORT=8000
HOST=0.0.0.0
ENVIRONMENT=development

# Optional: CORS Settings
FRONTEND_URL=http://localhost:5173
```

### LLM Configuration

The system uses **GPT-4o-mini** via OpenRouter for optimal balance of:
- **Cost efficiency**: Lower API costs
- **Performance**: Sufficient intelligence for content generation
- **Speed**: Fast response times
- **Consistency**: Low temperature (0.1) for deterministic outputs

## 📡 API Endpoints

### Generate Cover Letter
```http
POST /api/generate/cover-letter
```

**Request Body:**
```json
{
  "job_description_url": "https://example.com/job-posting",
  "user_profile": {
    "career_background": {
      "data_science": "Machine learning experience...",
      "data_engineering": "ETL pipeline development...",
      "computer_vision": "OpenCV and deep learning...",
      "cto": "Technical leadership experience..."
    },
    "education_background": "MS in Computer Science...",
    "motivation": "Passionate about data-driven solutions..."
  }
}
```

**Response:**
```json
{
  "cover_letter": {
    "title": "Cover Letter – Senior Data Engineer",
    "body": "Dear Hiring Manager,\n\n[Generated cover letter text]",
    "key_points_used": [
      "5+ years building data pipelines → aligns with ETL requirements",
      "AWS + Spark experience → matches cloud stack"
    ]
  },
  "feedback": {
    "feedback_items": [
      {
        "type": "tone",
        "suggestion": "Make the opening paragraph more confident"
      }
    ]
  },
  "job_summary": {
    "title": "Senior Data Engineer",
    "role_summary": "Design and implement scalable data pipelines...",
    "company_context": "Leading technology company..."
  },
  "filtered_profile": {
    "selected_profile_version": "Data Engineer",
    "relevant_skills": ["Python", "SQL", "AWS", "Spark"],
    "relevant_experience": ["Built data pipelines at Company X"],
    "relevant_education": ["MS in Computer Science"],
    "motivational_alignment": "Passionate about building scalable data infrastructure"
  }
}
```

### Answer HR Question
```http
POST /api/generate/answer
```

**Request Body:**
```json
{
  "job_description_url": "https://example.com/job-posting",
  "hr_question": "Why are you interested in this position?",
  "user_profile": { /* same as above */ }
}
```

**Response:**
```json
{
  "answer": {
    "answer": "I'm interested in this position because...",
    "assumptions": ["Assumed 3+ years of relevant experience"],
    "follow_up_question": null
  },
  "feedback": { /* feedback items */ },
  "job_summary": { /* job information */ },
  "filtered_profile": { /* filtered profile data */ }
}
```

### Apply Feedback (Modify Content)
```http
POST /api/modify
```

**Request Body:**
```json
{
  "original_output": {
    "title": "Cover Letter – Senior Data Engineer",
    "body": "Original content...",
    "key_points_used": ["key point 1", "key point 2"]
  },
  "selected_feedback": [
    {
      "type": "tone",
      "suggestion": "Make the opening paragraph more confident"
    }
  ],
  "output_type": "cover_letter"
}
```

## 🤖 Agent System Deep Dive

### 1. Data Collector Agent
**Purpose**: Intelligently match user profiles to job requirements

**Process**:
- Fetches and parses job descriptions from URLs
- Analyzes required skills, experience, and qualifications
- Maps user profile variants to job needs
- Filters irrelevant experience while preserving job-relevant data

**Key Features**:
- Supports multiple career tracks per user
- Uses semantic matching to identify relevant experience
- Maintains data integrity and prevents hallucination

### 2. Writer Agent
**Purpose**: Generate professional, tailored content

**Capabilities**:
- **Cover Letters**: Job-specific, professional formatting
- **HR Questions**: Direct, contextual answers
- **Constraint Enforcement**: Only uses provided data

**Quality Assurance**:
- Professional tone and structure
- Job-specific customization
- Factual accuracy guaranteed

### 3. Feedback Agent
**Purpose**: Provide constructive improvement suggestions

**Feedback Types**:
- **Tone**: Adjust formality, confidence, enthusiasm
- **Alignment**: Better job requirement matching
- **Clarity**: Improve readability and precision
- **Emphasis**: Highlight key qualifications
- **Structure**: Optimize content organization

### 4. Modificator Agent
**Purpose**: Apply user-approved refinements

**Process**:
- Preserves original facts and data
- Implements only selected feedback
- Maintains professional standards
- Ensures consistency with job requirements

## 🔧 Development

### Running in Development Mode
```bash
python main.py
# Server runs with auto-reload enabled
```

### API Documentation
Visit `http://localhost:8000/docs` for interactive API documentation.

### Testing
```bash
# Run with test environment
ENVIRONMENT=test python main.py
```

### Environment Configurations
- **development**: Auto-reload, debug logging
- **production**: Optimized performance, production logging
- **test**: Isolated testing environment

## 📊 Quality Assurance

### Hallucination Prevention
- **Strict Prompts**: Explicit instructions to use only provided data
- **Schema Validation**: Pydantic models enforce data structure
- **Factual Verification**: All claims traceable to user input

### Performance Optimization
- **Async Processing**: Non-blocking I/O operations
- **Connection Pooling**: Efficient HTTP client management
- **Caching**: LLM instance reuse and prompt template caching

### Error Handling
- **Graceful Degradation**: Fallback responses for failures
- **Comprehensive Logging**: Detailed error tracking
- **User-Friendly Messages**: Clear error communication

## 🔒 Security

- **API Key Protection**: Secure environment variable handling
- **Input Validation**: Pydantic schema enforcement
- **CORS Configuration**: Controlled cross-origin access
- **Rate Limiting**: Built-in request throttling (configurable)

## 📈 Monitoring

The system provides comprehensive logging for:
- API request/response cycles
- Agent processing times
- LLM API usage and costs
- Error rates and failure patterns

## 🚀 Deployment

### Docker Deployment
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install uv && uv sync --no-dev
COPY . .
EXPOSE 8000
CMD ["python", "main.py"]
```

### Production Environment Variables
```env
ENVIRONMENT=production
OPENROUTER_API_KEY=your-production-key
HOST=0.0.0.0
PORT=8000
```

## 🤝 Contributing

### Code Standards
- Type hints for all functions
- Comprehensive docstrings
- Unit tests for all agents
- Pre-commit hooks for code quality

### Testing Strategy
- Unit tests for individual agents
- Integration tests for chains
- End-to-end API testing
- LLM output validation tests

---

**Part of the Job Agent multi-agent system.** See [main README](../README.md) for complete project overview.
