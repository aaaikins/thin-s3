# The 'Thin' S3 Service

A lightweight, high-performance FastAPI-based S3 service with built-in caching, background task processing, and secure authentication.

## Features

- **FastAPI Framework**: Modern, fast web framework for building APIs
- **S3 Integration**: Seamless AWS S3 storage operations
- **Redis Caching**: High-performance in-memory caching layer
- **Background Tasks**: Asynchronous task processing with Celery
- **Security**: JWT-based authentication and authorization
- **CORS Support**: Cross-origin resource sharing enabled
- **Docker Support**: Complete containerization with Docker Compose
- **Health Checks**: Built-in health check endpoint

## Prerequisites

- Python 3.9+
- Docker & Docker Compose (optional, for containerized deployment)
- AWS S3 credentials (for S3 operations)
- Redis server (for caching)

## Installation

### Local Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd thin-s3
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env  # If available
   # Edit .env with your configuration
   ```

## Configuration

Set the following environment variables in your `.env` file:

```env
# AWS S3
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_S3_BUCKET=your_bucket_name
AWS_REGION=us-east-1

# Redis
REDIS_URL=redis://localhost:6379

# API
API_DEBUG=True
API_HOST=0.0.0.0
API_PORT=8000

# Security
SECRET_KEY=your_secret_key_here
```

## Running the Application

### Local Development

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- Alternative Docs: `http://localhost:8000/redoc`

### Docker Deployment

```bash
docker-compose up --build
```

The service will be available at `http://localhost:8000`

## API Endpoints

### Health Check

```
GET /health
```

Response:
```json
{
  "status": "healthy",
  "service": "The 'Thin' S3 Service",
  "version": "1.0.0"
}
```

### Storage Operations

- **List Storage**: `GET /api/storage`
- **Get File**: `GET /api/storage/{file_id}`
- **Delete File**: `DELETE /api/storage/{file_id}`

### Upload Operations

- **Upload File**: `POST /api/upload`
- **Get Upload Status**: `GET /api/upload/{upload_id}`

## Project Structure

```
.
├── app/
│   ├── api/               # API routes and endpoints
│   │   └── endpoints/     # Endpoint implementations
│   ├── core/              # Core configuration and security
│   ├── models/            # Data models and schemas
│   ├── services/          # Business logic (S3, Redis)
│   └── worker/            # Background task definitions
├── tests/                 # Test suite
├── docker-compose.yml     # Docker Compose configuration
├── Dockerfile             # Docker image definition
└── requirements.txt       # Python dependencies
```

## Testing

Run the test suite:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=app
```

## Development

### Adding New Endpoints

1. Create a new endpoint file in `app/api/endpoints/`
2. Define your route functions
3. Include the router in `app/api/router.py`

### Adding New Services

1. Create a new service module in `app/services/`
2. Implement your business logic
3. Import and use in your endpoints

## Troubleshooting

- **Redis Connection Issues**: Ensure Redis is running on `localhost:6379`
- **S3 Credentials**: Verify AWS credentials in environment variables
- **CORS Errors**: Check CORS middleware configuration in `app/main.py`

## License

[Specify your license here]

## Support

For issues and questions, please open an issue on the repository.

