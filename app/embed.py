import io
import urllib.request

import truststore
truststore.inject_into_ssl()

from PIL import Image
from sentence_transformers import SentenceTransformer

from app.schemas import Pin

from concurrent.futures import ThreadPoolExecutor

model = SentenceTransformer("clip-ViT-B-32", device="mps")

def load_image(url: str) -> Image.Image:
    data = urllib.request.urlopen(url, timeout=10).read()
    return Image.open(io.BytesIO(data)).convert("RGB")

def try_load(p: Pin):
    try:
        return p.source_id, load_image(p.image_url)
    except Exception as e:
        print(f"skipped {p.source_id}: {e}")
        return None

def embed_pins(pins: list[Pin]):
    with_images = [p for p in pins if p.image_url]
    with ThreadPoolExecutor(max_workers=16) as pool:
        results = [r for r in pool.map(try_load, with_images) if r is not None]
    ids = [pin_id for pin_id, _ in results]
    images = [img for _, img in results]
    vectors = model.encode(images, batch_size=32)
    return ids, vectors