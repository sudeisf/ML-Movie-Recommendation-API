# Movie Recommendation System — FastAPI Backend

A content-based and rating-adjusted movie recommendation API built with **FastAPI**. Given a movie title, it returns similar movies enriched with metadata (overview, poster) fetched from the [TMDb API](https://www.themoviedb.org/documentation/api).

---

## Features

- **Content-based filtering** — uses TF-IDF vectorization on movie titles and genres, combined with cosine similarity to find similar movies.
- **Rating adjustment** — blends cosine similarity scores with average user ratings (50 / 50 weight) so popular, well-rated films surface higher.
- **TMDb metadata enrichment** — each recommendation is augmented with a synopsis and poster image via the TMDb REST API.
- **CORS support** — pre-configured to accept requests from a local React/Vite front-end (`http://localhost:5173`).

---

## Tech Stack

| Layer | Technology |
|---|---|
| Web framework | [FastAPI](https://fastapi.tiangolo.com/) |
| Data processing | [pandas](https://pandas.pydata.org/), [scikit-learn](https://scikit-learn.org/) |
| Similarity | TF-IDF + Cosine Similarity |
| External API | [TMDb API](https://www.themoviedb.org/documentation/api) |
| HTTP client | [requests](https://docs.python-requests.org/) |
| Validation | [Pydantic](https://docs.pydantic.dev/) |

---

## Prerequisites

- Python 3.9+
- A [TMDb API key](https://www.themoviedb.org/settings/api)
- The following CSV dataset files placed in the project root:
  - `movies.csv` — columns: `movieId`, `title`, `genres`
  - `ratings.csv` — columns: `userId`, `movieId`, `rating`, `timestamp`
  - `links.csv` — columns: `movieId`, `imdbId`, `tmdbId`

  These files are excluded from version control (`.gitignore`). You can obtain them from the [MovieLens dataset](https://grouplens.org/datasets/movielens/).

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/sudeisf/movie_recommendation_system_backend_with_fastapi.git
cd movie_recommendation_system_backend_with_fastapi

# 2. Create and activate a virtual environment
python -m venv myenv
source myenv/bin/activate   # Windows: myenv\Scripts\activate

# 3. Install dependencies
pip install fastapi uvicorn pandas scikit-learn requests pydantic
```

---

## Configuration

Open `main.py` and replace the placeholder API key with your own TMDb key:

```python
TMDB_API_KEY = "your_tmdb_api_key_here"
```

> **Tip:** For production use, store the key in a `.env` file and load it with `python-dotenv` to avoid committing secrets to source control.

---

## Running the Server

```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

Interactive docs (Swagger UI) are served automatically at `http://127.0.0.1:8000/docs`.

---

## API Reference

### `POST /recommend/`

Returns a list of recommended movies based on the provided title.

#### Request Body

```json
{
  "title": "Toy Story",
  "num_recommendations": 5
}
```

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `title` | `string` | ✅ | — | Title of the reference movie |
| `num_recommendations` | `integer` | ❌ | `5` | Number of movies to return |

#### Success Response — `200 OK`

```json
{
  "recommendations": [
    {
      "title": "A Bug's Life",
      "genres": "Animation Children Comedy",
      "overview": "On behalf of the colony, ...",
      "poster": "https://image.tmdb.org/t/p/w500/qlqLeHmJOiQVfj2rdqHFgFiMDSL.jpg"
    }
  ]
}
```

#### Error Responses

| Status | Condition |
|---|---|
| `400 Bad Request` | Movie title not found in the dataset |
| `500 Internal Server Error` | Unexpected processing error |

#### Example with `curl`

```bash
curl -X POST "http://127.0.0.1:8000/recommend/" \
  -H "Content-Type: application/json" \
  -d '{"title": "Toy Story", "num_recommendations": 5}'
```

---

## Project Structure

```
movie_recommendation_system_backend_with_fastapi/
├── main.py          # FastAPI application, recommendation logic, TMDb integration
├── movies.csv       # Movie metadata (gitignored — add your own)
├── ratings.csv      # User ratings (gitignored — add your own)
├── links.csv        # MovieLens ↔ TMDb ID mapping (gitignored — add your own)
├── .gitignore
└── README.md
```

---

## How It Works

1. On startup, the first 1,000 rows of `movies.csv` and `ratings.csv` are loaded.
2. Movie genres are joined with their titles to form a combined feature string.
3. TF-IDF vectorization converts those strings into numerical feature vectors.
4. Cosine similarity is computed across all movie pairs.
5. When a request arrives, the top-N most similar movies are retrieved.
6. Each candidate's final score is a 50/50 blend of its cosine similarity and its average user rating.
7. TMDb is queried for each recommended movie to fetch an overview and poster URL.

---

## License

This project is open-source. Feel free to fork and extend it.
