import psycopg
from fastapi import FastAPI
from psycopg.rows import dict_row
from fastapi.responses import FileResponse

from app.db import DATABASE_URL

app = FastAPI()

@app.get("/")
def home():
    return FileResponse("app/static/index.html")

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/themes")
def list_themes():
    # taking dict_row makes each row come back as a dictionary
    # fastAPI turns dictionaries into straight JSON
    with psycopg.connect(DATABASE_URL, row_factory=dict_row) as conn:
        return conn.execute(
            "SELECT id, name, giftability, reason, size, score FROM themes ORDER BY score DESC"
        ).fetchall()


@app.get("/wishlist")
def wishlist():
    with psycopg.connect(DATABASE_URL, row_factory=dict_row) as conn:
        # Combine the two tables (matching theme_id to theme's id)
        rows = conn.execute("""
            SELECT t.id AS theme_id, t.name AS theme, g.name, g.why, g.link
            FROM gifts g
            JOIN themes t ON t.id = g.theme_id
            ORDER BY t.score DESC
        """).fetchall()
    grouped = {}
    for r in rows:
        theme = grouped.setdefault(r["theme_id"], {"theme": r["theme"], "gifts": []})
        theme["gifts"].append({"name": r["name"], "why": r["why"], "link": r["link"]})
    return list(grouped.values())