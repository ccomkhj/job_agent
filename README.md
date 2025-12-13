# Job Agent - Multi-Agent Job Application Assistant

[![Backend](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square)](https://fastapi.tiangolo.com/)
[![Frontend](https://img.shields.io/badge/Frontend-React-61DAFB?style=flat-square)](https://reactjs.org/)
[![AI](https://img.shields.io/badge/AI-LangChain-000000?style=flat-square)](https://www.langchain.com/)
[![LLM](https://img.shields.io/badge/LLM-OpenRouter-FF6B35?style=flat-square)](https://openrouter.ai/)

An intelligent, multi-agent job application assistant built with LangChain and FastAPI that helps users create tailored cover letters and answer HR questions using AI-powered analysis.

## 🎯 Achievements

### ✅ **Complete Multi-Agent System Implementation**
- **4 Specialized Agents**: Data Collector, Writer, Feedback, and Modificator agents
- **LangChain Integration**: Full orchestration using LangChain chains and prompts
- **Hallucination-Free**: Strict constraints ensure only provided information is used
- **Job-Specific Content**: Intelligent profile filtering based on job requirements

### ✅ **Full-Stack Application**
- **Backend**: FastAPI with comprehensive API endpoints and error handling
- **Frontend**: React + TypeScript chat interface with modern UX
- **Real-time Communication**: Seamless frontend-backend integration
- **Responsive Design**: Mobile-friendly interface

### ✅ **Advanced Features**
- **Multi-Career Profile Support**: Data Science, Data Engineering, Computer Vision, CTO tracks
- **Iterative Refinement**: AI feedback system with user-controlled improvements
- **Professional Output**: Polished cover letters and HR answers
- **Copy-to-Clipboard**: Easy content export functionality

### ✅ **Production-Ready Architecture**
- **Type Safety**: Full Pydantic and TypeScript validation
- **Error Handling**: Comprehensive error management and fallbacks
- **Scalable Design**: Modular agent architecture for easy extension
- **Clean Code**: Well-structured, documented, and maintainable codebase

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- OpenRouter API key ([get one here](https://openrouter.ai/))

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd job_agent
   ```

2. **Backend Setup**
   ```bash
   cd backend
   uv sync  # Install dependencies

   # Configure environment variables
   cp .env.example .env
   # Edit .env with your OpenRouter API key
   ```

3. **Frontend Setup**
   ```bash
   cd ../frontend
   npm install  # Install dependencies
   ```

### Running the Application

1. **Start Backend** (Terminal 1)
   ```bash
   cd backend
   python main.py
   ```
   Backend will run on `http://localhost:8000`

2. **Start Frontend** (Terminal 2)
   ```bash
   cd frontend
   npm run dev
   ```
   Frontend will run on `http://localhost:5173`

3. **Open Browser**
   Navigate to `http://localhost:5173` to use the application

## ⚙️ Environment Configuration

### Backend Configuration

The backend reads configuration from a `.env` file in the `backend/` directory:

```env
# Required: OpenRouter API Configuration
OPENROUTER_API_KEY=your-openrouter-api-key-here

# Optional: Server Configuration
PORT=8000
HOST=0.0.0.0
ENVIRONMENT=development

# Optional: CORS Settings
FRONTEND_URL=http://localhost:5173
```

**Setup:**
```bash
cd backend
cp .env.example .env
# Edit .env with your actual OpenRouter API key
```

### Frontend Configuration

The frontend can be configured via environment variables in `.env.local`:

```env
VITE_API_URL=http://localhost:8000/api
VITE_APP_NAME=Job Agent
```

## 📚 Detailed Documentation

For comprehensive technical details:

### Backend Architecture
📖 **[Backend README](backend/README.md)**
- Multi-agent system deep dive
- API endpoint specifications
- Agent responsibilities and workflows
- Development and deployment guides

### Frontend Architecture
📖 **[Frontend README](frontend/README.md)**
- Component hierarchy and data flow
- UI/UX design principles
- Development workflow and tooling
- Performance optimization strategies

## 📖 How to Use

### Step 1: Enter Job Posting
- Paste the URL of the job posting you want to apply for
- The system will analyze the job requirements and responsibilities

### Step 2: Set Up Your Profile
- Fill in your professional background across multiple career tracks:
  - **Data Science**: ML/AI experience, analytics work
  - **Data Engineering**: ETL, pipelines, big data technologies
  - **Computer Vision**: CV engineering, image processing
  - **CTO/Leadership**: Technical leadership, management experience
- Add your education background and motivation/goals
- Profile is automatically saved for future use

### Step 3: Generate Content
Choose from two options:

#### **Write Cover Letter**
- Click "Write Cover Letter"
- AI analyzes your profile and matches relevant experience to job requirements
- Receives a tailored, professional cover letter

#### **Answer HR Question**
- Enter the specific HR question you need to answer
- Or select from common questions (Why this role? Why leaving current job? etc.)
- Gets a customized, job-specific answer

### Step 4: Review and Improve
- AI automatically provides feedback suggestions
- Review tone, alignment, clarity, and emphasis recommendations
- Select which feedback items to apply
- Click "Apply Selected Feedback" for iterative improvements

### Step 5: Export Results
- Copy the final content to clipboard
- Use in your job application materials

## 🏗️ Architecture

### Backend Architecture
```
backend/
├── main.py                 # FastAPI application
├── api/routes.py          # API endpoints
├── agents/                # LangChain agents
│   ├── data_collector.py  # Analyzes jobs & selects profile data
│   ├── writer.py          # Generates cover letters & answers
│   ├── feedback.py        # Reviews and suggests improvements
│   └── modificator.py     # Applies user-selected feedback
├── chains/                # Orchestration chains
│   ├── cover_letter_chain.py
│   └── question_answer_chain.py
├── loaders/               # Data loading utilities
│   └── job_description_loader.py
├── schemas/               # Pydantic models
│   └── models.py
├── prompts/               # LangChain prompt templates
└── utils/                 # Helper utilities
    └── profile_normalizer.py
```

### Frontend Architecture
```
frontend/
├── src/
│   ├── components/        # React components
│   │   ├── ChatInterface.tsx    # Main chat UI
│   │   ├── MessageBubble.tsx    # Message display
│   │   ├── OutputDisplay.tsx    # Content display
│   │   ├── FeedbackSelector.tsx # Feedback interface
│   │   └── [input components]   # Form components
│   ├── services/          # API client
│   │   └── api.ts
│   ├── types/             # TypeScript definitions
│   │   └── index.ts
│   └── styles/            # CSS styles
│       └── App.css
```

### Data Flow
```
User Input → Job URL Analysis → Profile Filtering → Content Generation → Feedback → User Refinement → Final Output
```

## 🛠️ Technology Stack

### Backend
- **FastAPI**: High-performance async web framework
- **LangChain**: LLM orchestration and chaining
- **OpenRouter**: LLM provider abstraction
- **Pydantic**: Data validation and serialization
- **httpx**: Async HTTP client for job fetching
- **BeautifulSoup4**: HTML parsing for job descriptions
- **uv**: Fast Python package manager

### Frontend
- **React 19**: Modern React with hooks
- **TypeScript**: Type-safe JavaScript
- **Vite**: Fast build tool and dev server
- **Axios**: HTTP client for API calls
- **CSS**: Custom responsive styling

## 🔧 API Endpoints

### Generate Cover Letter
```http
POST /api/generate/cover-letter
Content-Type: application/json

{
  "job_description_url": "https://example.com/job",
  "user_profile": {
    "career_background": {
      "data_science": "...",
      "data_engineering": "...",
      // ...
    },
    "education_background": "...",
    "motivation": "..."
  }
}
```

### Answer HR Question
```http
POST /api/generate/answer
Content-Type: application/json

{
  "job_description_url": "https://example.com/job",
  "hr_question": "Why are you interested in this position?",
  "user_profile": { /* ... */ }
}
```

### Apply Feedback
```http
POST /api/modify
Content-Type: application/json

{
  "original_output": { /* generated content */ },
  "selected_feedback": [ /* selected feedback items */ ],
  "output_type": "cover_letter" | "question_answer"
}
```

## 🎨 Features

### Intelligent Profile Matching
- Automatically selects the most relevant career experience for each job
- Filters out irrelevant skills and experience
- Ensures job-specific, targeted content

### Professional Content Generation
- No hallucinated information - only uses provided data
- Professional tone and structure
- Tailored to specific job requirements
- Supports both cover letters and HR questions

### Iterative Improvement
- AI-powered feedback on tone, alignment, clarity
- User-controlled refinement process
- Multiple rounds of improvement possible
- Maintains original facts while enhancing presentation

### User-Friendly Interface
- Chat-based interaction flow
- Real-time feedback and validation
- Copy-to-clipboard functionality
- Mobile-responsive design

## 🚀 Future Enhancements

- **Session Management**: Persistent chat sessions across browser refreshes
- **Profile Templates**: Pre-built profile templates for common roles
- **Batch Processing**: Generate content for multiple jobs simultaneously
- **Analytics Dashboard**: Track application success rates and content performance
- **Integration APIs**: Connect with LinkedIn, Indeed, and other job platforms
- **Advanced AI Models**: Support for multiple LLM providers and models

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests, report issues, or suggest enhancements.

## 📞 Support

For questions or support, please open an issue on the GitHub repository.

---

**Built with ❤️ using LangChain, FastAPI, and React**
