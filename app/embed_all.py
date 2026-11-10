import time

import psycopg

from app.db import DATABASE_URL, save_embeddings
from app.embed import embed_pins
from app.pinterest import parse_export

CHUNK = 500

def main():
    pins = parse_export("data/pinterest_export/pins")

    with psycopg.connect(DATABASE_URL) as conn:
        rows = conn.execute("SELECT source_id FROM pins WHERE embedding IS NOT NULL")
        done = {row[0] for row in rows}

    todo = [p for p in pins if p.image_url and p.source_id not in done]
    print(f"{len(done)} already embedded, {len(todo)} to go")

    start = time.time()
    for i in range(0, len(todo), CHUNK): # increases by 500
        chunk = todo[i : i + CHUNK]
        ids, vectors = embed_pins(chunk)
        save_embeddings(ids, vectors)
        print(f"{i + len(chunk)}/{len(todo)} done, {time.time() - start:.0f}s elapsed")

if __name__ == "__main__":
    main()