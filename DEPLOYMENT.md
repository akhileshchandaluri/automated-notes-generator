# 🚀 Deployment Guide

Complete guide for deploying the Automated PDF Notes Generator.

## 📋 Table of Contents

1. [Local Development](#local-development)
2. [Streamlit Cloud](#streamlit-cloud)
3. [Docker Deployment](#docker-deployment)
4. [Cloud Platforms](#cloud-platforms)
5. [Production Considerations](#production-considerations)

---

## 🏠 Local Development

### Quick Start

**Windows:**
```bash
run.bat
```

**Linux/Mac:**
```bash
chmod +x run.sh
./run.sh
```

### Manual Start

```bash
# Activate virtual environment (if using)
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows

# Run app
streamlit run app.py
```

### Configuration

Edit `config/config.py` to customize:
- NLP parameters
- Output settings
- Processing options

---

## ☁️ Streamlit Cloud Deployment

### Prerequisites

- GitHub account
- Streamlit Cloud account (free at streamlit.io)
- Project pushed to GitHub

### Steps

1. **Prepare Repository**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/username/automated-notes-gen.git
   git push -u origin main
   ```

2. **Create `packages.txt` (for system dependencies)**
   ```
   # Not needed for this project
   # Add if you need system packages
   ```

3. **Verify `requirements.txt`**
   - Already created
   - Ensure all dependencies listed

4. **Deploy on Streamlit Cloud**
   - Go to https://share.streamlit.io
   - Click "New app"
   - Select your repository
   - Set main file: `app.py`
   - Click "Deploy"

5. **Configure Secrets** (if needed)
   - Click "Advanced settings"
   - Add any API keys or secrets
   - Format: TOML

### Notes for Streamlit Cloud

- Free tier: 1GB RAM, 1 CPU
- App will sleep after inactivity
- Large PDFs may need more resources
- Consider upgrading for production

---

## 🐳 Docker Deployment

### Create Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data
RUN python -c "import nltk; \
    nltk.download('punkt'); \
    nltk.download('stopwords'); \
    nltk.download('wordnet'); \
    nltk.download('punkt_tab')"

# Download spaCy model (optional)
RUN python -m spacy download en_core_web_sm

# Copy application code
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run app
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Create docker-compose.yml

```yaml
version: '3.8'

services:
  notes-generator:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
      - ./output:/app/output
    environment:
      - STREAMLIT_SERVER_MAXUPLOADSIZE=50
    restart: unless-stopped
```

### Build and Run

```bash
# Build image
docker build -t notes-generator .

# Run container
docker run -p 8501:8501 notes-generator

# Or use docker-compose
docker-compose up -d
```

### Docker Hub Deployment

```bash
# Tag image
docker tag notes-generator username/notes-generator:latest

# Push to Docker Hub
docker push username/notes-generator:latest
```

---

## ☁️ Cloud Platforms

### AWS EC2

1. **Launch EC2 Instance**
   - Ubuntu 22.04 LTS
   - t2.medium or larger (2GB+ RAM)
   - Open port 8501

2. **Setup Script**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install Python
   sudo apt install python3-pip python3-venv -y
   
   # Clone repository
   git clone https://github.com/username/automated-notes-gen.git
   cd automated-notes-gen
   
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Download models
   python setup.py
   
   # Run with nohup
   nohup streamlit run app.py --server.port=8501 --server.address=0.0.0.0 &
   ```

3. **Use systemd for Auto-Start**
   
   Create `/etc/systemd/system/notes-generator.service`:
   ```ini
   [Unit]
   Description=PDF Notes Generator
   After=network.target
   
   [Service]
   Type=simple
   User=ubuntu
   WorkingDirectory=/home/ubuntu/automated-notes-gen
   Environment="PATH=/home/ubuntu/automated-notes-gen/venv/bin"
   ExecStart=/home/ubuntu/automated-notes-gen/venv/bin/streamlit run app.py
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```
   
   Enable service:
   ```bash
   sudo systemctl enable notes-generator
   sudo systemctl start notes-generator
   sudo systemctl status notes-generator
   ```

### Google Cloud Platform (Cloud Run)

1. **Create `app.yaml`**
   ```yaml
   runtime: python39
   
   entrypoint: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   
   env_variables:
     STREAMLIT_SERVER_MAX_UPLOAD_SIZE: 50
   ```

2. **Deploy**
   ```bash
   gcloud app deploy
   ```

### Heroku

1. **Create `Procfile`**
   ```
   web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```

2. **Create `runtime.txt`**
   ```
   python-3.9.16
   ```

3. **Deploy**
   ```bash
   heroku create notes-generator
   git push heroku main
   ```

---

## 🔧 Production Considerations

### Performance Optimization

1. **Caching**
   ```python
   # In app.py, add caching
   @st.cache_data
   def load_model():
       return NotesGenerator()
   ```

2. **Async Processing**
   - Consider Celery for background tasks
   - Use Redis for task queue
   - Store results in database

3. **Resource Limits**
   - Limit PDF size (currently 50MB)
   - Set timeout for processing
   - Implement queue system for multiple users

### Security

1. **File Upload Security**
   - Validate file types
   - Scan for malware
   - Limit file size
   - Use temporary storage

2. **Environment Variables**
   ```python
   # Use python-dotenv
   from dotenv import load_dotenv
   import os
   
   load_dotenv()
   API_KEY = os.getenv('API_KEY')
   ```

3. **HTTPS**
   - Use reverse proxy (nginx)
   - SSL certificate (Let's Encrypt)

### Monitoring

1. **Logging**
   ```python
   import logging
   
   logging.basicConfig(
       level=logging.INFO,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
       handlers=[
           logging.FileHandler('app.log'),
           logging.StreamHandler()
       ]
   )
   ```

2. **Error Tracking**
   - Integrate Sentry
   - Monitor exceptions
   - Track performance

3. **Analytics**
   - Track usage statistics
   - Monitor processing times
   - User behavior analytics

### Scaling

1. **Horizontal Scaling**
   - Use load balancer
   - Multiple app instances
   - Shared storage for outputs

2. **Database Integration**
   - Store user data
   - Cache results
   - User authentication

3. **CDN for Static Files**
   - Use CloudFront or Cloudflare
   - Cache static assets

---

## 📊 Cost Estimation

### Streamlit Cloud
- **Free Tier**: $0/month
  - 1 app
  - 1GB RAM
  - Limited hours

- **Pro**: $20/month
  - Unlimited apps
  - More resources

### AWS EC2
- **t2.medium**: ~$30/month
  - 2 vCPU, 4GB RAM
  - Suitable for moderate traffic

- **t2.large**: ~$60/month
  - 2 vCPU, 8GB RAM
  - Better for high traffic

### Docker (Self-Hosted)
- Variable based on server
- $5-50/month for VPS
- Full control

---

## 🔄 CI/CD Pipeline

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        python setup.py
    
    - name: Run tests
      run: python test.py
  
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - name: Deploy to server
      # Add deployment steps
      run: echo "Deploying..."
```

---

## 📝 Environment Variables

Create `.env` file (don't commit):

```bash
# Application Settings
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_SERVER_MAX_UPLOAD_SIZE=50

# API Keys (if needed in future)
# OPENAI_API_KEY=your_key_here

# Database (if added)
# DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Storage (if using cloud)
# AWS_ACCESS_KEY_ID=your_key
# AWS_SECRET_ACCESS_KEY=your_secret
# S3_BUCKET_NAME=your_bucket
```

---

## 🎯 Post-Deployment Checklist

- [ ] App accessible via URL
- [ ] File upload works
- [ ] PDF processing completes
- [ ] All tabs display correctly
- [ ] Download buttons work
- [ ] Error handling functions
- [ ] Logs are being written
- [ ] Performance acceptable
- [ ] Mobile responsive
- [ ] HTTPS enabled (production)
- [ ] Backups configured
- [ ] Monitoring active

---

## 🆘 Troubleshooting

### Common Issues

**Out of Memory**
- Increase instance size
- Implement file size limits
- Add memory monitoring

**Slow Processing**
- Optimize algorithms
- Add progress indicators
- Implement caching

**NLTK Data Missing**
- Run download commands
- Check data directory
- Verify permissions

**spaCy Model Not Found**
- Download model manually
- Check installation path
- Use fallback without spaCy

---

## 📞 Support

For deployment issues:
1. Check logs: `app.log`
2. Run test suite: `python test.py`
3. Review error messages
4. Check GitHub Issues
5. Contact support

---

## 🔄 Updates and Maintenance

### Regular Updates

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart service
sudo systemctl restart notes-generator
```

### Backup Strategy

- Backup output directory daily
- Version control all code
- Document configuration changes
- Test backups regularly

---

## 📚 Additional Resources

- [Streamlit Documentation](https://docs.streamlit.io)
- [Docker Documentation](https://docs.docker.com)
- [AWS EC2 Guide](https://aws.amazon.com/ec2/getting-started/)
- [NLTK Documentation](https://www.nltk.org)
- [spaCy Documentation](https://spacy.io)
