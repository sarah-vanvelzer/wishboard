import numpy as np
import psycopg
from pgvector.psycopg import register_vector

import random

from sklearn.cluster import KMeans

from app.pinterest import parse_export

from app.db import DATABASE_URL

def load_embeddings():
    with psycopg.connect(DATABASE_URL) as conn:
        register_vector(conn)
        rows = conn.execute(
            "SELECT source_id, embedding FROM pins WHERE embedding IS NOT NULL"
        ).fetchall()
    ids = [row[0] for row in rows]
    matrix = np.stack([row[1].to_numpy() for row in rows])
    return ids, matrix

def run_kmeans(matrix, k=20):
    normed = matrix / np.linalg.norm(matrix, axis=1, keepdims=True)
    km = KMeans(n_clusters=k, random_state=42, n_init="auto")
    return km.fit_predict(normed)

def write_gallery(ids, labels, path="data/gallery.html", per_cluster=12):
    pins = {p.source_id: p for p in parse_export("data/pinterest_export/pins")}
    random.seed(0)
    html = ["<html><body style='font-family:sans-serif'>"]
    for c in sorted(set(labels)):
        members = [i for i, l in zip(ids, labels) if l == c]
        html.append(f"<h2>Cluster {c} ({len(members)} pins)</h2>")
        for i in random.sample(members, min(per_cluster, len(members))):
            html.append(f"<img src='{pins[i].image_url}' height='150'>")
    html.append("</body></html>")
    open(path, "w").write("\n".join(html))

if __name__ == "__main__":
    ids, matrix = load_embeddings()
    labels = run_kmeans(matrix)
    write_gallery(ids, labels)
    print("wrote data/gallery.html")