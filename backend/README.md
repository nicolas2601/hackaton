# Backend - Manufactura Santander 4.0

Django backend for the Manufactura Santander 4.0 IoT platform.

## Quick Start

```bash
# Install dependencies
uv sync

# Run migrations
uv run python manage.py makemigrations
uv run python manage.py migrate

# Create superuser
uv run python manage.py createsuperuser

# Run development server
uv run python manage.py runserver

# Run MQTT worker (in separate terminal)
uv run python manage.py mqtt_worker
```

## Docker Development

```bash
# Start all services
docker compose up -d

# Run migrations
docker compose exec backend python manage.py migrate

# Create superuser
docker compose exec backend python manage.py createsuperuser

# View logs
docker compose logs -f backend
```

## API Endpoints

- `POST /api/auth/token/` - Obtain JWT token
- `POST /api/auth/token/refresh/` - Refresh JWT token
- `GET /api/production/lines/` - List production lines
- `GET /api/production/machines/` - List machines
- `GET /api/telemetry/events/` - List telemetry events
- `GET /api/analytics/oee/` - Get OEE metrics

## Documentation

API documentation available at `/api/docs/` (Swagger UI).