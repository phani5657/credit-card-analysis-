# CreditWise — AI Credit Card Statement Analyzer

CreditWise is an AI-powered application that allows users to upload credit card statements and ask questions about their spending using natural language.

Instead of manually going through a lengthy statement, users can ask questions such as:

- How much did I spend on food?
- What were my top 5 transactions?
- How much did I spend on Amazon?
- What were my biggest expenses?

The application extracts transaction data from the PDF and uses an LLM to understand the user's question and generate an answer based on the available statement data.

## Features

- PDF statement processing and transaction extraction
- Natural language questions about spending
- Retrieval of relevant statement information
- Spending analysis by amount, merchant, category, and transaction
- JWT-based authentication
- PostgreSQL database integration
- REST APIs using FastAPI

## Architecture

```text
User
 |
 v
Frontend
 |
 v
FastAPI Backend
 |
 +-- Authentication
 |
 +-- PDF Processing
 |
 +-- Transaction Processing
 |
 +-- Database
 |
 +-- AI / Retrieval
       |
       v
      LLM
       |
       v
  Final Answer
```

Query flow:

```text
User Question
      |
      v
Understand Query
      |
      v
Retrieve Relevant Statement Data
      |
      v
LLM Processing
      |
      v
Final Answer
```

## Tech Stack

Backend:
- Python
- FastAPI
- SQLAlchemy
- Pydantic
- JWT Authentication
- Uvicorn

AI:
- Google Gemini
- LangChain
- Retrieval and context-based prompting

Database:
- PostgreSQL
- Supabase

Document Processing:
- pypdf

Frontend:
- HTML
- CSS
- JavaScript

Deployment:
- GitHub
- Cloud deployment

## Project Structure

```text
CreditWise/
|
+-- backend/
|   +-- main.py
|   +-- models.py
|   +-- schemas.py
|   +-- database.py
|   +-- auth.py
|   +-- llm.py
|
+-- frontend/
|   +-- index.html
|   +-- login.html
|   +-- style.css
|   +-- script.js
|
+-- requirements.txt
+-- .env
+-- README.md
```

## Getting Started

### 1. Clone the repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd CreditWise
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file:

```env
GEMINI_API_KEY=your_api_key
DATABASE_URL=your_database_url
JWT_SECRET_KEY=your_secret_key
```

### 5. Run the backend

```bash
uvicorn main:app --reload
```

API documentation:

```text
http://localhost:8000/docs
```

## Example Queries

```text
How much did I spend this month?
```

```text
What were my biggest transactions?
```

```text
How much did I spend on Amazon?
```

```text
How much did I spend on food?
```

```text
Show transactions above ₹5,000.
```

## Key Engineering Challenge

A major challenge is ensuring that the LLM answers using the actual transaction data from the uploaded statement rather than generating unsupported financial information.

The application follows this approach:

```text
LLM
 |
 v
Understand the question
 |
 v
Retrieve and process relevant transaction data
 |
 v
LLM
 |
 v
Generate the final response
```

For financial calculations, future improvements can move more calculations into deterministic backend functions instead of relying entirely on the LLM.

## Future Improvements

- Support statements from multiple banks and formats
- Improve automatic transaction categorization
- Add spending dashboards and visualizations
- Support multi-month spending analysis
- Move financial calculations to deterministic backend functions
- Improve retrieval for large statements
- Add more advanced AI agent workflows

## Author

Phanindra Sadanala

IIT Madras

Built as a practical project to explore LLM applications, retrieval, backend engineering, and AI-powered financial analysis.
