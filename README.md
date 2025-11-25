# 🚀 CONTEXIA – AI-Powered Multi-Platform Content Generation System

[![Next.js](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org/)
[![Django](https://img.shields.io/badge/Django-5.0-green)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://www.python.org/)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL%20%2B%20pgvector-brightgreen)](https://supabase.com/)
[![Celery](https://img.shields.io/badge/Celery-5.3-37814A)](https://docs.celeryq.dev/)
[![Redis](https://img.shields.io/badge/Redis-Cache%2FQueue-red)](https://redis.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

CONTEXIA is an **AI-powered, multi-platform content generation system** that transforms a single source (PDFs, documents, URLs, or raw text) into **platform-optimized content** for LinkedIn, X/Twitter, YouTube, blogs, and more. It combines **RAG (Retrieval-Augmented Generation)**, **multi-agent AI**, and **async processing** to deliver fast, on-brand, and trend-aware content at scale, backed by **Supabase (PostgreSQL + pgvector)** for storage and semantic search.

---

## 🎥 Project Walkthrough (YouTube)

> 🔗 **Watch the full project explanation here:**  
> https://youtu.be/yr-pU17GC5I

---

## 📌 A. Problem Statement

### The Challenge

Content creators, marketers, and social media managers face:

1. **Time-Consuming Multi-Platform Publishing**  
   Adapting one piece of content into platform-specific formats takes hours.

2. **Inconsistent Brand Voice**  
   Hard to maintain consistent tone while respecting each platform’s style and constraints.

3. **Trend Integration Difficulty**  
   Manually finding and incorporating relevant trends is slow and often outdated.

4. **Image Optimization Complexity**  
   Each platform demands different aspect ratios, styles, and layouts.

5. **Scalability Limits**  
   As content volume grows, manual workflows become a bottleneck.

### Target Users

- Digital marketers & agencies  
- Solo content creators & influencers  
- Social media managers (multi-account)  
- Small businesses & startups  
- Personal brands wanting to scale presence

---

## 📌 B. Solution Overview

### Our AI-Powered Approach

**CONTEXIA** takes any input content and produces **platform-optimized, trend-aware content** with minimal human effort.

High-level pipeline:

```text
Input Content → Document Processing → RAG-Enhanced AI Agents
→ Platform-Specific Content → Optional Image Generation → Publishing/Export
````

### Core Innovation: Multi-Agent + RAG

1. **Intelligent Document Extraction Engine**

   * Extracts text from **PDF, DOCX, PPTX, TXT**
   * Web scraping for URLs with readability-based content extraction
   * Topic detection and semantic analysis

2. **RAG-Powered Trend Integration**

   * Trend scraping (e.g., via DuckDuckGo or similar sources)
   * Embedding + **pgvector**-powered semantic search (hosted on Supabase PostgreSQL)
   * Injects relevant, up-to-date trends into prompts

3. **Multi-Agent Content Generation System**

   * Dedicated AI agents for:

     * LinkedIn
     * X/Twitter
     * YouTube scripts
     * Blog articles
     * Email / long-form variants
   * Each agent encodes:

     * Platform constraints (length, tone, structure)
     * Engagement patterns & formatting best practices
   * Brand voice personalization from user profile / settings

4. **AI Image Generation & Processing**

   * Multi-provider support:

     * Nano Banana / Google Imagen
     * Fal.ai
     * Freepik API
   * 8 design themes:

     * Minimal, Bold, Gradient, Vintage, Neon, Corporate, Organic, Tech
   * Auto-resizing & optimization for each platform

5. **Async Task Processing**

   * **Celery + Redis** handle long-running jobs
   * Content generation, trend retrieval, and image generation run asynchronously
   * Frontend polls for task status to provide real-time feedback

### Expected Impact

* ⏱ **Up to 90% time saved** for multi-platform adaptation
* 📈 **3–5x better engagement** vs generic cross-posting
* 🧠 Consistent brand voice across platforms
* 📦 Scales to **100+ content pieces/day** with minimal supervision
* 🔍 Auto-integrates trends to boost discoverability

---

## 📌 C. System Architecture

### High-Level Architecture

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND (Next.js 14)                        │
│  Upload UI  •  Generation Dashboard  •  Preview Editor  • Publishing   │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │  REST API (HTTPS)
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                  BACKEND (Django 5 + Django REST Framework)            │
│   API Gateway: file upload, generation, status, publishing endpoints   │
│   ├─ ingest/      – document & web content processing                  │
│   ├─ generator/   – multi-agent AI + LLM wrappers                      │
│   ├─ trends/      – RAG + trend scraping + vector store                │
│   ├─ media/       – image generation pipeline                          │
│   └─ social/      – social account & publishing integration            │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                 TASK QUEUE (Celery + Redis)                            │
│   • Content generation tasks                                           │
│   • Image generation tasks                                             │
│   • Trend retrieval & enrichment tasks                                 │
│   • Social publishing tasks                                            │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      DATA PERSISTENCE LAYER                            │
│   Supabase (PostgreSQL + pgvector)                                     │
│   • Users • Content Records • Trend Vectors • Social Accounts          │
│   Redis                                                                │
│   • Task Queue • Caching • Real-time state                             │
└─────────────────────────────────────────────────────────────────────────┘

External Services: OpenAI, Google Gemini, Trend sources, Image APIs
```

---

## 📌 D. Tech Stack

### Frontend

| Technology        | Purpose                         |
| ----------------- | ------------------------------- |
| **Next.js 14**    | React framework with App Router |
| **React 18**      | UI components                   |
| **TypeScript 5**  | Type safety                     |
| **Tailwind CSS**  | Utility-first styling           |
| **shadcn/ui**     | Reusable UI components          |
| **Framer Motion** | Animations & transitions        |
| **Axios**         | HTTP client                     |
| **Sonner**        | Toast notifications             |

### Backend

| Technology                           | Purpose                       |
| ------------------------------------ | ----------------------------- |
| **Django 5**                         | Web framework                 |
| **Django REST Framework**            | REST API                      |
| **Python 3.10+**                     | Backend language              |
| **Supabase (PostgreSQL + pgvector)** | Primary database + vectors    |
| **Redis**                            | Caching & Celery broker       |
| **Celery 5.3+**                      | Async task queue              |
| **django-celery-beat**               | Periodic tasks (optional)     |
| **django-cors-headers**              | CORS support                  |
| **Gunicorn / uvicorn+daphne**        | Production serving (optional) |

### AI & ML

| Technology                | Purpose                            |
| ------------------------- | ---------------------------------- |
| **OpenAI API**            | Primary LLM for text generation    |
| **Google Gemini API**     | Alternative / fallback LLM         |
| **Nano Banana / Imagen**  | Image generation (primary)         |
| **Fal.ai, Freepik API**   | Image generation fallbacks         |
| **pgvector via Supabase** | Semantic search for trends/content |

### Document Processing

| Library              | Purpose                   |
| -------------------- | ------------------------- |
| **pypdf**            | PDF extraction            |
| **python-docx**      | DOCX extraction           |
| **BeautifulSoup4**   | HTML parsing & scraping   |
| **readability-lxml** | Article content isolation |
| **Pillow (PIL)**     | Image handling            |

---

## 📌 E. Getting Started

### 1️⃣ Prerequisites

Make sure you have installed:

* **Node.js** v18+
* **Python** 3.10+
* **Supabase** account (managed PostgreSQL with `pgvector`)
* **Redis** (local or remote)
* **Git**

> You can still run with local PostgreSQL for development, but this project is designed to work seamlessly with **Supabase** as the main database provider.

---

### 2️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/CONTEXIA_AI.git
cd CONTEXIA_AI
```

(Adjust the URL to your actual repository.)

---

### 3️⃣ Backend Setup (Django + Celery)

#### 3.1 Navigate to Backend

```bash
cd backend
```

#### 3.2 Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

#### 3.3 Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 3.4 Configure Supabase (PostgreSQL + pgvector)

1. Create a project in **Supabase**.

2. Go to **SQL Editor** in Supabase and enable `pgvector`:

   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

3. Get your Supabase **database connection string** from
   `Project Settings → Database → Connection Info`.

   Example:

   ```text
   postgresql://postgres:YOUR_PASSWORD@YOUR_PROJECT_HOST.supabase.co:5432/postgres
   ```

   or using the pooled connection:

   ```text
   postgresql://postgres:YOUR_PASSWORD@YOUR_PROJECT_HOST.supabase.co:6543/postgres?sslmode=require
   ```

4. In `backend/.env`, configure:

```env
# Django
SECRET_KEY=your-super-secret-django-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Supabase Database (recommended)
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@YOUR_PROJECT_HOST.supabase.co:6543/postgres?sslmode=require

# If using separate DB_* vars in settings:
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=YOUR_PASSWORD
DB_HOST=YOUR_PROJECT_HOST.supabase.co
DB_PORT=6543

# AI Provider
AI_PROVIDER=openai        # or "gemini"
OPENAI_API_KEY=your-openai-api-key
GOOGLE_API_KEY=your-gemini-api-key

# Image APIs (optional but recommended)
NANO_BANANA_API_KEY=your-nano-banana-api-key
FAL_API_KEY=your-fal-api-key
FREEPIK_API_KEY=your-freepik-api-key

# Redis / Celery
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=django-db

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Auth / Integration
NEXTAUTH_SECRET=your-nextauth-secret   # must match frontend
```

> 🔐 **Important:** Never commit `.env` files — they must be in `.gitignore`.

#### 3.5 Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

#### 3.6 Create Superuser

```bash
python manage.py createsuperuser
```

#### 3.7 Start Django Server

```bash
python manage.py runserver
```

Backend now runs at: **[http://localhost:8000](http://localhost:8000)**

---

### 4️⃣ Redis & Celery

#### 4.1 Start Redis

```bash
# Windows (WSL)
wsl
redis-server

# macOS (Homebrew)
brew services start redis

# Linux
sudo service redis-server start
```

#### 4.2 Start Celery Worker

From `backend/` with venv activated:

```bash
# Windows
celery -A project worker --loglevel=info --pool=solo

# macOS / Linux
celery -A project worker --loglevel=info
```

(Keep this terminal open.)

---

### 5️⃣ Frontend Setup (Next.js)

#### 5.1 Navigate to Frontend

From the project root:

```bash
cd frontend
```

#### 5.2 Install Dependencies

```bash
npm install
```

#### 5.3 Create `.env.local`

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000

NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-nextauth-secret   # must match backend

# Optional social OAuth keys (if direct posting is enabled)
LINKEDIN_CLIENT_ID=
LINKEDIN_CLIENT_SECRET=
TWITTER_CLIENT_ID=
TWITTER_CLIENT_SECRET=

# Optional Supabase usage in frontend (if needed)
NEXT_PUBLIC_SUPABASE_URL=https://YOUR_PROJECT_HOST.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
```

#### 5.4 Start Frontend Dev Server

```bash
npm run dev
```

Frontend runs at: **[http://localhost:3000](http://localhost:3000)**

---

## 🎮 F. Running the Full System

You’ll typically have **4 terminals**:

1. **Redis**

   ```bash
   redis-server
   ```
2. **Celery Worker**

   ```bash
   cd backend
   venv\Scripts\activate  # or source venv/bin/activate
   celery -A project worker --loglevel=info --pool=solo
   ```
3. **Django Backend**

   ```bash
   cd backend
   venv\Scripts\activate
   python manage.py runserver
   ```
4. **Next.js Frontend**

   ```bash
   cd frontend
   npm run dev
   ```

Then go to **[http://localhost:3000](http://localhost:3000)** in your browser.

---

## 📌 G. Usage Guide

### 1. First-Time Login

1. Visit `http://localhost:3000`
2. Register a new account or log in using the Django superuser (if integrated)
3. After login, you’ll be redirected to the **dashboard**

### 2. Content Lab Workflow

1. Navigate to **Content Lab** from the sidebar.
2. Choose input method:

   * Upload a file (PDF, DOCX, PPTX, TXT), or
   * Paste raw text, or
   * Provide a URL (if enabled)
3. Click **“Generate Content for All Platforms”**.
4. The backend:

   * Extracts + cleans content
   * Runs topic detection
   * Retrieves relevant trends via RAG (Supabase + pgvector)
   * Orchestrates multi-agent generation (LinkedIn/X/YouTube/Blog)
5. The frontend polls the task until status is **completed**.
6. Review content per platform using tabs:

   * **LinkedIn**: Long-form, professional post + hashtags
   * **X/Twitter**: Thread format, concise hooks
   * **YouTube**: Script + description ideas
   * **Blog**: SEO-ready long-form article

### 3. Image Generation (Optional)

* If enabled and configured, CONTEXIA:

  * Calls image providers with design theme prompts
  * Auto-optimizes images for the chosen platform
* Images can be previewed and downloaded or attached to posts.

### 4. Publishing

* Direct publishing to LinkedIn / X / others requires:

  * OAuth setup (client ID/secret)
  * Linking accounts through the UI
* Alternatively:

  * Use **Copy** buttons to copy content
  * Manually paste into your target platform

---

## 📁 H. Project Structure

```text
CONTEXIA_AI/
├── backend/
│   ├── apps/
│   │   ├── api/            # REST API endpoints
│   │   ├── generator/      # LLM wrappers, multi-agent logic, Celery tasks
│   │   ├── ingest/         # File & web content ingestion
│   │   ├── trends/         # Trend scraping + vectorstore (pgvector on Supabase)
│   │   ├── social/         # Social auth & posting (optional)
│   │   └── media/          # Image generation & processing
│   ├── project/            # Django project (settings, urls, celery, etc.)
│   ├── manage.py
│   └── requirements.txt
│
├── frontend/
│   ├── app/                # Next.js App Router
│   │   ├── dashboard/      # Protected dashboard routes
│   │   │   └── content/    # Content Lab UI
│   │   ├── login/          # Auth pages
│   │   └── register/
│   ├── components/         # Shared UI components
│   ├── lib/                # API client, auth helpers
│   ├── public/             # Static assets
│   └── package.json
│
├── docker-compose.yml      # Optional containerized setup
├── .gitignore
└── README.md
```

---

## 🧩 I. Configuration & Tuning

### AI Provider Selection

In `backend/.env`:

```env
AI_PROVIDER=openai   # or "gemini"
OPENAI_API_KEY=...
GOOGLE_API_KEY=...
```

### Performance

* **Batching & parallelization** handled in generator tasks
* You can tune:

  * Max content length
  * Number of fetched trends
  * Polling interval on frontend (default ~1s)

---

## 🐛 J. Troubleshooting

### Common Backend Issues

**1. ModuleNotFoundError**

```bash
cd backend
# Ensure venv active
pip install -r requirements.txt
```

**2. Database Errors**

* Ensure Supabase credentials are correct
* Check `DATABASE_URL` in `.env`
* Confirm `vector` extension is enabled in Supabase SQL Editor

**3. Celery / Redis Issues**

* Ensure Redis is running:

  ```bash
  redis-cli ping   # should return PONG
  ```

* Check Celery logs (terminal where worker runs)

---

### Common Frontend Issues

**1. Port 3000 in Use**

```bash
npm run dev -- -p 3001
```

**2. Stale Build**

```bash
rm -rf .next
npm run dev
```

**3. NEXTAUTH / Auth Issues**

* Ensure `NEXTAUTH_URL` and `NEXTAUTH_SECRET` are set both in frontend and backend (if shared)
* Backend must be reachable at `NEXT_PUBLIC_API_URL`

---

## 🤝 K. Contributing

Contributions are welcome!

1. Fork the repo
2. Create a feature branch:

   ```bash
   git checkout -b feature/amazing-feature
   ```
3. Commit your changes:

   ```bash
   git commit -m "Add amazing feature"
   ```
4. Push to your branch:

   ```bash
   git push origin feature/amazing-feature
   ```
5. Open a Pull Request

---

## 📄 L. License

This project is licensed under the **MIT License**.
See the [`LICENSE`](LICENSE) file for details.

---

## 📧 M. Support

* 🐛 Issues: open a GitHub issue in this repository
* 📩 Email: **[pranaychandra751@gmail.com](mailto:pranaychandra751@gmail.com)**

---

<div align="center">
  <p>Made with ❤️ by the CONTEXIA Team</p>
  <p>⭐ Star this repo if you find it helpful!</p>
</div>
```
