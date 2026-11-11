import os
import random
import time
from google.genai import errors

import truststore
truststore.inject_into_ssl()

from dotenv import load_dotenv
from google import genai

from pydantic import BaseModel

class ThemeInfo(BaseModel):
    name: str
    giftability: int
    reason: str

load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"], http_options={"timeout": 30000})
MODEL = "gemini-3.5-flash-lite"

def cluster_text(member_pins, n=40):
    random.seed(0)
    sample = random.sample(member_pins, min(n, len(member_pins)))
    lines = []
    for p in sample:
        parts = [p.board, p.title, p.description[:150]]
        lines.append("- " + " | ".join(x for x in parts if x))
    return "\n".join(lines)

def call_gemini(prompt, schema=None, attempts=5):
    config = {"response_mime_type": "application/json"}
    if schema:
        config["response_schema"] = schema
    for attempt in range(attempts):
        try:
            resp = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config=config,
            )
            return resp.text
        except errors.APIError as e:
            if e.code not in (429, 500, 503):
                raise
            wait = 5 * 2 ** attempt
            print(f"Gemini busy ({e.code}), retrying in {wait}s")
            time.sleep(wait)
    raise RuntimeError("Gemini still unavailable after retries")


def name_cluster(member_pins):
    prompt = f"""These pins are one group from someone's Pinterest.
Each line is: board | title | description (some parts may be missing).

{cluster_text(member_pins)}

Reply in JSON with exactly these keys:
"name": a 2 to 4 word name for the INTEREST (e.g. "Trail Running", not "Runner Girl"),
"giftability": 0 to 10, how easy it is to buy a physical Christmas gift for this theme,
"reason": one short sentence explaining the score.

Scoring guide (be strict, most themes should NOT score above 7):
0-3: hard to buy for (quotes, memes, mindset, career goals, places to visit)
4-6: possible but vague (general aesthetic, lifestyle)
7-10: clear products to buy (sports gear, clothing, jewelry, home decor, books)"""
    return call_gemini(prompt, schema=ThemeInfo)