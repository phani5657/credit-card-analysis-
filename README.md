# Credit Card Statement Analysis Assistant

A backend application built with Python and FastAPI to analyse credit card statement data using LLMs and Retrieval-Augmented Generation (RAG).

The project allows users to ask questions about their credit card statement data in natural language. Depending on the question, the application retrieves relevant information from the stored data and uses Gemini to generate a response.

Some example questions include:

* What was my highest transaction?
* How much did I spend on Amazon?
* Show me my transactions from last month.
* What is my outstanding balance?
* When is my payment due?

## What I used

* **Python**
* **FastAPI**
* **SQLAlchemy**
* **Gemini API**
* **RAG and vector retrieval**
* **Database for storing statement data**

## How it works

The backend receives a question, processes it, retrieves the relevant information, and sends the required context to the LLM to generate an answer.

The project also explores hybrid retrieval. Some questions are better handled using structured database queries, while others can benefit from semantic or vector-based search.

For example, finding the highest transaction is mainly a database operation, while finding information related to a broader question may require semantic retrieval.

## Project structure

```text id="8eghit"
app/
├── api/
├── core/
├── models/
├── schemas/
├── services/
│   ├── hybrid_retrieval_service.py
│   ├── answer_service.py
│   └── query_processing.py
└── main.py
```

## Running the project

Clone the repository:

```bash id="qzeu4t"
git clone <repository-url>
cd credit-card-analyser
```

Install the dependencies:

```bash id="6yqazr"
pip install -r requirements.txt
```

Add the required environment variables to a `.env` file:

```env id="uwr0iz"
GEMINI_API_KEY=your_api_key
DATABASE_URL=your_database_url
```

Run the application:

```bash id="phov96"
uvicorn app.main:app --reload
```

The API documentation will be available at `/docs`.

## Current status

This project is still under development. I am building it mainly to understand how backend systems, databases, RAG, retrieval, and LLMs can be combined in a real application.

More features and improvements will be added as the project develops.
