import psycopg

from app.schemas import Pin

from pgvector.psycopg import register_vector

DATABASE_URL = "postgresql://localhost:5433/wishboard"

INSERT_PIN = """
    INSERT INTO pins (source, source_id, title, description, board, board_id, image_url, link)
    VALUES (%(source)s, %(source_id)s, %(title)s, %(description)s, %(board)s, %(board_id)s, %(image_url)s, %(link)s)
    ON CONFLICT (source, source_id) DO NOTHING
"""

def save_pins(pins: list[Pin]) -> None:
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.executemany(INSERT_PIN, [p.model_dump() for p in pins])

def save_embeddings(ids, vectors) -> None:
    with psycopg.connect(DATABASE_URL) as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            cur.executemany(
                "UPDATE pins SET embedding = %s WHERE source = 'pinterest' AND source_id = %s",
                list(zip(vectors, ids)),
            )