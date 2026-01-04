# Lexi — Language Learning Backend

Backend service for **Lexi**, a smart language learning application that helps users build vocabulary using AI-assisted processing and spaced repetition.

## 🚀 Tech Stack
- FastAPI
- Firebase Authentication (Google)
- PostgreSQL
- SQLAlchemy
- Alembic
- JWT
- Pydantic

## 🔐 Authentication Flow
1. Client authenticates via Google using Firebase
2. Firebase returns an ID Token
3. Client sends the ID Token to the backend
4. Backend verifies the token via Firebase Admin SDK
5. Backend issues its own JWT for protected endpoints

## ⚙️ Setup

### 1. Clone repository
```bash
git clone https://github.com/your-username/lexi-backend.git
cd lexi-backend
```
### 2. Create virtual environment
```bash
python -m venv .venv
source .venv/binactivate
```
### 3. Install dependencies
```bash
pip install -r requirements.txt
```
### 4. Environment variables
```bash
cp .env.example .env
```
Fill in required values inside .env.

### 5. Run database migrations
```bash
alembic upgrade head
```
### 6. Start development server
```bash
uvicorn app.main:app --reload
```
Server will be available at:
```
http://127.0.0.1:8000
```
Swagger UI:

```http://127.0.0.1:8000/docs```

### 📡 API Overview
## Auth
- ```POST /auth/google``` — Google login via Firebase

## Users
- ```GET /users/me``` — Get current authenticated user

### 🧠 Roadmap
- Vocabulary processing via OCR

- AI-powered translation and categorization

- Spaced repetition learning system

- Progress analytics and insights
