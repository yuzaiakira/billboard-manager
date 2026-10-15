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

## Admin media library

In the billboard admin change form, image fields (`billboard_pic` and gallery images) include **انتخاب از کتابخانه**.

- Browse previously uploaded images (search + pagination) and reuse them without re-uploading.
- Admins see all images; resellers only see images from their own billboards.
- New uploads still work as before (compressed on save). Selecting from the library only stores the existing relative path — no duplicate file and no nested date paths.

No database schema change is required for this feature.

## Repair nested image paths

Older saves sometimes stored nested paths like:

`billboard/2026/10/11/billboard/2026/10/04/photo.jpg`

After deploying the code, repair DB path strings safely (files are not deleted; schema is unchanged):

```bash
# Preview
docker compose exec web python manage.py repair_nested_billboard_paths --dry-run

# Apply (local or production after deploy)
docker compose exec web python manage.py repair_nested_billboard_paths
```

On production (cPanel), run the same `manage.py` commands after uploading the new code. Do not flush the database or wipe `upload/` media.
