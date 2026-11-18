# Wishboard

Turns years of saved Pinterest pins into a ranked list of interests and a Christmas gift list with real, findable products.

Built with Python, PostgreSQL + pgvector, CLIP, scikit-learn and the Gemini API.

## Why

A Pinterest board says a lot about what someone loves, but nobody is going to scroll through 20,000 pins to pick a gift. Wishboard looks at all of them, groups them into themes, works out which themes are actually giftable, and finds specific products for the best ones.

## How it works

```
Pinterest export → parse → Postgres → CLIP image embeddings (pgvector)
                                              ↓
                                     K-means → 20 themes
                                              ↓
                      Gemini names + scores each theme → ranked themes
                                              ↓
          gift agent: plan searches → web search → suggest products → verify
```

1. **Parse the export.** Pinterest's data export is a set of HTML pages. `pinterest.py` splits them into pins, pulls out the title, description, board and image hash, rebuilds each image URL, and fills in missing board names from board IDs. About 22,900 unique pins are saved to Postgres.
2. **Embed the images.** Each pin image is turned into a 512-number vector with CLIP (`clip-ViT-B-32`), run on the Apple Silicon GPU. Images download on a 16-thread pool, which made embedding about 10x faster. Work happens in chunks of 500 and skips pins that are already done, so it can be stopped and restarted.
3. **Find themes.** The vectors are normalized and grouped into 20 clusters with K-means.
4. **Name and rank them.** For each cluster, Gemini reads a sample of 40 pins and returns structured JSON: a 2–4 word interest name, a 0–10 "giftability" score (how easy it is to buy a physical gift for it) and a one-line reason. Themes are ranked by `sqrt(size) × giftability`, so a big theme matters more without completely drowning out smaller, very giftable ones.
5. **Find gifts.** A small agent takes a top theme and:
   - asks Gemini to plan 2 search queries,
   - searches the web (DuckDuckGo) and filters out ads,
   - asks Gemini for 3 specific brand-name products based on what it found,
   - searches for each product again and drops any it can't find, so it never suggests something made up.

Gemini calls use Pydantic schemas for structured output and retry with exponential backoff when the API is busy (429/500/503).

## Project structure

| File | What it does |
|---|---|
| `app/pinterest.py` | Parses the Pinterest export into `Pin` objects |
| `app/schemas.py` | Pydantic `Pin` model |
| `app/db.py` | Saves pins and embeddings to Postgres |
| `app/embed.py`, `app/embed_all.py` | CLIP embeddings with parallel downloads, in resumable chunks |
| `app/cluster.py` | K-means clustering, plus an HTML gallery to eyeball each cluster |
| `app/naming.py` | Gemini client, retries, theme naming and giftability scoring |
| `app/build_themes.py` | Clusters, names, scores and saves the ranked themes |
| `app/agent.py` | The gift-finding agent (`find_gifts(theme, reason)`) |
| `app/main.py` | FastAPI app (health check so far) |
| `db/` | SQL schema and migrations (pins, pgvector column, themes) |

## Setup

You need Python 3.12, PostgreSQL with the [pgvector](https://github.com/pgvector/pgvector) extension, and a Gemini API key.

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create the database (the code expects `postgresql://localhost:5433/wishboard`) and run the SQL files in order:

```bash
createdb -p 5433 wishboard
psql -p 5433 wishboard -f db/schema.sql
psql -p 5433 wishboard -f db/002_add_embeddings.sql
psql -p 5433 wishboard -f db/003_add_themes.sql
```

Add your key to a `.env` file in the project root:

```
GEMINI_API_KEY=your-key-here
```

Request your data from Pinterest (Settings → Privacy and data → Request your data) and put the pin pages in `data/pinterest_export/pins/`. The `data/` folder is gitignored, so your pins stay on your machine.

## Run it

```bash
python -m app.embed_all       # embed every pin image with CLIP
python -m app.cluster         # optional: writes data/gallery.html to check the clusters
python -m app.build_themes    # name, score and rank the themes
```

Then call `find_gifts(theme_name, reason)` from `app/agent.py` with one of the top themes.

`embed.py` uses `device="mps"` (Apple Silicon). On other machines, change it to `"cuda"` or `"cpu"`.

## What's next

- API routes and a simple front end to browse themes and gifts
- Support for more sources than Pinterest