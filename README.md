# Movie Recommendation API

FastAPI backend for content-based movie recommendations with rating adjustment and optional TMDb enrichment.

## What Improved

- Moved from a single-file app to a modular folder structure (`app/core`, `app/services`, `app/api`, `app/schemas`).
- Removed hardcoded TMDb API key from source code.
- Added environment-based configuration via `.env`/environment variables.
- Added request limits and validation (`num_recommendations >= 1`, max clamp from config).
- Added HTTP timeout for TMDb calls to reduce hanging external requests.

## Project Structure

```text
ml-movie-recommendation-api/
├── app/
│   ├── api/
│   │   └── routes.py
│   ├── core/
│   │   └── config.py
│   ├── schemas/
│   │   └── recommendation.py
│   ├── services/
│   │   ├── recommender.py
│   │   └── tmdb.py
│   └── main.py
├── .env.example
├── main.py
└── README.md
```

## Setup

1. Create and activate a virtual environment.
1. Install dependencies:

```bash
pip install fastapi uvicorn pandas scikit-learn requests pydantic
```

1. Add dataset files in the project root (or set `DATA_DIR`):

- `movies.csv`
- `ratings.csv`
- `links.csv`

1. Configure environment variables:

```bash
copy .env.example .env
```

Set values in `.env`:

- `TMDB_API_KEY` (optional, but recommended for overview/poster metadata)
- `ALLOWED_ORIGINS` (comma-separated)
- `SAMPLE_SIZE`
- `MAX_RECOMMENDATIONS`
- `DATA_DIR`

## Run

```bash
uvicorn main:app --reload
```

Server: `http://127.0.0.1:8000`
Swagger docs: `http://127.0.0.1:8000/docs`

## Endpoint

`POST /recommend`

Request body:

```json
{
  "title": "Toy Story",
  "num_recommendations": 5
}
```

Responses:

- `200`: Recommendations returned
- `404`: Movie title not found in dataset

## Security Notes

- Do not commit `.env`.
- Rotate your TMDb key if it was exposed previously.
- Keep `ALLOWED_ORIGINS` restricted to trusted frontends.
