**(LangChain-centric, multi-agent, full-stack)**

---

## Role & Context

You are a **senior full-stack engineer and LLM architect**.
Your task is to design and implement a **LangChain-based multi-agent system** with a FastAPI backend and a Vite frontend.

The system assists users in:

1. Writing **tailored cover letters**
2. Answering **free-text HR application questions**

The outputs must be **job-specific**, **profile-consistent**, and **hallucination-free**.

---

## 1) High-Level Architecture

### Core Principle

Use **LangChain as the primary orchestration layer**:

* PromptTemplates
* Chains
* Agents
* Tools
* (Optional) Memory

The backend follows a **multi-agent pipeline**, where each agent has a single responsibility.

---

## 2) Backend Multi-Agent Design

### Agent Overview

#### 1. **Data Collector Agent**

**Responsibility**

* Analyze job description
* Select the *most relevant version(s)* of the user profile
* Produce a **job-aligned profile summary**

**Key logic**

* Users may have **multiple profile variants**, e.g.:

  * Data Scientist
  * Data Engineer
  * Computer Vision Engineer
  * CTO / Technical Leader

The agent must:

* Match job requirements → relevant career tracks
* Exclude unrelated experience
* Produce a **condensed, role-specific profile**

**Output (structured)**

```json
{
  "selected_profile_version": "Data Engineer",
  "relevant_skills": [],
  "relevant_experience": [],
  "relevant_education": [],
  "motivational_alignment": ""
}
```

---

#### 2. **Writer Agent**

**Responsibility**

* Generate:

  * Cover letter OR
  * HR question answer
* Use **only** the filtered data from the Data Collector Agent

**Constraints**

* No hallucinated employers, dates, titles, metrics
* No irrelevant career paths
* Professional, concise tone

---

#### 3. **Feedback Agent**

**Responsibility**

* Critically review the Writer Agent’s output
* Suggest **optional improvements**, such as:

  * Tone adjustment
  * Stronger alignment with job requirements
  * Clarity or conciseness
  * Missing emphasis on key skills

**Important**

* Feedback is **non-destructive**
* Feedback does **not** modify text automatically

**Output**

```json
{
  "feedback_items": [
    {
      "type": "tone",
      "suggestion": "Make the opening paragraph more confident."
    }
  ]
}
```

---

#### 4. **Modificator Agent**

**Responsibility**

* Apply **only user-selected feedback**
* Modify Writer Agent output accordingly
* Preserve original facts and structure

---

## 3) LangChain Component Design

### Required Components

#### `JobDescriptionLoader`

* Fetch job description from URL
* Clean & extract:

  * Responsibilities
  * Requirements
  * Role summary
  * Company context
* Fail fast if URL is unreachable

---

#### `ProfileNormalizer`

* Accepts arbitrary user profile schema
* Produces a canonical structured profile
* Supports **multiple profile variants per user**

---

#### Chains / Agents

* `DataCollectorChain`
* `CoverLetterWriterChain`
* `QuestionAnswerWriterChain`
* `FeedbackChain`
* `ModificationChain`

Each chain must:

* Use **PromptTemplate**
* Enforce **schema-locked output**
* Receive only required inputs

---

## 4) Inputs

### Backend Input Schema

#### User Profile

```json
{
  "career_background": {
    "data_science": "...",
    "data_engineering": "...",
    "computer_vision": "...",
    "cto": "..."
  },
  "education_background": "...",
  "motivation": "..."
}
```

#### Request Inputs

* `job_description_url` (required)
* `hr_question` (required only for question answering)

---

## 5) Output Requirements

### Cover Letter Output

```json
{
  "title": "Cover Letter – Senior Data Engineer",
  "body": "…",
  "key_points_used": [
    "5+ years building data pipelines → aligns with ETL requirements",
    "AWS + Spark experience → matches cloud stack"
  ]
}
```

---

### HR Question Answer Output

```json
{
  "answer": "…",
  "assumptions": [],
  "follow_up_question": null
}
```

If required info is missing:

* Ask **exactly one** clarification question
* Do not guess

---

## 6) API Endpoints

### Required Endpoints

#### Generate Cover Letter

```
POST /generate/cover-letter
```

```json
{
  "job_description_url": "...",
  "user_profile": {...}
}
```

---

#### Answer HR Question

```
POST /generate/answer
```

```json
{
  "job_description_url": "...",
  "hr_question": "...",
  "user_profile": {...}
}
```

---

#### Apply Feedback (Optional but Recommended)

```
POST /modify
```

```json
{
  "original_output": {...},
  "selected_feedback": [...]
}
```

---

## 7) Frontend (Vite)

### Minimal UI (MVP)

* Job Description URL input
* HR Question textbox
* Buttons:

  * **Write Cover Letter**
  * **Answer Question**
* Output panel:

  * Pretty-printed JSON
  * Copy-to-clipboard

---

## 8) Chat Interface Extension (Suggested)

### Why Chat?

A chat interface improves:

* Iterative refinement
* Feedback selection
* Clarification questions

### Suggested Chat Flow

```
User: Writes job URL
System: Shows extracted job summary
User: Clicks “Write cover letter”
System: Shows draft
System: Shows suggested feedback (checkboxes)
User: Selects feedback
User: Clicks “Apply changes”
```

### Chat Design Notes

* Chat is **stateful**, but memory should be:

  * Per session
  * Short-lived
* Use LangChain memory only for:

  * Last draft
  * Selected feedback
* Avoid long conversation replay

---

## 9) Backend Folder Structure (Suggested)

```
backend/
├── main.py
├── api/
│   └── routes.py
├── agents/
│   ├── data_collector.py
│   ├── writer.py
│   ├── feedback.py
│   └── modificator.py
├── chains/
│   ├── cover_letter_chain.py
│   └── question_answer_chain.py
├── loaders/
│   └── job_description_loader.py
├── schemas/
│   └── models.py
├── prompts/
│   ├── data_collector.prompt
│   ├── writer.prompt
│   ├── feedback.prompt
│   └── modificator.prompt
```

---

## 10) Quality & Safety Constraints

* Never invent:

  * Companies
  * Dates
  * Degrees
  * Metrics
* Use **only provided profile + job description**
* Deterministic JSON outputs
* Strict schema validation with Pydantic
* Fail loudly on missing or invalid data
