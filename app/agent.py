import json

from ddgs import DDGS
from pydantic import BaseModel
from ddgs.exceptions import DDGSException

from app.naming import call_gemini

class Queries(BaseModel):
    queries: list[str]

class Gift(BaseModel):
    name: str
    why: str
    price: str
    link: str

class GiftList(BaseModel):
    gifts: list[Gift]

class Idea(BaseModel):
    name: str
    why: str

class IdeaList(BaseModel):
    ideas: list[Idea]

def plan_queries(theme_name, reason):
    prompt = f"""You are shopping for a Christmas gift for a young woman whose Pinterest shows a strong interest in: {theme_name} ({reason}).
Write 2 short web search queries (plain keywords, no quotes or special characters) that would find specific gift products for this interest."""
    return json.loads(call_gemini(prompt, schema=Queries))["queries"]

def search(query, n=5, attempts=3):
    for attempt in range(attempts):
        try:
            results = DDGS().text(query, max_results=n)
            return [r for r in results if "bing.com/aclick" not in r["href"]]
        except DDGSException as e:
            wait = 5 * 2 ** attempt
            print(f"search failed for {query!r} ({e}), retrying in {wait}s")
            time.sleep(wait)
    return []

def suggest_products(theme_name, results):
    lines = "\n".join(f"- {r['title']} | {r['body'][:200]}" for r in results)
    prompt = f"""Interest: {theme_name}
Gift guide search results:
{lines}

Suggest 3 SPECIFIC products as Christmas gifts for this interest, ideally ones mentioned above.
Each "name" must be a real brand + product name (e.g. "Garmin Forerunner 165", "Lululemon Align Leggings"), never a category like "running gear".
"why": one sentence on why it fits."""
    return json.loads(call_gemini(prompt, schema=IdeaList))["ideas"]


def verify_product(name):
    results = search(name, n=3)
    if not results:
        return None
    top = results[0]
    return {"link": top["href"], "source": top["title"]}


def find_gifts(theme_name, reason):
    queries = plan_queries(theme_name, reason)
    results = []
    for q in queries:
        results.extend(search(q))
    print("queries:", queries, "| results:", len(results))
    if not results:
        return queries, []
    gifts = []
    for idea in suggest_products(theme_name, results):
        found = verify_product(idea["name"])
        if found:
            gifts.append({**idea, **found})
        else:
            print("dropped (not found):", idea["name"])
    return queries, gifts