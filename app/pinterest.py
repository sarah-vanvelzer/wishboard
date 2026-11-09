def image_url_from_hash(h: str) -> str:
    return f"https://i.pinimg.com/736x/{h[0:2]}/{h[2:4]}/{h[4:6]}/{h}.jpg"

def get_field(chunk: str, label: str) -> str:
    value = chunk.split(label + ": ")[1].split('<br>')[0].strip()
    if value == "No data":
        return ""
    return value