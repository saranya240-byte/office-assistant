#  TechNova AI Office Assistant

An AI-powered internal employee assistant for **TechNova Pvt. Ltd.** that helps employees access company policies, employee information, leave balances, IT assets, office information, reimbursement details, and submit leave requests through a conversational interface.

The system combines **multi-agent orchestration, Retrieval-Augmented Generation (RAG), FAISS vector search, local sentence-transformer embeddings, employee data tools, action handling, memory, and a Streamlit UI** to provide a reliable internal office assistant.

---

##  Table of Contents

1. [Project Overview](#-project-overview)
2. [Problem Statement](#-problem-statement)
3. [Objectives](#-objectives)
4. [Key Features](#-key-features)
5. [System Architecture](#-system-architecture)
6. [Project Flow](#-project-flow)
7. [Technology Stack](#-technology-stack)
8. [Project Structure](#-project-structure)
9. [Agent Architecture](#-agent-architecture)
10. [Intent Classification](#-intent-classification)
11. [Orchestrator](#-orchestrator)
12. [Policy RAG System](#-policy-rag-system)
13. [FAISS Vector Store](#-faiss-vector-store)
14. [Local Embedding Model](#-local-embedding-model)
15. [Employee Data Handling](#-employee-data-handling)
16. [Leave Application Flow](#-leave-application-flow)
17. [Response Generation](#-response-generation)
18. [Memory](#-memory)
19. [Streamlit UI](#-streamlit-ui)
20. [Error Handling](#-error-handling)
21. [Testing](#-testing)
22. [Performance](#-performance)
23. [Challenges and Solutions](#-challenges-and-solutions)
24. [Installation](#-installation)
25. [Running the Application](#-running-the-application)
26. [Example Queries](#-example-queries)
27. [End-to-End Examples](#-end-to-end-examples)
28. [Security and Reliability](#-security-and-reliability)
29. [Limitations](#-limitations)
30. [Future Enhancements](#-future-enhancements)
31. [Conclusion](#-conclusion)

---

# 📖 Project Overview

The **TechNova AI Office Assistant** is designed to act as a centralized conversational interface for employees.

Instead of searching through multiple policy documents, employee databases, or IT information manually, employees can simply ask questions using natural language.

### Examples

```text
What is the work from home policy?

How many casual leaves do I have?

What laptop is assigned to me?

What are the reimbursement rules?

Where is my office located?

Apply casual leave from 2026-09-10 to 2026-09-12.
```

The assistant identifies the employee's intent, routes the request to the appropriate agent or tool, retrieves relevant information, and returns an employee-friendly response.

---

#  Problem Statement

Employees often need to access information from different sources such as:

* Employee records
* Leave management systems
* Company policies
* IT asset information
* Office guidelines
* Reimbursement policies
* Security policies

Manually searching these sources can be time-consuming and inefficient.

The goal of this project is to create a **single conversational AI interface** through which employees can access this information quickly and naturally.

---

# Objectives

The main objectives of the project are:

* Provide a conversational employee assistant.
* Automatically identify the user's intent.
* Route queries to the appropriate agent.
* Retrieve policy information using RAG.
* Use FAISS for efficient vector similarity search.
* Use local embeddings for policy retrieval.
* Provide employee-specific information.
* Display IT asset information.
* Display leave balances.
* Handle leave applications.
* Extract leave parameters from natural language.
* Maintain conversational context.
* Provide a simple Streamlit-based UI.
* Prevent unsupported information from being fabricated.
* Provide source information for policy answers.
* Support reliable local execution.

---

# ✨ Key Features

## 1. Policy Question Answering

Employees can ask questions about:

* Leave policies
* Work-from-home policies
* Reimbursement policies
* Security policies
* IT policies
* Office guidelines
* Employee handbook
* Benefits
* Onboarding

Policy documents are processed using a RAG pipeline.

---

## 2. Employee Information

The assistant can provide information such as:

* Employee name
* Employee ID
* Designation
* Department
* Manager
* Office location

---

## 3. Leave Balance

Employees can check:

* Casual Leave
* Earned Leave
* Sick Leave

---

## 4. Leave Application

Employees can submit leave requests through natural language.

Example:

```text
Apply casual leave from 2026-09-10 to 2026-09-12
because I have personal work.
```

The system extracts:

```text
Leave Type → Casual Leave
Start Date → 2026-09-10
End Date → 2026-09-12
Reason → Personal work
```

---

## 5. IT Asset Information

The assistant can provide assigned IT asset information such as:

* Laptop
* Desktop
* Asset ID
* Serial number
* Other assigned equipment

---

## 6. Office Information

Employees can ask about:

* Office location
* Address
* Working hours
* Working days
* Office guidelines

---

## 7. Expense and Reimbursement Information

The assistant can answer questions related to:

* Reimbursement policies
* Expense claims
* Required documents
* Eligible expenses

---

## 8. Conversational UI

The application provides a Streamlit-based chat interface.

Employees can enter their employee ID and ask questions through a chat box.

---

# 🏗️ System Architecture

```text
                         ┌──────────────────────┐
                         │      Employee        │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   Streamlit UI       │
                         │   Chat Interface     │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    Orchestrator      │
                         └──────────┬───────────┘
                                    │
                         ┌──────────┴──────────┐
                         │                     │
                         ▼                     ▼
                ┌────────────────┐    ┌─────────────────┐
                │  Intent Agent  │    │ Parameter Agent │
                └───────┬────────┘    └────────┬────────┘
                        │                      │
          ┌─────────────┼──────────────┐       │
          │             │              │       │
          ▼             ▼              ▼       ▼
     ┌─────────┐   ┌────────────┐  ┌─────────────┐
     │ Policy  │   │ Employee   │  │ Action      │
     │ Agent   │   │ Agent      │  │ Agent       │
     └────┬────┘   └─────┬──────┘  └──────┬──────┘
          │              │                 │
          ▼              ▼                 ▼
       ┌──────┐      ┌────────┐       ┌──────────┐
       │ RAG  │      │Employee│       │Leave /   │
       │FAISS │      │ Data   │       │Actions   │
       └──┬───┘      └────────┘       └──────────┘
          │
          ▼
    ┌──────────────┐
    │ Policy PDFs  │
    └──────────────┘

                         │
                         ▼
                ┌──────────────────┐
                │ Response Agent   │
                └────────┬─────────┘
                         │
                         ▼
                ┌──────────────────┐
                │ Employee Answer  │
                └──────────────────┘
```

---

# Project Flow

The complete request flow is:

```text
User Query
    ↓
Streamlit UI
    ↓
Orchestrator
    ↓
Intent Classification
    ↓
Intent-based Routing
    ↓
┌───────────────┬──────────────────┬─────────────────┐
│               │                  │
Policy          Employee           Action
│               │                  │
↓               ↓                  ↓
RAG             Employee Tool      Parameter Extraction
↓               ↓                  ↓
FAISS           Employee Data      Leave Action
↓               │                  │
Relevant        │                  │
Chunks          │                  │
└───────────────┴──────────────────┘
                ↓
         Response Generation
                ↓
          Streamlit UI
                ↓
          Employee Answer
```

---

# Technology Stack

| Component               | Technology                          |
| ----------------------- | ----------------------------------- |
| Programming Language    | Python                              |
| UI                      | Streamlit                           |
| Embedding Model         | Sentence Transformers               |
| Embedding Model         | `all-MiniLM-L6-v2`                  |
| Vector Database         | FAISS                               |
| Policy Retrieval        | RAG                                 |
| LLM Response Generation | Ollama / local LLM where configured |
| Database / Memory       | SQLite where enabled                |
| Document Format         | PDF                                 |
| Testing                 | Pytest                              |
| Version Control         | Git / GitHub                        |

---

#  Project Structure

```text
office-assistant/
│
├── app/
│   ├── __init__.py
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── action_agent.py
│   │   ├── employee_agent.py
│   │   ├── intent_agent.py
│   │   ├── orchestrator.py
│   │   ├── parameter_agent.py
│   │   ├── policy_agent.py
│   │   └── response_agent.py
│   │
│   ├── data/
│   │   └── memory.db
│   │
│   ├── knowledge_base/
│   │   ├── Employee_Handbook.pdf
│   │   ├── WFH_Policy.pdf
│   │   ├── Leave_Policy.pdf
│   │   ├── Reimbursement_Policy.pdf
│   │   ├── Security_Policy.pdf
│   │   ├── Office_Guidelines.pdf
│   │   ├── IT_Policy.pdf
│   │   ├── Onboarding_Guide.pdf
│   │   └── Benefits_Guide.pdf
│   │
│   ├── prompts/
│   │   └── response_prompt.txt
│   │
│   ├── rag/
│   │   ├── document_loader.py
│   │   ├── embeddings.py
│   │   ├── retriever.py
│   │   └── text_splitter.py
│   │
│   ├── vector_store/
│   │   ├── policy_index.faiss
│   │   └── chunks.pkl
│   │
│   ├── utils/
│   │   └── config.py
│   │
│   └── main.py
│
├── tests/
│   ├── test_action_tool.py
│   ├── test_agent.py
│   ├── test_paramater_test.py
│   ├── test_policy_agent.py
│   ├── test_rag.py
│   └── test_response_agent.py
│
├── requirements.txt
├── README.md
└── .env.example
```

---

# 🤖 Agent Architecture

The project follows a modular agent-based architecture.

## Agents

### Intent Agent

Determines what the employee is asking.

Supported intents include:

```text
POLICY
EMPLOYEE_INFO
LEAVE_BALANCE
EXPENSE
IT_ASSET
OFFICE
APPLY_LEAVE
UNKNOWN
```

---

### Policy Agent

Handles policy-related queries.

It connects the query to the RAG system and retrieves relevant sections from the company policy documents.

---

### Employee Agent

Handles employee-related information.

It retrieves information such as:

* Employee details
* Leave balance
* IT assets
* Office information
* Expense-related information

---

### Action Agent

Handles actions such as leave applications.

It validates the request and performs the required operation.

---

### Parameter Agent

Extracts required parameters from natural language.

For leave requests, parameters include:

```text
leave_type
start_date
end_date
reason
```

It also normalizes supported date formats into:

```text
YYYY-MM-DD
```

---

### Response Agent

Converts structured results into employee-friendly responses.

For deterministic business information, predefined responses are used.

For other structured results, the configured response-generation mechanism can be used.

---

### Orchestrator

The orchestrator is the central routing component.

It receives the query and decides which agent should handle it.

Example:

```text
"What is the WFH policy?"
        ↓
Intent Agent
        ↓
POLICY
        ↓
Policy Agent
        ↓
RAG
```

Another example:

```text
"How many casual leaves do I have?"
        ↓
Intent Agent
        ↓
LEAVE_BALANCE
        ↓
Employee Agent
        ↓
Employee Data
```

---

#  Intent Classification

The intent agent maps natural language to one of the supported intents.

Example:

| User Query                        | Intent        |
| --------------------------------- | ------------- |
| What is the WFH policy?           | POLICY        |
| What is the reimbursement policy? | POLICY        |
| What is my designation?           | EMPLOYEE_INFO |
| How many leaves do I have?        | LEAVE_BALANCE |
| What laptop do I have?            | IT_ASSET      |
| Where is my office?               | OFFICE        |
| Apply casual leave                | APPLY_LEAVE   |

If the system cannot identify a supported intent, it returns:

```text
UNKNOWN
```

This prevents unsupported requests from being routed incorrectly.

---

# 📚 Policy RAG System

The project uses **Retrieval-Augmented Generation (RAG)** to answer policy-related questions.

Instead of expecting an LLM to memorize company policies, the system searches the actual company documents.

## Policy Documents

The knowledge base contains documents such as:

```text
Employee Handbook
WFH Policy
Leave Policy
Reimbursement Policy
Security Policy
Office Guidelines
IT Policy
Onboarding Guide
Benefits Guide
```

---

# 🔨 RAG Indexing Pipeline

Policy documents are processed offline.

```text
PDF Documents
      ↓
Text Extraction
      ↓
Text Cleaning
      ↓
Text Chunking
      ↓
Generate Embeddings
      ↓
Sentence Transformer
      ↓
FAISS Index
      ↓
Save Index + Metadata
```

The generated files are:

```text
policy_index.faiss
chunks.pkl
```

---

#  RAG Runtime Pipeline

At runtime, the system does **not** rebuild the complete document index for every query.

Instead:

```text
User Question
      ↓
Generate embedding for question
      ↓
Search existing FAISS index
      ↓
Retrieve top relevant chunks
      ↓
Rerank relevant policy results
      ↓
Return policy information
      ↓
Generate employee response
```

This makes the runtime much faster.

---

#  Embeddings

The project uses:

```text
sentence-transformers/all-MiniLM-L6-v2
```

The model converts text into numerical vectors.

For example:

```text
"What is the WFH policy?"
```

is converted into an embedding vector.

The same process is performed for policy chunks.

The system then compares the query vector with stored document vectors.

---

#  FAISS Vector Store

FAISS is used for similarity search.

The project currently stores:

```text
Vectors : 268
Chunks  : 268
```

The vector store consists of:

```text
app/vector_store/policy_index.faiss
app/vector_store/chunks.pkl
```

### Why FAISS?

* Fast similarity search
* Local execution
* No external database required
* Efficient for vector retrieval
* Suitable for the project's policy knowledge base

---

# ⚡ RAG Optimization

An important optimization was implemented to avoid loading the embedding model and FAISS index repeatedly.

The RAG resources are cached using:

```python
@lru_cache(maxsize=1)
```

Conceptually:

```text
First query
    ↓
Load MiniLM model
    ↓
Load FAISS index
    ↓
Cache resources
    ↓
Retrieve answer
```

Subsequent queries:

```text
New query
    ↓
Use cached model
    ↓
Use cached FAISS index
    ↓
Retrieve answer
```

This avoids unnecessary model initialization.

---

#  Retrieval Reranking

Pure vector similarity can sometimes return a generally related document before the exact policy document.

For example, a WFH query may initially retrieve the employee handbook before the dedicated WFH policy.

To improve this, deterministic policy prioritization is used.

Examples:

```text
WFH / remote / hybrid
        ↓
Prioritize WFH_Policy.pdf

Leave
        ↓
Prioritize Leave_Policy.pdf

Reimbursement / expense
        ↓
Prioritize Reimbursement_Policy.pdf

Password / VPN / security
        ↓
Prioritize Security_Policy.pdf

Laptop / device / IT
        ↓
Prioritize IT_Policy.pdf
```

This improves retrieval relevance without requiring another LLM call.

---

#  Employee Data Flow

For employee-specific queries:

```text
User Query
    ↓
Intent Agent
    ↓
EMPLOYEE_INFO / LEAVE_BALANCE / IT_ASSET / OFFICE
    ↓
Employee Agent
    ↓
Employee Data
    ↓
Structured Result
    ↓
Response Agent
    ↓
Employee Response
```

---

#  Leave Application Flow

Leave applications follow a separate action flow.

```text
Employee Request
       ↓
Intent Agent
       ↓
APPLY_LEAVE
       ↓
Parameter Agent
       ↓
Extract Parameters
       ↓
Validate Parameters
       ↓
Action Agent
       ↓
Submit Leave Request
       ↓
Generate Request ID
       ↓
Response Agent
       ↓
Confirmation
```

Example input:

```text
Apply casual leave from 2026-09-10 to 2026-09-12
because I have personal work.
```

Extracted parameters:

```text
Leave Type : Casual Leave
Start Date : 2026-09-10
End Date   : 2026-09-12
Reason     : Personal work
```

Example response:

```text
Your Casual Leave request has been submitted successfully.

Request ID: ...
Start Date: 2026-09-10
End Date: 2026-09-12
Working Days: ...
Status: Pending
```

---

#  Response Generation

The Response Agent converts structured system output into a user-friendly response.

For deterministic information, predefined response formatting is used.

Examples include:

### Office

```text
Your office is located at ...
Working hours are ...
```

### Leave Balance

```text
You have X Casual Leave days,
Y Earned Leave days,
and Z Sick Leave days remaining.
```

### IT Assets

```text
Your assigned laptop is ...
Asset ID: ...
```

### Leave Application

```text
Your leave request has been submitted successfully.
```

For supported dynamic responses, the configured LLM response-generation layer can also be used.

---

# 🧠 Memory

The project includes conversational memory functionality.

## Short-Term Memory

The Streamlit session maintains the current conversation.

Conceptually:

```text
User message
     ↓
Assistant response
     ↓
Stored in session state
     ↓
Available during current session
```

This allows the interface to display previous messages.

## Long-Term Memory

SQLite-based memory support is included in the project for persistent conversation information where enabled by the current implementation.

Memory is associated with the employee and can store previous interactions.

> The exact long-term-memory behavior should be verified against the current code before claiming persistent memory as a production-ready feature.

---

#  Streamlit UI

The application uses **Streamlit** for the frontend.

The UI provides:

* Application title
* Employee ID input
* Chat interface
* User messages
* Assistant messages
* Loading indicator
* Error messages
* Policy-related interactions

Basic interaction:

```text
┌──────────────────────────────────────────┐
│  TechNova Office Assistant             │
│ AI-powered employee assistant            │
│                                          │
│ Employee ID: TN0001                      │
│                                          │
│ User: What is the WFH policy?            │
│                                          │
│ Assistant: You can work from home...     │
│                                          │
│ ┌──────────────────────────────────────┐ │
│ │ Ask about policies, leave, expenses │ │
│ └──────────────────────────────────────┘ │
└──────────────────────────────────────────┘
```

The UI communicates with:

```text
Streamlit
   ↓
process_query()
   ↓
Orchestrator
```

---

#  Policy Document Access

The UI can provide access to policy information while the assistant handles conversational questions.

This creates two complementary experiences:

```text
View Policy Document
        +
Ask Assistant About Policy
```

This helps employees both inspect the original policy and ask natural-language questions about it.

---

#  Error Handling

The application handles several types of failures.

Examples:

* Unknown intent
* Missing leave parameters
* Invalid date formats
* Missing employee information
* Empty IT asset list
* Failed response generation
* Missing policy information
* Invalid requests

For unsupported questions, the assistant should avoid inventing answers.

Example:

```text
I couldn't determine what you're asking.
Please rephrase your request.
```

---

#  Testing

The project includes automated tests using **Pytest**.

Test areas include:

```text
Action Agent
Intent Agent
Parameter Extraction
Policy Agent
RAG
Response Agent
```

The test suite was used to validate:

* Intent classification
* Leave parameter extraction
* Date normalization
* Policy retrieval
* RAG behavior
* Action handling
* Response generation

The project reached a test state with **29 tests passing** during development.

Run tests using:

```bash
PYTHONPATH="$(pwd)" python -m pytest -q
```

---

#  Performance

One of the major optimizations was separating:

### Offline Processing

```text
PDF
 ↓
Chunk
 ↓
Embed
 ↓
FAISS
```

from:

### Runtime Processing

```text
Question
 ↓
Embed Question
 ↓
FAISS Search
 ↓
Retrieve
```

The runtime retrieval test showed approximately:

```text
Retrieval Time: ~0.45 seconds
```

The RAG model and vector index are loaded only once per Python process using caching.

This confirmed that repeated RAG initialization was not the primary source of UI delay.

---

#  Challenges and Solutions

## 1. Hugging Face SSL Error

### Problem

The environment encountered SSL certificate verification errors while accessing Hugging Face.

### Solution

The locally cached model was used directly.

The model path is loaded from the Hugging Face cache rather than repeatedly downloading it.

Offline mode can be enabled with:

```bash
HF_HUB_OFFLINE=1
```

---

## 2. Repeated RAG Initialization

### Problem

Loading the embedding model repeatedly caused unnecessary overhead.

### Solution

RAG resources were cached:

```python
@lru_cache(maxsize=1)
def load_rag_resources():
    ...
```

---

## 3. Incorrect Retrieval Threshold

### Problem

A fixed similarity threshold of:

```text
score >= 0.50
```

caused valid policy results to be discarded.

For example, relevant Leave Policy results had scores around:

```text
0.47
```

Therefore, the threshold was too strict.

### Solution

The fixed threshold was removed.

The system now relies on:

* Top-k retrieval
* Deterministic policy reranking
* Relevance-based selection

---

## 4. Generic Documents Ranking Above Specific Policies

### Problem

A query about WFH could retrieve the Employee Handbook before the dedicated WFH policy.

### Solution

Deterministic policy prioritization was added.

Example:

```text
WFH query → WFH_Policy.pdf
Leave query → Leave_Policy.pdf
Expense query → Reimbursement_Policy.pdf
Security query → Security_Policy.pdf
IT query → IT_Policy.pdf
```

---

## 5. LLM Dependency and API Issues

During development, external LLM/API approaches encountered issues such as:

* Model availability
* API quota limits
* Rate limiting
* Temporary service unavailability
* Network dependency

The project was therefore designed so that **policy retrieval itself does not depend on an external LLM**.

The local embedding model and FAISS index can perform retrieval independently.

---

#  Security and Reliability

The assistant is designed as an internal employee assistant.

Important principles include:

### Employee Identification

Employee-specific queries use an employee ID.

### Grounded Policy Answers

Policy responses are based on retrieved company documents rather than relying solely on model memory.

### No Fabrication

The response layer is instructed to use only available structured information.

### Local RAG

The embedding model and FAISS index can operate locally.

### Separation of Responsibilities

Different agents handle different responsibilities.

This makes the system easier to test and maintain.

---

# ⚙️ Installation

## 1. Clone the Repository

```bash
git clone <repository-url>
cd office-assistant
```

---

## 2. Create Virtual Environment

```bash
python3 -m venv venv
```

Activate it:

```bash
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure Environment

Create the environment configuration according to the project's `.env.example`.

```bash
cp .env.example .env
```

Configure the required values.

---

#  Running the Application

From the project root:

```bash
source venv/bin/activate
```

Then:

```bash
PYTHONPATH="$(pwd)" streamlit run app/main.py
```

The Streamlit application will start locally.

---

#  Running Tests

Run:

```bash
PYTHONPATH="$(pwd)" python -m pytest -q
```

For more detailed output:

```bash
PYTHONPATH="$(pwd)" python -m pytest -v
```

---

# 🔎 Testing RAG Directly

The policy retrieval system can be tested without the UI.

Example:

```bash
HF_HUB_OFFLINE=1 python -c "from app.agents.policy_agent import retrieve_policy; print(retrieve_policy('What is the work from home policy?'))"
```

This verifies the RAG layer independently from Streamlit.

---

#  Example Queries

## Policy

```text
What is the work from home policy?
```

```text
How many days can I work from home?
```

```text
What is the leave policy?
```

```text
What is the reimbursement policy?
```

```text
What are the password requirements?
```

---

## Employee

```text
What is my designation?
```

```text
Who is my manager?
```

```text
Which department do I work in?
```

---

## Leave

```text
How many casual leaves do I have?
```

```text
How many sick leaves do I have?
```

```text
What is my current leave balance?
```

---

## IT

```text
What laptop is assigned to me?
```

```text
What are my IT assets?
```

---

## Office

```text
Where is my office?
```

```text
What are the office working hours?
```

---

## Leave Application

```text
Apply casual leave from 2026-09-10 to 2026-09-12.
```

```text
Apply sick leave from 2026-09-15 to 2026-09-16 because I am unwell.
```

---

#  End-to-End Example

## Example 1 — WFH Policy

User:

```text
What is the work from home policy?
```

### Step 1 — UI

Streamlit receives the question.

### Step 2 — Orchestrator

The query is sent to:

```python
process_query()
```

### Step 3 — Intent Agent

Classifies:

```text
POLICY
```

### Step 4 — Policy Agent

The query is converted into an embedding.

### Step 5 — FAISS

FAISS searches the stored policy vectors.

### Step 6 — Reranking

The WFH policy is prioritized.

### Step 7 — Response

Relevant policy information is returned.

### Step 8 — UI

The answer is displayed to the employee.

---

#  End-to-End Leave Example

User:

```text
Apply casual leave from 2026-09-10 to 2026-09-12
because I have personal work.
```

Flow:

```text
Streamlit
   ↓
Orchestrator
   ↓
Intent Agent
   ↓
APPLY_LEAVE
   ↓
Parameter Agent
   ↓
Extract:
  Casual Leave
  2026-09-10
  2026-09-12
  Personal work
   ↓
Action Agent
   ↓
Leave Request
   ↓
Response Agent
   ↓
Confirmation
   ↓
Streamlit
```

---

# Complete Architecture Flow

```text
                    ┌─────────────────┐
                    │     Employee    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Streamlit UI   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Orchestrator   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Intent Agent   │
                    └────────┬────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
          ▼                  ▼                  ▼
    ┌───────────┐     ┌────────────┐     ┌────────────┐
    │  Policy   │     │ Employee   │     │  Action    │
    │   Agent   │     │   Agent    │     │   Agent    │
    └─────┬─────┘     └─────┬──────┘     └─────┬──────┘
          │                  │                  │
          ▼                  ▼                  ▼
    ┌───────────┐      ┌───────────┐      ┌───────────┐
    │    RAG    │      │ Employee  │      │  Leave /  │
    │   FAISS   │      │   Data    │      │  Actions  │
    └─────┬─────┘      └───────────┘      └───────────┘
          │
          ▼
    ┌─────────────┐
    │ Policy PDFs │
    └─────────────┘

          All routes
               │
               ▼
      ┌─────────────────┐
      │ Response Agent  │
      └────────┬────────┘
               │
               ▼
      ┌─────────────────┐
      │ Employee Answer │
      └─────────────────┘
               │
               ▼
        ┌────────────┐
        │ Streamlit  │
        │     UI     │
        └────────────┘
```

---

# Advantages

* Conversational employee experience
* Centralized access to company information
* Modular architecture
* Clear separation of agent responsibilities
* Local RAG capability
* Fast vector retrieval
* FAISS-based similarity search
* Cached embedding model
* Policy-grounded responses
* Employee-specific information
* Automated testing
* Easy-to-use Streamlit interface
* Reduced dependency on external APIs for retrieval

---

# ⚠️ Limitations

Current limitations include:

* The assistant supports a predefined set of intents.
* Policy answers depend on the quality of retrieved document chunks.
* The local embedding model is optimized for retrieval rather than generation.
* External/local LLM configuration may affect response generation for certain dynamic responses.
* Leave parameter extraction currently supports specific date formats.
* The current system is designed primarily for internal/demo usage rather than large-scale production deployment.
* Long-term memory behavior depends on the currently enabled implementation.

---

# 🚀 Future Enhancements

Potential future improvements include:

### 1. Better Intent Classification

Use a trained classifier or LLM-based classification with fallback logic.

### 2. Advanced RAG

Implement:

* Hybrid search
* BM25 + vector search
* Cross-encoder reranking
* Query expansion
* Better chunking strategies

### 3. More Employee Actions

Add:

* Expense submission
* IT support tickets
* Attendance requests
* Onboarding tasks
* HR requests

### 4. Authentication

Integrate enterprise authentication such as:

* SSO
* OAuth
* Active Directory

### 5. Production Database

Replace demo/static employee data with an enterprise database.

### 6. Advanced Memory

Implement:

* Conversation summaries
* User preferences
* Context-aware follow-ups
* Persistent conversation history

### 7. Better UI

Add:

* Policy document viewer
* Search
* Sidebar navigation
* Employee dashboard
* Leave calendar
* Asset dashboard

### 8. Monitoring

Add:

* Logging
* Latency monitoring
* Retrieval evaluation
* Error monitoring
* Usage analytics

---

# 📊 Project Evaluation Points

The project demonstrates knowledge of:

```text
Python
│
├── Modular application design
├── Agent architecture
├── Natural Language Processing
├── Embeddings
├── Vector Search
├── RAG
├── FAISS
├── LLM integration
├── Prompt engineering
├── Streamlit
├── SQLite / memory
├── API/tool integration
├── Error handling
├── Automated testing
└── Git/GitHub
```

---

#  Capstone Learning Outcomes

Through this project, the team gained practical experience in:

* Designing an AI application architecture
* Building multi-agent workflows
* Implementing RAG from PDF documents
* Creating embeddings
* Building and querying FAISS indexes
* Optimizing model loading
* Handling LLM/API limitations
* Implementing conversational interfaces
* Processing natural-language actions
* Writing automated tests
* Debugging Python applications
* Managing Git branches and merge conflicts
* Building an end-to-end AI application

---

# 🏁 Conclusion

The **TechNova AI Office Assistant** demonstrates how AI, RAG, vector search, agent-based architecture, business logic, memory, and a conversational UI can be combined to create a practical internal employee assistant.

The system separates responsibilities across different components:

```text
Streamlit
    ↓
Orchestrator
    ↓
Intent Classification
    ↓
Specialized Agents
    ↓
RAG / Employee Data / Actions
    ↓
Response Generation
    ↓
Employee
```

The use of a **local embedding model and FAISS** provides an efficient and independent policy retrieval layer, while the modular agent architecture makes the system easier to test, maintain, and extend.

The project provides a strong foundation for a production-ready enterprise AI assistant and can be extended with authentication, enterprise databases, advanced RAG, richer actions, improved memory, and monitoring.

---

##  Project

**Project:** TechNova AI Office Assistant
**Type:** AI / RAG / Multi-Agent Capstone Project
**Interface:** Streamlit
**Language:** Python
**Vector Search:** FAISS
**Embedding Model:** `all-MiniLM-L6-v2`
**Testing:** Pytest
**Version Control:** Git / GitHub
