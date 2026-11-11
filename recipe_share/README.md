# RecipeShare

## Requirements
- Python 3.11+
- MySQL 8+

## Setup on Windows
```powershell
cd recipe_share
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
flask --app app run
```

## Tests
```powershell
python -m pytest
```

Configuration values are loaded from environment variables. Do not commit real secrets or database credentials.

## Database setup
1. Start MySQL 8 as an administrator or ask an administrator to start the MySQL80 service.
2. Create a dedicated database account, for example a MySQL user with access only to `recipeshare`.
3. Set `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, and `MYSQL_DATABASE` in `.env`.
4. Apply the schema and optional seed data:

```powershell
python database/migrate.py
python database/migrate.py --seed
```

The canonical schema is [database/schema.sql](database/schema.sql). Migration 001 mirrors this initial schema and seed data is kept separate from production schema setup.
