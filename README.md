# Django Billboard manager

## Run with Docker

1. Copy env file and set values if needed:

```bash
cp sample.env .env
```

2. Build and start:

```bash
docker compose up --build
```

3. Open the app: [http://localhost:8000](http://localhost:8000)

Useful commands:

```bash
# Create admin user
docker compose exec web python manage.py createsuperuser

# Shell
docker compose exec web python manage.py shell

# Stop
docker compose down
```

MySQL is available on host port `3306` (configurable via `DB_PORT` in `.env`).
Inside Docker, Django always connects to the `db` service.
