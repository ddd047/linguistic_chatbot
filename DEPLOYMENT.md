# Multilingual Campus Chatbot - Deployment Guide

This guide will help student volunteers deploy and maintain the multilingual campus chatbot system.

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8 or higher** installed on your system
2. **Basic terminal/command prompt** knowledge
3. **Internet connection** for installing dependencies

### Step 1: Setup Backend

1. **Navigate to backend folder:**
   ```bash
   cd backend
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the backend server:**
   ```bash
   python main.py
   ```
   
   The server will start at `http://localhost:8000`

### Step 2: Setup Frontend

1. **Open a new terminal/command prompt**
2. **Navigate to frontend folder:**
   ```bash
   cd frontend
   ```

3. **Start a simple web server:**
   
   **Option A - Using Python:**
   ```bash
   python -m http.server 3000
   ```
   
   **Option B - Using Node.js (if available):**
   ```bash
   npx serve -s . -l 3000
   ```

4. **Open your browser** and go to:
   - Main interface: `http://localhost:3000`
   - Widget demo: `http://localhost:3000/widget.html`

## 🔧 Configuration

### Backend Configuration

Edit `backend/main.py` to customize:

1. **Server Port** (line 199):
   ```python
   uvicorn.run(app, host="0.0.0.0", port=8000)  # Change port here
   ```

2. **CORS Origins** (line 19):
   ```python
   allow_origins=["*"]  # In production, specify exact domains
   ```

### Knowledge Base Customization

Edit `data/knowledge_base.json` to:

1. **Add new categories:**
   ```json
   "new_category": {
     "keywords": ["keyword1", "keyword2", "नया", "નવું"],
     "responses": {
       "en": "English response",
       "hi": "हिंदी उत्तर",
       "gu": "ગુજરાતી જવાબ"
     }
   }
   ```

2. **Update contact information:**
   ```json
   "contact": {
     "office_hours": "9:00 AM - 5:00 PM, Monday to Friday",
     "phone": "+91-YOUR-COLLEGE-NUMBER",
     "email": "your-college@email.edu",
     "address": "Your College Address"
   }
   ```

## 🌐 Website Integration

### Method 1: Embedded Widget

Add this code to any webpage:

```html
<script src="http://your-domain.com:8000/widget/embed.js"></script>
```

### Method 2: iFrame Integration

```html
<iframe 
    src="http://your-domain.com:3000/widget.html" 
    width="350" 
    height="500"
    frameborder="0">
</iframe>
```

### Method 3: Full Page Integration

Simply link to: `http://your-domain.com:3000`

## 📱 Testing the System

### Test with Sample Queries

Try these sample queries in different languages:

**English:**
- "What are the fees?"
- "How to apply for scholarship?"
- "Library timing"

**Hindi:**
- "शुल्क क्या है?"
- "छात्रवृत्ति के लिए कैसे आवेदन करें?"
- "पुस्तकालय का समय"

**Gujarati:**
- "ફી કેટલી છે?"
- "સ્કોલરશિપ માટે કેવી રીતે અરજી કરવી?"

### Checking System Health

1. **Backend Health Check:**
   Visit: `http://localhost:8000/health`

2. **View Conversation Logs:**
   Visit: `http://localhost:8000/logs/daily`

## 🔍 Monitoring and Maintenance

### Daily Tasks

1. **Check system status** - ensure both frontend and backend are running
2. **Review conversation logs** - identify common unanswered questions
3. **Monitor error logs** - check terminal output for issues

### Weekly Tasks

1. **Update knowledge base** based on new queries
2. **Review and improve responses** that had low confidence scores
3. **Clean up old conversation logs** if needed

### Monthly Tasks

1. **Update college information** (fees, dates, contact info)
2. **Add new categories** based on seasonal queries
3. **Performance optimization** if needed

## 🛠️ Troubleshooting

### Common Issues

**"Module not found" error:**
```bash
# Solution: Install missing dependencies
pip install -r requirements.txt
```

**"Port already in use" error:**
```bash
# Solution: Change port number in main.py or kill existing process
# Windows:
netstat -ano | findstr :8000
taskkill /F /PID [PID_NUMBER]

# Linux/Mac:
lsof -ti:8000 | xargs kill -9
```

**Frontend not loading:**
- Check if web server is running
- Verify port number (default: 3000)
- Check browser console for errors

**Chatbot not responding:**
- Ensure backend server is running on port 8000
- Check CORS settings if accessing from different domain
- Verify API_BASE_URL in frontend/script.js

### Log Files

**Backend logs:** Check terminal output where you ran `python main.py`

**Frontend errors:** Open browser Developer Tools (F12) → Console

**Conversation logs:** Stored in `data/conversations.db` (SQLite database)

## 📋 Production Deployment

### For Production Use

1. **Use a proper web server:**
   - Nginx or Apache for frontend
   - Gunicorn for Python backend

2. **Secure the system:**
   - Use HTTPS
   - Implement proper authentication
   - Set specific CORS origins
   - Use environment variables for sensitive data

3. **Database backup:**
   - Regularly backup `data/conversations.db`
   - Consider using PostgreSQL for production

4. **Domain and SSL:**
   - Get a proper domain name
   - Install SSL certificate
   - Update API_BASE_URL in frontend

### Sample Production Commands

```bash
# Backend with Gunicorn
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000

# Frontend with Nginx (config file)
server {
    listen 80;
    server_name your-domain.com;
    root /path/to/frontend;
    index index.html;
}
```

## 🆘 Getting Help

### Resources

1. **FastAPI Documentation:** https://fastapi.tiangolo.com/
2. **Python HTTP Server:** https://docs.python.org/3/library/http.server.html
3. **SQLite Browser:** https://sqlitebrowser.org/ (for viewing logs)

### Common Commands Reference

```bash
# Check Python version
python --version

# Install specific package
pip install package-name

# List running processes on port
netstat -tulnp | grep :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Start backend in background (Linux/Mac)
nohup python main.py &

# Check if ports are available
telnet localhost 8000
telnet localhost 3000
```

### Support Contacts

- **Technical Issues:** Contact your college IT department
- **Content Updates:** Contact academic administration
- **System Maintenance:** Designated student volunteer team

---

**Important:** Always test changes in a development environment before applying to production!

**Backup:** Keep regular backups of the knowledge base and conversation logs.

**Security:** Never commit sensitive information like API keys or passwords to version control.
