# Court Service

A FastAPI microservice for handling court-related operations, including finding nearby courts based on geographic location.


## 🔐 Environment Variables

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `SUPABASE_URL` | Your Supabase project URL | Yes | `https://xxxxx.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | Service role key (admin access) | Yes | `eyJhbGc...` |
| `SUPABASE_ANON_KEY` | Anonymous/public key | Yes | `eyJhbGc...` |
| `SUPABASE_JWT_SECRET` | JWT secret for token verification | Yes | `your-secret` |
| `ENV` | Environment (dev/staging/prod) | No | `dev` |
| `API_VERSION` | API version prefix | No | `v1` |

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
