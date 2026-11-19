# Wishboard 🎄

Turns 22,000+ saved Pinterest pins into themes and a ranked Christmas gift list,
using CLIP embeddings, clustering, and an LLM agent.

## How it works
1. **Parse**: reads the Pinterest data export (HTML) into a shared `Pin` format
2. **Store**: saves pins to PostgreSQL (deduplicated with a UNIQUE constraint)
3. **Embed**: CLIP turns each pin's image into a 512-d vector, stored with pgvector
4. **Cluster**: k-means groups similar pins into 20 themes
5. **Name & rank**: Gemini names each theme and scores how giftable it is (structured output)
6. **Find gifts**: an agent plans searches, suggests specific products, and verifies them with web search
7. **Serve**: FastAPI exposes `/themes` and `/wishlist`, plus a simple web page

## Results
- **22,911** unique pins parsed (6 duplicates removed automatically)
- **99%** of 6,913 missing board labels recovered by joining on board IDs
- **22,874** pins embedded (99.8%)
- Embedding time cut from **~6 hours to 32 minutes** (GPU inference + parallel downloads)

## Tech stack
Python, FastAPI, PostgreSQL, pgvector, CLIP (sentence-transformers), scikit-learn,
Gemini API, DuckDuckGo search

## Engineering notes
- Resumable batch jobs (chunked, skip already-processed rows)
- Retry with exponential backoff for temporary API errors; fail fast on permanent ones
- Request throttling for the search API
- LLM outputs validated with Pydantic schemas; agent links verified against real search results

## Known limitations / next steps
- Some gift links point to category or article pages; next: check links load and look like product pages
- Prefer Canadian retailers
- Docker, cloud deployment and CI