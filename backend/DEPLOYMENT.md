# Deployment Guide - Music Transcription API

## 🚀 Deployment Options

### Option 1: Google Cloud Run (Recommended)

#### Prerequisites
- Google Cloud account
- `gcloud` CLI installed
- Firebase project set up

#### Steps

1. **Install Google Cloud SDK**
```bash
# macOS
brew install google-cloud-sdk

# Or download from: https://cloud.google.com/sdk/docs/install
```

2. **Authenticate**
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

3. **Build and push Docker image**
```bash
cd backend

# Build image
docker build -t gcr.io/YOUR_PROJECT_ID/music-transcription-api:latest .

# Push to Google Container Registry
docker push gcr.io/YOUR_PROJECT_ID/music-transcription-api:latest
```

4. **Deploy to Cloud Run**
```bash
gcloud run deploy music-transcription-api \
  --image gcr.io/YOUR_PROJECT_ID/music-transcription-api:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="ENVIRONMENT=production" \
  --set-env-vars="FIREBASE_PROJECT_ID=YOUR_PROJECT_ID" \
  --set-env-vars="JWT_SECRET_KEY=YOUR_SECRET_KEY" \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300
```

5. **Set up Redis (Cloud Memorystore)**
```bash
gcloud redis instances create music-transcription-redis \
  --size=1 \
  --region=us-central1 \
  --redis-version=redis_7_0
```

6. **Deploy Celery Worker**
```bash
# Deploy as a separate Cloud Run service
gcloud run deploy music-transcription-worker \
  --image gcr.io/YOUR_PROJECT_ID/music-transcription-api:latest \
  --platform managed \
  --region us-central1 \
  --no-allow-unauthenticated \
  --command="celery" \
  --args="-A,app.tasks.celery_app,worker,--loglevel=info" \
  --memory 4Gi \
  --cpu 2
```

---

### Option 2: Heroku

#### Prerequisites
- Heroku account
- Heroku CLI installed

#### Steps

1. **Install Heroku CLI**
```bash
# macOS
brew tap heroku/brew && brew install heroku

# Or download from: https://devcenter.heroku.com/articles/heroku-cli
```

2. **Login and create app**
```bash
heroku login
heroku create music-transcription-api
```

3. **Add Redis addon**
```bash
heroku addons:create heroku-redis:hobby-dev
```

4. **Set environment variables**
```bash
heroku config:set ENVIRONMENT=production
heroku config:set JWT_SECRET_KEY=your-secret-key
heroku config:set FIREBASE_PROJECT_ID=your-project-id
heroku config:set FIREBASE_STORAGE_BUCKET=your-bucket
```

5. **Deploy**
```bash
cd backend
git init
heroku git:remote -a music-transcription-api
git add .
git commit -m "Initial deployment"
git push heroku main
```

6. **Scale workers**
```bash
heroku ps:scale web=1 worker=1
```

---

### Option 3: Railway

#### Prerequisites
- Railway account
- Railway CLI installed

#### Steps

1. **Install Railway CLI**
```bash
npm install -g @railway/cli
```

2. **Login and initialize**
```bash
railway login
railway init
```

3. **Add Redis**
```bash
railway add redis
```

4. **Deploy**
```bash
cd backend
railway up
```

5. **Set environment variables**
```bash
railway variables set ENVIRONMENT=production
railway variables set JWT_SECRET_KEY=your-secret-key
railway variables set FIREBASE_PROJECT_ID=your-project-id
```

---

## 🔧 Environment Variables for Production

### Required Variables
```bash
ENVIRONMENT=production
API_HOST=0.0.0.0
API_PORT=8000

# Firebase
FIREBASE_CREDENTIALS_PATH=/app/firebase-credentials.json
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_STORAGE_BUCKET=your-bucket

# JWT
JWT_SECRET_KEY=generate-secure-random-string
JWT_ALGORITHM=HS256
JWT_EXPIRATION_DAYS=7

# Redis
REDIS_HOST=your-redis-host
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password

# Celery
CELERY_BROKER_URL=redis://your-redis-url
CELERY_RESULT_BACKEND=redis://your-redis-url

# External APIs
YOUTUBE_API_KEY=your-youtube-key
SPOTIFY_CLIENT_ID=your-spotify-id
SPOTIFY_CLIENT_SECRET=your-spotify-secret
```

### Generate Secure Keys
```bash
# JWT Secret Key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Or use OpenSSL
openssl rand -base64 32
```

---

## 📊 Monitoring Setup

### 1. Sentry (Error Tracking)

```bash
pip install sentry-sdk[fastapi]
```

Add to `app/main.py`:
```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FastApiIntegration()],
    environment=settings.environment,
    traces_sample_rate=1.0,
)
```

### 2. Google Cloud Logging

Already configured via JSON logging format.

### 3. Prometheus Metrics

```bash
pip install prometheus-fastapi-instrumentator
```

Add to `app/main.py`:
```python
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

---

## 🔒 Security Checklist

- [ ] Change JWT_SECRET_KEY to a secure random string
- [ ] Enable HTTPS/TLS
- [ ] Set up CORS properly (restrict origins in production)
- [ ] Enable Firebase Security Rules
- [ ] Set up rate limiting
- [ ] Enable API authentication
- [ ] Secure Redis with password
- [ ] Use environment variables for secrets
- [ ] Enable logging and monitoring
- [ ] Set up backup strategy
- [ ] Configure firewall rules
- [ ] Enable DDoS protection

---

## 🧪 Pre-Deployment Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Load testing
pip install locust
locust -f tests/load_test.py
```

---

## 📈 Scaling Considerations

### Horizontal Scaling
- Use Cloud Run auto-scaling
- Scale Celery workers based on queue length
- Use Redis Cluster for high availability

### Vertical Scaling
- Increase memory for AI/ML processing
- Increase CPU for faster transcription
- Use GPU instances for ML models (future)

### Database Optimization
- Create Firestore indexes
- Implement caching strategy
- Use connection pooling

---

## 🔄 CI/CD Pipeline

GitHub Actions workflow is already configured in `.github/workflows/backend-ci.yml`

### Automatic Deployment

Add to GitHub Actions:
```yaml
- name: Deploy to Cloud Run
  uses: google-github-actions/deploy-cloudrun@v1
  with:
    service: music-transcription-api
    image: gcr.io/${{ secrets.GCP_PROJECT_ID }}/music-transcription-api:latest
    region: us-central1
```

---

## 📝 Post-Deployment Checklist

- [ ] Verify health check endpoint
- [ ] Test authentication flow
- [ ] Check logs for errors
- [ ] Monitor API response times
- [ ] Verify Redis connection
- [ ] Test Celery workers
- [ ] Check Firebase connectivity
- [ ] Verify external API integrations
- [ ] Test rate limiting
- [ ] Monitor resource usage
- [ ] Set up alerts
- [ ] Document API endpoints
- [ ] Update DNS records
- [ ] Enable SSL certificate

---

## 🆘 Troubleshooting

### API not starting
```bash
# Check logs
gcloud run services logs read music-transcription-api --limit=50

# Or for Heroku
heroku logs --tail
```

### Redis connection issues
```bash
# Test Redis connection
redis-cli -h your-redis-host -p 6379 ping
```

### Firebase authentication errors
- Verify firebase-credentials.json is present
- Check FIREBASE_PROJECT_ID matches your project
- Verify Firebase APIs are enabled

### High memory usage
- Increase container memory
- Optimize AI model loading
- Implement model caching

---

## 📞 Support

For deployment issues:
1. Check logs first
2. Review environment variables
3. Verify all services are running
4. Check network connectivity
5. Review security rules

---

**Deployment Status**: Ready for production deployment
**Last Updated**: 2026-01-31
