import json
import math
import time
from collections import defaultdict

import psycopg

from app.cluster import load_embeddings, run_kmeans
from app.db import DATABASE_URL
from app.naming import name_cluster
from app.pinterest import parse_export


def main():
    ids, matrix = load_embeddings()
    labels = [int(l) for l in run_kmeans(matrix)]
    pins = {p.source_id: p for p in parse_export("data/pinterest_export/pins")}

    groups = defaultdict(list)
    for i, l in zip(ids, labels):
        groups[l].append(pins[i])

    themes = []
    for c in sorted(groups):
        members = groups[c]
        info = json.loads(name_cluster(members))
        score = math.sqrt(len(members)) * info["giftability"]
        themes.append((c, info["name"], info["giftability"], info["reason"], len(members), score))
        print(c, len(members), info["name"], info["giftability"])
        time.sleep(4)

    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.executemany(
                "UPDATE pins SET cluster = %s WHERE source = 'pinterest' AND source_id = %s",
                list(zip(labels, ids)),
            )
            cur.execute("DELETE FROM themes")
            cur.executemany(
                "INSERT INTO themes (cluster, name, giftability, reason, size, score) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                themes,
            )

    print("\nTop themes:")
    for t in sorted(themes, key=lambda t: t[5], reverse=True)[:10]:
        print(f"{t[5]:.0f}  {t[1]} ({t[4]} pins, giftability {t[2]})")


if __name__ == "__main__":
    main()