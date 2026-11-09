from pydantic import BaseModel

class Pin(BaseModel):
    source: str
    source_id: str
    title: str = ""
    board: str = ""
    board_id: str = ""
    image_url: str | None = None
    link: str | None = None