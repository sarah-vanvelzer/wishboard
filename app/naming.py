import os
import random

import truststore
truststore.inject_into_ssl()

from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"], http_options={"timeout": 30000})
MODEL = "gemini-3.5-flash-lite"

def cluster_text(member_pins, n=40):
    random.seed(0)
    sample = random.sample(member_pins, min(n, len(member_pins)))
    lines = []
    for p in sample:
        parts = [p.board, p.title, p.description]
        lines.append("- " + " | ".join(x for x in parts if x))
    return "\n".join(lines)

def name_cluster(member_pins):
    prompt = f"""These pins are one group from someone's Pinterest.
Each line is: board | title | description (some parts may be missing).

{cluster_text(member_pins)}

Reply in JSON with exactly these keys:
"name": a 2 to 4 word theme name,
"giftability": a number from 0 to 10 for how easy it is to buy a Christmas gift for this theme,
"reason": one short sentence explaining the score."""
    resp = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config={"response_mime_type": "application/json"},
    )
    return resp.text