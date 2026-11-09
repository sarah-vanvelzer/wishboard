from pathlib import Path
from app.schemas import Pin

def image_url_from_hash(h: str) -> str:
    return f"https://i.pinimg.com/736x/{h[0:2]}/{h[2:4]}/{h[4:6]}/{h}.jpg"

def get_field(chunk: str, label: str) -> str:
    if label + ": " not in chunk:
        return ""
    value = chunk.split(label + ": ")[1].split('<br>')[0].strip()
    if value == "No data":
        return ""
    return value

def parse_chunk(chunk: str) -> Pin:
    image_hash = get_field(chunk, "Image")
    return Pin(
        source="pinterest",
        source_id=chunk.split('/')[0],
        title=get_field(chunk, "Title"),
        description=get_field(chunk, "Details"),
        board=get_field(chunk, "Board Name"),
        image_url=image_url_from_hash(image_hash) if image_hash else None,
    )

def parse_file(path: str) -> list[Pin]:
    t = open(path).read()
    chunks = t.split('<a href="https://www.pinterest.com/pin/')
    pins = [parse_chunk(c) for c in chunks[1:]]
    return pins

def parse_export(folder: str) -> list[Pin]:
    all_pins = []
    for path in sorted(Path(folder).glob("0*.html")):
        all_pins.extend(parse_file(path))
    return all_pins