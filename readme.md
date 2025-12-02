# 📧 Constructure AI – Gmail AI Assistant

Constructure AI is an intelligent email assistant that connects to Gmail via Google OAuth, fetches your recent emails, summarizes them using AI, and allows conversational commands such as:
- **"Show my last 5 emails"**
- **"Give me today's email digest"**
- **"Delete last email"**
- **"Delete email 2"**

It uses **FastAPI** backend + **Next.js** frontend + **Gemini AI** for natural language understanding and summarization.

---

## 🚀 Live Demo
🔗 **Live App:** https://your-app-name.vercel.app  
(Currently requires dev tester access via Google OAuth)

---

## 🧠 Tech Stack & Libraries

| Layer | Technology |
|--------|-------------|
| Frontend | Next.js 14 (App Router), TypeScript, TailwindCSS |
| Backend | FastAPI, Python 3.11, Uvicorn |
| OAuth | Google OAuth 2.0 (People API, Gmail API) |
| AI Provider | Gemini (Google Generative AI) |
| Other Libraries | google-auth, google-auth-oauthlib, googleapis, axios, pydantic, jwt |

---

## 📦 Features
- Google OAuth login with Gmail permissions
- Fetch latest messages from Gmail via API
- AI-powered email summarization
- Chat-like UI for asking questions about inbox
- Delete specific emails using voice-like commands
- JWT-based session authentication

---

## 🛠 Setup Instructions

### 1️⃣ Clone Repository
```bash
git clone https://github.com/ankit03ak/constructure-ai
cd constructure-ai

cd backend
python -m venv venv
source venv/bin/activate 
pip install -r requirements.txt


uvicorn app.main:app --reload --host 0.0.0.0 --port 8080


cd frontend
npm install
npm run dev


APP_ENV=local
APP_HOST=0.0.0.0
APP_PORT=8080

CORS_ORIGINS=http://localhost:3000

SESSION_SECRET_KEY=your-secret-key

GOOGLE_CLIENT_ID=xxxxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxxxx
GOOGLE_REDIRECT_URI=http://localhost:8080/auth/google/callback
GOOGLE_OAUTH_SCOPES=https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/gmail.send https://www.googleapis.com/auth/gmail.modify https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email openid

GEMINI_API_KEY=your-gemini-api-key
FRONTEND_URL=http://localhost:3000

## Frontend env

NEXT_PUBLIC_BACKEND_URL=http://localhost:8080
NEXT_PUBLIC_GOOGLE_CLIENT_ID=xxxxx.apps.googleusercontent.com

