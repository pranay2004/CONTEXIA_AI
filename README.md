# 🚀 CONTEXIA - AI-Powered Content Generation Platform

[![Next.js](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org/)
[![Django](https://img.shields.io/badge/Django-5.0-green)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📖 Overview

**CONTEXIA** is an intelligent content generation platform that transforms your raw content (PDFs, documents, presentations, or text) into platform-ready social media posts. Powered by advanced AI (OpenAI/Gemini), it analyzes your content and automatically generates optimized posts for LinkedIn, Twitter, YouTube, and blogs with real-time generation using Celery background tasks.

## ✨ Features

### 🎯 Core Functionality
- **📤 Unified Content Upload**: Upload PDFs, DOCX, PPTX, or paste text directly
- **🤖 AI-Powered Generation**: Uses OpenAI/Gemini with parallel execution for 2x faster generation
- **🔄 Async Processing**: Background task processing with Celery & Redis
- **📱 Multi-Platform Output**: Automatically generates content for:
  - LinkedIn posts with hashtags
  - Twitter/X threads (multi-tweet support)
  - YouTube video scripts with descriptions
  - SEO-optimized blog articles
- **🖼️ Image Processing**: Auto-edit and optimize photos for each platform
- **📊 Real-time Polling**: 1-second status updates during generation
- **🔐 Secure Authentication**: JWT-based auth with NextAuth.js
- **📈 Analytics Dashboard**: Track performance across all platforms

### 🎨 User Experience
- Beautiful, modern UI with Tailwind CSS
- Real-time content generation with progress tracking
- Copy-to-clipboard functionality
- Platform-specific content previews
- Responsive design for all devices
- Dark mode support

---

## 📋 Prerequisites

Before you begin, ensure you have installed:

| Software | Version | Download |
|----------|---------|----------|
| **Node.js** | v18.0.0+ | [nodejs.org](https://nodejs.org/) |
| **Python** | v3.10+ | [python.org](https://www.python.org/downloads/) |
| **Redis** | Latest | [redis.io](https://redis.io/) or WSL |
| **Git** | Latest | [git-scm.com](https://git-scm.com/) |

### Additional Requirements
- **OpenAI API Key** or **Google Gemini API Key** (for AI generation)
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
