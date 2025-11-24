<<<<<<< HEAD
# 🚀 CONTEXIA - AI-Powered Multi-Platform Content Generation System

[![Next.js](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org/)
[![Django](https://img.shields.io/badge/Django-5.0-green)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://www.python.org/)
[![Celery](https://img.shields.io/badge/Celery-5.3-37814A)](https://docs.celeryq.dev/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📌 A. Problem Statement

### The Challenge
Content creators and marketers face several critical challenges:

1. **Time-Consuming Multi-Platform Publishing**: Creating platform-specific content (LinkedIn posts, Twitter threads, YouTube scripts, blog articles) from a single source takes hours of manual adaptation.

2. **Inconsistent Brand Voice**: Maintaining consistent messaging across different platforms while adapting to each platform's unique requirements and audience expectations.

3. **Trend Integration Difficulty**: Manually researching and incorporating trending topics relevant to the content is labor-intensive and often outdated by the time content is published.

4. **Image Optimization Complexity**: Each platform has different image requirements, aspect ratios, and design aesthetics that require specialized tools and expertise.

5. **Scalability Issues**: As content volume grows, manual content adaptation becomes a bottleneck, limiting publishing frequency and reach.

### Target Users
- **Digital Marketers**: Need to maintain active presence across multiple platforms
- **Content Creators**: Require efficient content repurposing workflows
- **Social Media Managers**: Must handle multiple client accounts with consistent quality
- **Small Businesses**: Lack resources for dedicated platform-specific content creation
- **Personal Brands**: Want to maximize reach without hiring large teams

---

## 📌 B. Solution Overview

### Our AI-Powered Approach

**CONTEXIA** is an intelligent, end-to-end content generation platform that transforms any input (PDFs, documents, URLs, or text) into platform-optimized social media content using advanced AI agents and RAG (Retrieval-Augmented Generation).

#### Core Innovation: Multi-Agent AI System

```
Input Content → Document Processing → RAG-Enhanced AI Agents → Platform-Specific Content → Multi-Platform Publishing
```

**Key Components:**

1. **Intelligent Document Extraction Engine**
   - Extracts text from PDFs, DOCX, PPTX files
   - Web scraping with readability algorithms for URL content
   - Topic detection using AI semantic analysis

2. **RAG-Powered Trend Integration**
   - Real-time trend scraping from DuckDuckGo
   - Vector embeddings (pgvector) for semantic similarity matching
   - Automatic integration of relevant trending topics into generated content

3. **Multi-Agent Content Generation System**
   - Specialized AI agents for each platform (LinkedIn, Twitter, YouTube, Blog, Email)
   - Each agent understands platform-specific best practices, character limits, and engagement patterns
   - Brand voice personalization for consistent messaging

4. **AI Image Generation & Processing**
   - Multiple provider support (Nano Banana/Google Imagen, Fal.ai, Freepik)
   - 8 theme-based design systems (minimal, bold, gradient, vintage, neon, etc.)
   - Automatic image optimization for each platform's requirements

5. **Async Task Processing**
   - Celery + Redis for non-blocking content generation
   - Real-time progress tracking with WebSocket-style polling
   - Handles concurrent requests efficiently

### Expected Impact

- **90% Time Reduction**: Generate 5+ platform-specific posts in minutes vs. hours
- **Improved Engagement**: Platform-optimized content performs 3-5x better than generic cross-posts
- **Consistency**: Brand voice maintained across all platforms automatically
- **Scalability**: Handle 100+ content pieces per day with minimal human oversight
- **Trend Relevance**: Content automatically incorporates latest trends, increasing discoverability

### Value Proposition

- **For Marketers**: Free up 15-20 hours/week for strategy instead of content adaptation
- **For Creators**: Expand reach to 5+ platforms without proportional time investment
- **For Businesses**: Professional multi-platform presence without hiring specialized staff
- **For Agencies**: Scale client work 5x with same team size

---

## 📌 C. Architecture Diagram

### System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND LAYER (Next.js 14)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐│
│  │   Upload UI  │  │  Generation  │  │   Preview    │  │  Publishing ││
│  │   (Drag &    │→ │   Dashboard  │→ │   Editor     │→ │   Manager   ││
│  │    Drop)     │  │  (Real-time) │  │ (Platform-   │  │  (Schedule) ││
│  └──────────────┘  └──────────────┘  └──────────────┘  └─────────────┘│
└───────────────────────────────────┬─────────────────────────────────────┘
                                    │ HTTP/REST API
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      BACKEND LAYER (Django 5.0 + DRF)                   │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                       API Gateway (views.py)                      │  │
│  │  • File Upload Endpoints    • Content Generation Endpoints       │  │
│  │  • Task Status Polling      • Social Media Publishing            │  │
│  └────────────────────────────────┬─────────────────────────────────┘  │
│                                   │                                     │
│  ┌────────────────────────────────▼─────────────────────────────────┐  │
│  │              DOCUMENT PROCESSING MODULE (ingest/)                │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │  │
│  │  │   PDF    │  │   DOCX   │  │   PPTX   │  │   Web Scraper    │ │  │
│  │  │ Extractor│  │ Extractor│  │ Extractor│  │ (BeautifulSoup)  │ │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘ │  │
│  └────────────────────────────────┬─────────────────────────────────┘  │
│                                   │                                     │
│  ┌────────────────────────────────▼─────────────────────────────────┐  │
│  │              AI PROCESSING LAYER (generator/)                    │  │
│  │                                                                   │  │
│  │  ┌─────────────────────────────────────────────────────────────┐ │  │
│  │  │         MULTI-AGENT AI SYSTEM (ai_wrapper.py)              │ │  │
│  │  │                                                             │ │  │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │ │  │
│  │  │  │  LinkedIn   │  │   Twitter   │  │   YouTube   │       │ │  │
│  │  │  │    Agent    │  │    Agent    │  │    Agent    │  ...  │ │  │
│  │  │  └─────────────┘  └─────────────┘  └─────────────┘       │ │  │
│  │  │         │                 │                 │              │ │  │
│  │  │         └─────────────────┴─────────────────┘              │ │  │
│  │  │                          │                                 │ │  │
│  │  │                ┌─────────▼─────────┐                      │ │  │
│  │  │                │  OpenAI / Gemini  │                      │ │  │
│  │  │                │   LLM Backend     │                      │ │  │
│  │  │                └───────────────────┘                      │ │  │
│  │  └─────────────────────────────────────────────────────────────┘ │  │
│  └────────────────────────────────┬─────────────────────────────────┘  │
│                                   │                                     │
│  ┌────────────────────────────────▼─────────────────────────────────┐  │
│  │         RAG SYSTEM (trends/ + vectorstore.py)                    │  │
│  │                                                                   │  │
│  │  ┌───────────────┐    ┌──────────────────┐   ┌───────────────┐ │  │
│  │  │ DuckDuckGo    │───▶│  Embedding Gen   │──▶│  PostgreSQL   │ │  │
│  │  │ Trend Scraper │    │ (AI Embeddings)  │   │  + pgvector   │ │  │
│  │  └───────────────┘    └──────────────────┘   └───────────────┘ │  │
│  │                                │                      │          │  │
│  │                         ┌──────▼──────────────────────▼────┐    │  │
│  │                         │  Semantic Similarity Search      │    │  │
│  │                         │  (Top-K Relevant Trends)         │    │  │
│  │                         └──────────────────────────────────┘    │  │
│  └────────────────────────────────┬─────────────────────────────────┘  │
│                                   │                                     │
│  ┌────────────────────────────────▼─────────────────────────────────┐  │
│  │           IMAGE GENERATION & PROCESSING (media/)                 │  │
│  │                                                                   │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │  │
│  │  │ Nano Banana  │  │   Fal.ai     │  │   Freepik API        │  │  │
│  │  │ (Google AI)  │→ │  (Fallback)  │→ │   (Fallback 2)       │  │  │
│  │  └──────────────┘  └──────────────┘  └──────────────────────┘  │  │
│  │          │                                                       │  │
│  │          ▼                                                       │  │
│  │  ┌────────────────────────────────────────────────────────────┐ │  │
│  │  │  AI Design System (8 Themes)                              │ │  │
│  │  │  • Minimal  • Bold  • Gradient  • Vintage                 │ │  │
│  │  │  • Neon  • Corporate  • Organic  • Tech                   │ │  │
│  │  └────────────────────────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    TASK QUEUE LAYER (Celery + Redis)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐│
│  │   Content    │  │    Image     │  │   Trend      │  │   Social    ││
│  │  Generation  │  │  Generation  │  │   Scraping   │  │  Publishing ││
│  │    Tasks     │  │    Tasks     │  │    Tasks     │  │    Tasks    ││
│  └──────────────┘  └──────────────┘  └──────────────┘  └─────────────┘│
└───────────────────────────────────┬─────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      DATA PERSISTENCE LAYER                             │
│  ┌────────────────────────────┐  ┌──────────────────────────────────┐  │
│  │   PostgreSQL Database      │  │      Redis Cache & Queue         │  │
│  │  • User Data               │  │  • Task Queue (Celery)           │  │
│  │  • Content Records         │  │  • Session Management            │  │
│  │  • Trend Vectors (pgvector)│  │  • Real-time State               │  │
│  │  • Social Accounts         │  │  • Rate Limiting                 │  │
│  └────────────────────────────┘  └──────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘

                                    ┌─────────────────────┐
                                    │  External Services  │
                                    │  • OpenAI API       │
                                    │  • Google Gemini    │
                                    │  • DuckDuckGo       │
                                    │  • Image APIs       │
                                    └─────────────────────┘
```

### Agent Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       CONTENT GENERATION WORKFLOW                       │
└─────────────────────────────────────────────────────────────────────────┘

    User Input (PDF/DOCX/Text/URL)
              │
              ▼
    ┌─────────────────────┐
    │  Document Processor │
    │  • Extract Text     │
    │  • Detect Topic     │
    │  • Clean Content    │
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────────────┐
    │   Topic Analysis    │
    │  (AI Embeddings)    │
    └──────────┬──────────┘
               │
               ├──────────────────────────────┐
               │                              │
               ▼                              ▼
    ┌─────────────────────┐      ┌─────────────────────┐
    │  Trend Retrieval    │      │   Brand Voice       │
    │  (RAG System)       │      │   Retrieval         │
    │  • Vector Search    │      │   (User Profile)    │
    │  • Top-K Trends     │      └──────────┬──────────┘
    └──────────┬──────────┘                 │
               │                            │
               └────────────┬───────────────┘
                            │
                            ▼
              ┌─────────────────────────────┐
              │   Content Context Builder   │
              │   • Input Text              │
              │   • Relevant Trends         │
              │   • Brand Voice Rules       │
              └─────────────┬───────────────┘
                            │
                            ▼
         ┌──────────────────────────────────────────┐
         │      MULTI-AGENT AI ORCHESTRATION        │
         └──────────────────────────────────────────┘
                            │
         ┌──────────────────┼──────────────────┐
         │                  │                  │
         ▼                  ▼                  ▼
    ┌─────────┐        ┌─────────┐      ┌─────────┐
    │LinkedIn │        │ Twitter │      │ YouTube │  ...
    │  Agent  │        │  Agent  │      │  Agent  │
    └────┬────┘        └────┬────┘      └────┬────┘
         │                  │                 │
         │ Prompts:         │ Prompts:        │ Prompts:
         │ • Tone: Pro      │ • Tone: Casual  │ • Tone: Engaging
         │ • Length: 1300   │ • Length: 280   │ • Length: Script
         │ • Hashtags: Yes  │ • Thread: Yes   │ • Timestamps: Yes
         │                  │                 │
         └─────────┬────────┴─────────┬───────┘
                   │                  │
                   ▼                  ▼
         ┌──────────────────┐  ┌──────────────────┐
         │   OpenAI GPT-4   │  │  Google Gemini   │
         │   (Primary LLM)  │  │  (Fallback LLM)  │
         └─────────┬────────┘  └─────────┬────────┘
                   │                     │
                   └──────────┬──────────┘
                              │
                              ▼
                  ┌───────────────────────┐
                  │  Generated Content    │
                  │  • LinkedIn Post      │
                  │  • Twitter Thread     │
                  │  • YouTube Script     │
                  │  • Blog Article       │
                  │  • Email Newsletter   │
                  └───────────┬───────────┘
                              │
                              ▼
                  ┌───────────────────────┐
                  │  Image Generation     │
                  │  (If No Manual Images)│
                  │  • AI Image APIs      │
                  │  • Theme Selection    │
                  │  • Platform Resize    │
                  └───────────┬───────────┘
                              │
                              ▼
                  ┌───────────────────────┐
                  │   Database Storage    │
                  │   • Content JSON      │
                  │   • Metadata          │
                  │   • User Association  │
                  └───────────┬───────────┘
                              │
                              ▼
                  ┌───────────────────────┐
                  │   Frontend Display    │
                  │   • Platform Tabs     │
                  │   • Copy/Edit Tools   │
                  │   • Publishing Queue  │
                  └───────────────────────┘
```

---

## 📌 D. Tech Stack

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| **Next.js** | 14.x | React framework with App Router |
| **React** | 18.x | UI component library |
| **TypeScript** | 5.x | Type-safe JavaScript |
| **Tailwind CSS** | 3.x | Utility-first CSS framework |
| **Shadcn/ui** | Latest | Accessible component library |
| **Framer Motion** | 10.x | Animation library |
| **React Dropzone** | 14.x | File upload interface |
| **Axios** | 1.x | HTTP client for API calls |
| **Sonner** | Latest | Toast notifications |
| **date-fns** | 2.x | Date manipulation |

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| **Django** | 5.0+ | Web framework |
| **Django REST Framework** | 3.14+ | API development |
| **Python** | 3.10+ | Programming language |
| **PostgreSQL** | 15+ | Primary database |
| **pgvector** | 0.2+ | Vector similarity search |
| **Redis** | 5.0+ | Caching & message broker |
| **Celery** | 5.3+ | Async task queue |
| **django-celery-beat** | 2.5+ | Periodic task scheduler |

### AI & Machine Learning
| Technology | Purpose |
|------------|---------|
| **OpenAI API** | Primary LLM (GPT-4/GPT-3.5) |
| **Google Gemini API** | Fallback LLM + Embeddings |
| **Nano Banana (Google Imagen)** | AI image generation (primary) |
| **Fal.ai** | AI image generation (fallback) |
| **Freepik API** | AI image generation (fallback 2) |
| **Custom Vector Store** | Pure Python similarity search |

### Document Processing
| Library | Purpose |
|---------|---------|
| **pypdf** | PDF text extraction |
| **python-docx** | Word document processing |
| **BeautifulSoup4** | Web scraping |
| **readability-lxml** | Article content extraction |
| **Pillow (PIL)** | Image processing |

### Integration & Tools
| Technology | Purpose |
|------------|---------|
| **DuckDuckGo Search API** | Trend discovery |
| **JWT (SimpleJWT)** | Authentication tokens |
| **django-cors-headers** | Cross-origin resource sharing |
| **Gunicorn** | Production WSGI server |
| **Whitenoise** | Static file serving |

### Development Tools
| Tool | Purpose |
|------|---------|
| **Git** | Version control |
| **VSCode** | Code editor |
| **Postman** | API testing |
| **pgAdmin** | Database management |

---

## 📌 E. How to Run Your Project

### Prerequisites

Before you begin, ensure you have installed:

| Software | Version | Download |
|----------|---------|----------|
| **Node.js** | v18.0.0+ | [nodejs.org](https://nodejs.org/) |
| **Python** | v3.10+ | [python.org](https://www.python.org/downloads/) |
| **PostgreSQL** | v15+ | [postgresql.org](https://www.postgresql.org/download/) |
| **Redis** | Latest | [redis.io](https://redis.io/) or WSL |
| **Git** | Latest | [git-scm.com](https://git-scm.com/) |

### Step 1: Clone the Repository

```bash
git clone https://github.com/pranay2004/CONTEXIA_AI.git
cd CONTEXIA_AI
- **Redis Server** (for Celery task queue)

---

## 🚀 Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/yourusername/CONTEXIA.git
cd CONTEXIA
```

---

### 2️⃣ Backend Setup (Django + Celery)

#### **Step 2: Create Virtual Environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### **Step 3: Install Python Dependencies**
```bash
pip install -r requirements.txt
```

#### **Step 4: Configure Environment Variables**

Create a `.env` file in the `backend/` directory:

```env
# Django Settings
SECRET_KEY=your-django-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite by default)
DATABASE_URL=sqlite:///db.sqlite3

# AI Provider (choose one)
AI_PROVIDER=openai  # or 'gemini'
OPENAI_API_KEY=your-openai-api-key-here
GEMINI_API_KEY=your-gemini-api-key-here

# Celery & Redis
REDIS_URL=redis://127.0.0.1:6379/0

# NextAuth (must match frontend)
NEXTAUTH_SECRET=your-nextauth-secret-here

# Social Media OAuth (Optional)
LINKEDIN_CLIENT_ID=
LINKEDIN_CLIENT_SECRET=
TWITTER_CLIENT_ID=
TWITTER_CLIENT_SECRET=
```

#### **Step 5: Run Database Migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

#### **Step 6: Create Superuser (Admin Access)**
```bash
python manage.py createsuperuser
# Follow the prompts to create username, email, password
```

#### **Step 7: Start Redis Server**

**Option A: Windows with WSL**
```bash
wsl -d Ubuntu
sudo service redis-server start
```

**Option B: macOS**
```bash
brew services start redis
```

**Option C: Linux**
```bash
sudo systemctl start redis-server
```

#### **Step 8: Start Celery Worker**

Open a **new terminal** in the `backend/` directory:

```bash
# Windows
python -m celery -A project worker --loglevel=info --pool=solo

# macOS/Linux
celery -A project worker --loglevel=info
```

Keep this terminal running.

#### **Step 9: Start Django Development Server**

Open **another new terminal** in the `backend/` directory:

```bash
python manage.py runserver
```

✅ Backend running at: `http://localhost:8000`

---

### 3️⃣ Frontend Setup (Next.js)

#### **Step 1: Navigate to Frontend Directory**

Open a **new terminal**:

```bash
cd frontend
```

#### **Step 2: Install Dependencies**
```bash
npm install
```

#### **Step 3: Configure Environment Variables**

Create a `.env.local` file in the `frontend/` directory:

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# NextAuth Configuration
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-nextauth-secret-here-must-match-backend

# Social Media OAuth (Optional)
LINKEDIN_CLIENT_ID=
LINKEDIN_CLIENT_SECRET=
TWITTER_CLIENT_ID=
TWITTER_CLIENT_SECRET=
```

#### **Step 4: Start Next.js Development Server**
```bash
npm run dev
```

✅ Frontend running at: `http://localhost:3000`

---

## 🎮 Running the Application

### Required Terminals (4 total):

1. **Terminal 1 - Redis Server**
   ```bash
   # WSL/Linux
   wsl
   sudo service redis-server start
   ```

2. **Terminal 2 - Celery Worker**
   ```bash
   cd backend
   venv\Scripts\activate  # Windows
   python -m celery -A project worker --loglevel=info --pool=solo
   ```

3. **Terminal 3 - Django Backend**
   ```bash
   cd backend
   venv\Scripts\activate  # Windows
   python manage.py runserver
   ```

4. **Terminal 4 - Next.js Frontend**
   ```bash
   cd frontend
   npm run dev
   ```

### 🔐 First Time Login

1. Navigate to `http://localhost:3000`
2. Click **"Sign In"**
3. Register a new account or use:
   - **Username**: `testuser2`
   - **Password**: `testpass123`

---

## 📝 Usage Guide

### **Step 1: Upload Content**
- Go to **Content Lab** from the dashboard
- Upload a file (PDF, DOCX, PPTX, TXT) **OR** paste text
- Click **"Generate Content for All Platforms"**

### **Step 2: Wait for Generation**
- Generation happens in the background (Celery)
- Real-time status updates every 1 second
- Typically completes in **8-15 seconds**

### **Step 3: View Generated Content**
- Switch between platform tabs:
  - **LinkedIn**: Professional post with hashtags
  - **Twitter/X**: Multi-tweet thread
  - **YouTube**: Video script + description
  - **Blog**: Full SEO article with HTML

### **Step 4: Copy or Post**
- Use **Copy** buttons to copy content
- Use **Post** buttons for direct publishing (requires OAuth setup)

---

## ⚙️ Configuration

### AI Provider Selection

Edit `backend/.env`:

```env
# For OpenAI (GPT-4)
AI_PROVIDER=openai
OPENAI_API_KEY=sk-...

# For Google Gemini
AI_PROVIDER=gemini
GEMINI_API_KEY=...
```

### Performance Tuning

**Parallel Generation** (in `backend/apps/generator/gemini_wrapper.py`):
- Blog and social media generate simultaneously
- 50% faster than sequential generation

**Polling Interval** (in `frontend/app/dashboard/content/page.tsx`):
- Default: 1 second
- Adjust for slower networks: `setInterval(..., 2000)`

---

## 🏗️ Project Structure

```
CONTEXIA/
├── backend/                    # Django REST API
│   ├── apps/
│   │   ├── api/               # REST API endpoints
│   │   ├── generator/         # AI content generation
│   │   │   ├── tasks.py      # Celery async tasks
│   │   │   ├── openai_wrapper.py
│   │   │   └── gemini_wrapper.py
│   │   ├── ingest/           # File upload & processing
│   │   ├── trends/           # Trend scraping & vectorstore
│   │   ├── social/           # Social media integration
│   │   └── media/            # Image processing
│   ├── project/              # Django settings
│   │   ├── settings.py
│   │   ├── celery.py        # Celery configuration
│   │   └── urls.py
│   ├── manage.py
│   └── requirements.txt
│
├── frontend/                  # Next.js 14 App
│   ├── app/
│   │   ├── api/auth/         # NextAuth configuration
│   │   ├── dashboard/        # Protected routes
│   │   │   └── content/      # Content Lab page
│   │   ├── login/
│   │   └── register/
│   ├── components/
│   ├── lib/
│   │   ├── api-client.ts    # Axios API client
│   │   └── auth.ts
│   ├── types/
│   └── package.json
│
├── .gitignore
├── README.md
└── docker-compose.yml        # Docker setup (optional)
```

---

## 🐛 Troubleshooting

### **Issue: "401 Unauthorized" during generation**

**Solution**: Token expired. Log out and log back in.

```bash
# Clear Next.js cache
cd frontend
rm -rf .next
npm run dev
```

### **Issue: Celery worker not starting**

**Solution**: Check Redis connection

```bash
# Test Redis
redis-cli ping
# Should return: PONG

# Check Redis is running
wsl  # if on Windows
ps aux | grep redis
```

### **Issue: "ModuleNotFoundError" in backend**

**Solution**: Reinstall dependencies

```bash
cd backend
pip install --upgrade -r requirements.txt
```

### **Issue: Content generation takes too long**

**Solution**: Check AI provider configuration

```bash
# Verify API keys in backend/.env
cat backend/.env | grep API_KEY

# Check Celery logs for errors
# Look at Terminal 2 (Celery worker) output
```

---

## 🔧 Development Tools

### Django Admin Panel
- URL: `http://localhost:8000/admin`
- Login with superuser credentials
- Manage users, content, trends

### API Documentation
- Swagger UI: `http://localhost:8000/api/docs/` (if configured)
- Check available endpoints in `backend/apps/api/urls.py`

---

## 📦 Production Deployment

### Environment Variables Checklist

✅ Set `DEBUG=False` in backend  
✅ Use PostgreSQL instead of SQLite  
✅ Set secure `SECRET_KEY` and `NEXTAUTH_SECRET`  
✅ Configure CORS for production domain  
✅ Use managed Redis (Redis Cloud, AWS ElastiCache)  
✅ Set up HTTPS with SSL certificates  

### Recommended Stack
- **Frontend**: Vercel / Netlify
- **Backend**: AWS EC2, DigitalOcean, or Railway
- **Database**: PostgreSQL (AWS RDS, Supabase)
- **Redis**: Redis Cloud, AWS ElastiCache
- **Celery Worker**: Background process on same server

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **OpenAI** for GPT models
- **Google** for Gemini AI
- **Next.js** team for the amazing framework
- **Django** community for the robust backend

---

## 📧 Support

For issues, questions, or feature requests:
- 🐛 [Open an issue](https://github.com/yourusername/CONTEXIA/issues)
- 📧 Email: support@contexia.com
- 💬 Discord: [Join our community](https://discord.gg/contexia)

---

<div align="center">
  <p>Made with ❤️ by the CONTEXIA Team</p>
  <p>⭐ Star this repo if you find it helpful!</p>
</div

#### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 4: Configure Environment Variables
Create a `.env` file in the `backend` directory:

```env
SECRET_KEY=your-django-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1

# AI/API Keys (Optional - for full functionality)
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key

# Social Media API Keys (Optional - for direct posting)
LINKEDIN_CLIENT_ID=your-linkedin-client-id
LINKEDIN_CLIENT_SECRET=your-linkedin-secret
TWITTER_API_KEY=your-twitter-api-key
TWITTER_API_SECRET=your-twitter-secret
```

#### Step 5: Run Migrations
```bash
python manage.py migrate
```

#### Step 6: Create Superuser
```bash
python manage.py createsuperuser
```

#### Step 7: Start Django Server
```bash
python manage.py runserver
```

The backend will be available at `http://localhost:8000`

### 3. Frontend Setup (Next.js)

Open a new terminal window/tab.

#### Step 1: Navigate to Frontend Directory
```bash
cd frontend
```

#### Step 2: Install Dependencies
```bash
npm install
```

#### Step 3: Configure Environment Variables
Create a `.env.local` file in the `frontend` directory:

```env
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-nextauth-secret-key-here
NEXT_PUBLIC_API_URL=http://localhost:8000
```

To generate `NEXTAUTH_SECRET`:
```bash
openssl rand -base64 32
```

#### Step 4: Start Development Server
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## 🎯 Usage Guide

### First Time Setup

1. **Start Both Servers**:
   - Backend: `python manage.py runserver` (in backend directory)
   - Frontend: `npm run dev` (in frontend directory)

2. **Access the Application**:
   - Open your browser and go to `http://localhost:3000`

3. **Create an Account**:
   - Click "Register" on the landing page
   - Fill in your details
   - Or sign in with your Django superuser credentials

### Using the Content Lab

1. **Navigate to Content Lab**:
   - After logging in, click "Content Lab" in the sidebar

2. **Upload Your Content**:
   - Drag and drop a file (PDF, DOCX, PPT, or TXT)
   - OR paste text directly into the text area
   - Optionally add photos

3. **Generate Content**:
   - Click "Generate Content for All Platforms"
   - Wait for AI to analyze and generate posts (usually 10-30 seconds)

4. **Review and Post**:
   - Switch between platform tabs (LinkedIn, Twitter, YouTube, Blog)
   - Review generated content
   - Click "Copy" to copy to clipboard
   - Click "Post Now" to directly publish (requires social media accounts connected)

### Dashboard Overview

- **Overview**: View your content generation statistics and recent activity
- **Content Lab**: Upload and generate content
- **Analytics**: Track performance metrics across platforms

## 📁 Project Structure

```
CONTEXIA/
├── backend/                    # Django Backend
│   ├── apps/                   # Django Apps
│   │   ├── content/           # Content extraction & generation
│   │   ├── social/            # Social media integration
│   │   └── analytics/         # Analytics tracking
│   ├── config/                # Django settings
│   ├── requirements.txt       # Python dependencies
│   └── manage.py             # Django management script
│
├── frontend/                  # Next.js Frontend
│   ├── app/                  # Next.js App Router
│   │   ├── dashboard/       # Protected dashboard routes
│   │   ├── login/          # Authentication pages
│   │   └── register/
│   ├── components/          # React components
│   │   ├── ui/            # UI components
│   │   └── dashboard/     # Dashboard-specific components
│   ├── lib/               # Utilities
│   │   └── api-client.ts # API communication layer
│   ├── public/           # Static assets
│   └── package.json      # Node dependencies
│
└── README.md             # This file
```

## 🔧 API Endpoints

### Authentication
- `POST /api/token/` - Login and get JWT token
- `POST /api/token/refresh/` - Refresh JWT token
- `POST /api/register/` - Register new user

### Content
- `POST /api/extract/` - Upload and extract content from file
- `POST /api/generate-stream/` - Generate content for platforms
- `GET /api/jobs/{task_id}/` - Check generation task status
- `GET /api/stats/uploads/` - Get user's uploaded files

### Social Media
- `GET /api/social/accounts/` - Get connected social accounts
- `POST /api/social/posts/direct-post/` - Post directly to platform
- `GET /api/analytics/` - Get user analytics

### Health
- `GET /api/health/` - Check API health status

## 🚨 Troubleshooting

### Backend Issues

**Port Already in Use**:
```bash
# Find process using port 8000
# Windows:
netstat -ano | findstr :8000

# macOS/Linux:
lsof -i :8000

# Kill the process and restart
python manage.py runserver
```

**Database Errors**:
```bash
# Delete database and recreate
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

**Module Not Found**:
```bash
# Ensure virtual environment is activated
# Reinstall dependencies
pip install -r requirements.txt
```

### Frontend Issues

**Port 3000 in Use**:
```bash
# Use a different port
npm run dev -- -p 3001
```

**Module Not Found**:
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Build Errors**:
```bash
# Clear Next.js cache
rm -rf .next
npm run dev
```

**Authentication Issues**:
- Verify `NEXTAUTH_URL` matches your frontend URL
- Ensure `NEXTAUTH_SECRET` is set in `.env.local`
- Check that backend is running and accessible

## 🔐 Security Notes

1. **Never commit `.env` files** to version control
2. Change `SECRET_KEY` and `NEXTAUTH_SECRET` in production
3. Set `DEBUG=False` in production
4. Use HTTPS in production
5. Regularly update dependencies for security patches

## 📦 Building for Production

### Backend
```bash
cd backend
pip install gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

### Frontend
```bash
cd frontend
npm run build
npm start
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Contact: support@contexia.com
- Documentation: https://docs.contexia.com

## 🎉 Acknowledgments

- OpenAI for GPT models
- Anthropic for Claude
- Next.js team
- Django community
- All contributors

---

**Made with ❤️ by the CONTEXIA Team**
`

### Step 2: Backend Setup (Django)

#### 2.1 Navigate to Backend Directory
```bash
cd backend
```

#### 2.2 Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 2.3 Install Python Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 2.4 Set Up PostgreSQL Database

**Create Database:**
```sql
-- Open PostgreSQL command line (psql)
CREATE DATABASE contexia_db;
CREATE USER contexia_user WITH PASSWORD 'your_secure_password';
ALTER ROLE contexia_user SET client_encoding TO 'utf8';
ALTER ROLE contexia_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE contexia_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE contexia_db TO contexia_user;

-- Enable pgvector extension
\c contexia_db
CREATE EXTENSION IF NOT EXISTS vector;
```

#### 2.5 Configure Environment Variables

Create .env file in ackend/ directory:

```env
# Django Settings
SECRET_KEY=your-super-secret-django-key-change-this-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DB_NAME=contexia_db
DB_USER=contexia_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432

# AI Provider Configuration (Choose one or both)
# Option 1: OpenAI (Primary)
OPENAI_API_KEY=sk-your-openai-api-key-here
AI_PROVIDER=openai  # or 'gemini'

# Option 2: Google Gemini (Alternative/Fallback)
GOOGLE_API_KEY=your-google-gemini-api-key-here

# AI Image Generation APIs (Optional)
NANO_BANANA_API_KEY=your-nano-banana-api-key
FAL_API_KEY=your-fal-ai-api-key
FREEPIK_API_KEY=your-freepik-api-key

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=django-db

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

#### 2.6 Run Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

#### 2.7 Create Superuser
```bash
python manage.py createsuperuser
```

#### 2.8 Start Django Development Server
```bash
python manage.py runserver
```

---

### Step 3: Start Redis & Celery

#### 3.1 Start Redis Server
```bash
# Windows WSL
wsl redis-server

# macOS
brew services start redis

# Linux
sudo service redis-server start
```

#### 3.2 Start Celery Worker
```bash
# Windows
celery -A project worker --loglevel=info --pool=solo

# macOS/Linux
celery -A project worker --loglevel=info
```

---

### Step 4: Frontend Setup (Next.js)

#### 4.1 Navigate to Frontend
```bash
cd frontend
```

#### 4.2 Install Dependencies
```bash
npm install
```

#### 4.3 Configure Environment

Create .env.local:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-nextauth-secret
```

#### 4.4 Start Next.js
```bash
npm run dev
```

---

##  F. API Keys / Usage Notes

### Required API Keys

#### 1. AI/LLM Provider (Choose One)

**OpenAI**
- Get Key: platform.openai.com/api-keys
- Models: GPT-4, GPT-3.5-turbo
- Pricing: ~.01-0.03 per 1K tokens
- Variable: OPENAI_API_KEY=sk-...

**Google Gemini** 
- Get Key: makersuite.google.com/app/apikey
- Models: Gemini-1.5-flash, Gemini-1.5-pro
- Pricing: Free tier available
- Variable: GOOGLE_API_KEY=AIza...

#### 2. Database

**PostgreSQL with pgvector**
- Self-hosted, no API key
- Extension required: pgvector

---

##  G. Sample Inputs & Outputs

See comprehensive examples in the full documentation above.

---

##  Additional Resources

- **API Documentation**: ackend/API_DOCS.md
- **AI Image Setup**: ackend/AI_IMAGE_SETUP.md
- **Contributing**: CONTRIBUTING.md

---

##  License

MIT License - see LICENSE file

---

##  Support

- **Issues**: GitHub Issues
- **Email**: support@contexia.ai

---

** Star us on GitHub if you find this useful!**
=======
# Moon-phoenix
>>>>>>> 42eb12482ff1ff6a9fbc1a4f6ac1f312c1de2784
