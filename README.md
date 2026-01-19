# AI First CRM --- HCP Interaction Module (Task 1)

## 📌 Project Overview

This project was built as part of **Task 1** to create an AI‑first CRM
module for logging interactions with healthcare professionals (HCPs).

The system supports: - Structured form-based interaction logging -
Conversational (chat-based) interaction logging - AI-based extraction of
doctor names using LangGraph - Automatic meeting summary generation -
Viewing stored interactions

The project consists of: - **Frontend:** React\
- **Backend:** FastAPI\
- **AI Workflow:** LangGraph\
- **Communication:** REST APIs via Axios

------------------------------------------------------------------------

## 📁 Project Structure

    AI-CRM-HCP/
    │
    ├── frontend/
    │   ├── src/
    │   │   ├── App.js
    │   │   ├── index.js
    │   │   └── index.css
    │   └── package.json
    │
    ├── backend/
    │   ├── main.py
    │   └── requirements.txt
    │
    └── README.md

------------------------------------------------------------------------

## 🚀 How to Run the Project

### 1️⃣ Run Backend (FastAPI)

``` bash
cd backend
pip install fastapi uvicorn langgraph pydantic
python -m uvicorn main:app --reload
```

Backend runs at: **http://127.0.0.1:8000**\
API docs available at: **http://127.0.0.1:8000/docs**

------------------------------------------------------------------------

### 2️⃣ Run Frontend (React)

``` bash
cd frontend
npm install
npm start
```

Frontend runs at: **http://localhost:3000**

------------------------------------------------------------------------

## 🔌 API Endpoints

### Log interaction (structured form)

**POST** `/log_interaction`

Example:

``` json
{
  "hcp_name": "Dr. Rahul",
  "notes": "Met Dr. Rahul about diabetes treatment"
}
```

### Log interaction (chat)

**POST** `/chat_log`

Example:

``` json
{
  "text": "Met Dr. Priya today"
}
```

### Get all interactions

**GET** `/interactions`

------------------------------------------------------------------------

## 🧠 AI Component (LangGraph)

The backend uses LangGraph to: 1. Extract doctor name from free text\
2. Generate a short meeting summary\
3. Store structured records

------------------------------------------------------------------------

## ✅ Features Completed in Task 1

-   Structured form entry\
-   Conversational chat entry\
-   AI-based doctor name extraction\
-   Auto summary generation\
-   Frontend--backend integration\
-   Viewing saved interactions

------------------------------------------------------------------------

## 👤 Author

**Poorva Kumari** Task 1 Submission --- AI First CRM
