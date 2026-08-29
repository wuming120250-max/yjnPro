import os
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

import psycopg

ROOT = Path(__file__).resolve().parents[2]
env_path = ROOT / ".env"
if env_path.exists():
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())

raw_url = os.environ.get("DATABASE_URL")
if not raw_url:
    raise SystemExit("Missing DATABASE_URL. Copy .env.example to .env and fill it in first.")

raw_url = raw_url.replace("postgresql+psycopg://", "postgresql://", 1)
parts = urlsplit(raw_url)
admin_url = urlunsplit((parts.scheme, parts.netloc, "/postgres", parts.query, parts.fragment))
db_name = parts.path.lstrip("/") or "yanjiangnan_ai"

conn = psycopg.connect(admin_url, connect_timeout=5, autocommit=True)
print(conn.execute("select version()").fetchone()[0])
exists = conn.execute(
    "select datname from pg_database where datname = %s",
    (db_name,),
).fetchone()
print("db_exists", bool(exists))
if not exists:
    conn.execute(f'create database "{db_name}"')
    print(f"created {db_name}")
conn.close()
print("ok")
