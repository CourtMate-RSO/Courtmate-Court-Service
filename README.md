# Court Service

A FastAPI microservice for handling court-related operations, including finding nearby courts based on geographic location.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker and Docker Compose (optional)
- Supabase account and project

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Courtmate-Court-Service
   ```

2. **Set up environment variables**
   ```bash
   # Copy the example environment file
   cp .example.env .env
   
   # Edit .env and add your actual Supabase credentials
   # Get these from: https://app.supabase.com/project/_/settings/api
   nano .env  # or use your preferred editor
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the service**
   ```bash
   # Development mode with auto-reload
   uvicorn app.main:app --reload --port 8000
   
   # Or use Docker Compose
   docker-compose up
   ```

5. **Access the API**
   - API Documentation: http://localhost:8000/api/v1/facilities/docs
   - Health Check: http://localhost:8000/health

## 🔐 Environment Variables

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `SUPABASE_URL` | Your Supabase project URL | Yes | `https://xxxxx.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | Service role key (admin access) | Yes | `eyJhbGc...` |
| `SUPABASE_ANON_KEY` | Anonymous/public key | Yes | `eyJhbGc...` |
| `SUPABASE_JWT_SECRET` | JWT secret for token verification | Yes | `your-secret` |
| `ENV` | Environment (dev/staging/prod) | No | `dev` |
| `API_VERSION` | API version prefix | No | `v1` |

### 🔒 Security Notes

- **NEVER** commit `.env` file to version control
- `.env` contains sensitive credentials and should only exist locally
- Use `.env.example` as a template (no real values)
- For production, use secure secret management:
  - Kubernetes Secrets
  - AWS Secrets Manager / Parameter Store
  - Azure Key Vault
  - Google Cloud Secret Manager
  - HashiCorp Vault

## 🐳 Docker Deployment

### Development
```bash
docker-compose up
```

### Production
```bash
# Build the image
docker build -t court-service:latest .

# Run with environment variables (DO NOT use .env file in production)
docker run -d \
  -p 8000:8000 \
  -e SUPABASE_URL=$SUPABASE_URL \
  -e SUPABASE_SERVICE_ROLE_KEY=$SUPABASE_SERVICE_ROLE_KEY \
  -e SUPABASE_ANON_KEY=$SUPABASE_ANON_KEY \
  -e SUPABASE_JWT_SECRET=$SUPABASE_JWT_SECRET \
  -e ENV=prod \
  court-service:latest
```

## 📝 API Endpoints

### Facilities
- `GET /api/v1/facilities/` - List all facilities
- `GET /api/v1/facilities/{id}` - Get facility by ID
- `POST /api/v1/facilities/` - Create new facility
- `POST /api/v1/facilities/nearby` - Find nearby facilities

### Health
- `GET /health` - Service health check

## 🏗️ Project Structure

```
Courtmate-Court-Service/
├── app/
│   ├── main.py              # FastAPI application
│   ├── routes.py            # API endpoints
│   ├── models.py            # Pydantic models
│   ├── config.py            # Configuration settings
│   └── supabase_client.py   # Database client
├── sql/                     # SQL scripts
├── .env                     # Local secrets (NOT in git)
├── .example.env             # Template for .env
├── requirements.txt         # Python dependencies
├── dockerfile              # Docker configuration
└── docker-compose.yml      # Docker Compose setup
```
