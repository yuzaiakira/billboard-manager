# Billboard Manager

Django-based platform for listing, managing, and reserving outdoor advertising billboards. Supports multi-city catalogs, reseller accounts, Jalali dates, and a Django admin media library for reusing uploaded images.

## Tech stack

| Layer | Choice |
| --- | --- |
| Framework | Django 3.2 |
| Language | Python 3.10 |
| Database | MySQL 8 (SQLite for tests) |
| Calendar | django-jalali / jdatetime |
| Images | Pillow (compressed on save) |
| Deploy | Docker Compose (local), cPanel + Passenger (production) |

## Project layout

```text
├── account/          # Users, companies, auth
├── billboard/        # Catalog, media library, admin
├── addlist/          # Listing / submission flows
├── reservation/      # Reservations
├── siteoption/       # Site-wide options
├── seo/              # SEO base models
├── core/             # Settings, URLs, WSGI/ASGI
├── templates/        # HTML templates
├── static/           # Static assets
├── upload/           # Media files (do not wipe in production)
├── tests/            # Test suite (by app)
├── docker/           # Entrypoint scripts
└── passenger_wsgi.py # cPanel / Passenger entrypoint
```

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose (recommended for local development)
- Or: Python 3.10+, MySQL 8, and system libs for `mysqlclient` / Pillow

## Quick start (Docker)

1. **Configure environment**

   ```bash
   cp sample.env .env
   ```

   Edit `.env` if you need custom secrets, ports, or database credentials.

2. **Build and run**

   ```bash
   docker compose up --build
   ```

3. **Open the app**

   - Site: [http://localhost:8000](http://localhost:8000)
   - Admin: [http://localhost:8000/admin/](http://localhost:8000/admin/)

4. **Create a superuser**

   ```bash
   docker compose exec web python manage.py createsuperuser
   ```

### Useful Compose commands

```bash
# Django shell
docker compose exec web python manage.py shell

# Apply migrations (also run by the entrypoint on start)
docker compose exec web python manage.py migrate

# Stop containers (keeps MySQL volume and data)
docker compose down
```

MySQL is published on host port `3306` (override with `DB_PORT` in `.env`). Inside Compose, Django always connects to the `db` service.

## Environment variables

Copy from `sample.env`. Important keys:

| Variable | Description |
| --- | --- |
| `DJANGO_SECRET_KEY` | Django secret key |
| `DJANGO_DEBUG` | `True` / `False` |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD` | MySQL credentials |
| `DB_HOST`, `DB_PORT` | MySQL host/port (Compose overrides host to `db`) |
| `DB_ROOT_PASSWORD` | MySQL root password for the Compose `db` service |
| `WEB_PORT` | Host port for the web app (default `8000`) |
| `BASE_SITE_URL` | Optional URL prefix (e.g. `/billboard`) |

## Features

### Admin media library

In the billboard admin change form, image fields (`billboard_pic` and gallery images) include **انتخاب از کتابخانه**:

- Browse previously uploaded images (search + pagination) and reuse them without re-uploading.
- Admins see all images; resellers only see images from their own billboards.
- New uploads still work as before (compressed on save). Selecting from the library only stores the existing relative path — no duplicate file and no nested date paths.

No database schema change is required for this feature.

### Repair nested image paths

Older saves sometimes stored nested paths like:

```text
billboard/2026/10/11/billboard/2026/10/04/photo.jpg
```

After deploying the fix, repair DB path strings safely (files are not deleted; schema is unchanged):

```bash
# Preview
docker compose exec web python manage.py repair_nested_billboard_paths --dry-run

# Apply
docker compose exec web python manage.py repair_nested_billboard_paths
```

On production (cPanel), run the same `manage.py` commands after uploading the new code.

## Testing

Tests live under `tests/` and use SQLite via `core.test_settings` (no MySQL required). Coverage for application packages must stay at or above **90%** (see `.coveragerc`).

### Local

```bash
pip install -r requirements-dev.txt
DJANGO_SETTINGS_MODULE=core.test_settings coverage run manage.py test tests -v 2
coverage report -m
```

### Docker

```bash
docker compose run --rm --no-deps --entrypoint bash \
  -e DJANGO_SETTINGS_MODULE=core.test_settings web \
  -c "pip install -q coverage && coverage run manage.py test tests -v 2 && coverage report -m"
```

## Production (cPanel)

This project is deployed on **cPanel** with Passenger (`passenger_wsgi.py`).

**Data safety — do not:**

- Flush or reset the production database
- Delete Docker volumes / MySQL data as part of an update
- Overwrite production `.env` or wipe `upload/` media unless explicitly intended

**Safe update flow:**

1. Upload / pull the new code.
2. Install dependencies if needed.
3. Run migrations: `python manage.py migrate`
4. Run maintenance commands only when documented (e.g. `repair_nested_billboard_paths`).
5. Restart the Passenger / Python app.

Keep existing MySQL data, `.env`, and `upload/` intact across deploys.

## License

Proprietary — internal use for Anten Billboard Manager.
