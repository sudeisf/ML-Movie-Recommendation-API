from fastapi import FastAPI, HTTPException 
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import requests
import re


# TMDb API Key
TMDB_API_KEY = "62ce4c7067003545ab65a6e6d40c948c"

# Load datasets and sample the first 1000 rows (no randomization)
movies = pd.read_csv("movies.csv").iloc[:1000]  # Take the first 1000 rows
ratings = pd.read_csv("ratings.csv").iloc[:1000]  # Take the first 1000 rows
links = pd.read_csv("links.csv")

# Preprocess genres for content-based filtering
movies["genres"] = movies["genres"].str.replace("|", " ")  # Convert genre separators to spaces
movies["title_genres"] = movies["title"] + " " + movies["genres"]  # Combine title and genres for similarity

# Calculate average ratings for each movie
avg_ratings = ratings.groupby('movieId')['rating'].mean()

# Merge the average ratings with the movies dataframe
movies['avg_rating'] = movies['movieId'].map(avg_ratings)

# Vectorize title and genres using TF-IDF
vectorizer = TfidfVectorizer(stop_words="english")
tfidf_matrix = vectorizer.fit_transform(movies["title_genres"])

# Compute similarity scores
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)


# Helper function to get movie index from title, ignoring the year in parentheses
def get_movie_index(title):
    title = re.sub(r"\(\d{4}\)", "", title).strip()  # Remove the year (e.g., (1995)) and strip spaces
    title = title.lower().strip()  # Make the title lowercase and strip extra spaces
    # Search for a movie by title (case-insensitive)
    matching_movies = movies[movies["title"].str.contains(title, case=False, na=False, regex=False)]
    if not matching_movies.empty:
        return matching_movies.index[0]
    return None

# Recommendation function with rating consideration
def recommend_movies(title, num_recommendations=10):
    idx = get_movie_index(title)
    if idx is None:
        print(f"No movie found with title '{title}'")
        return pd.DataFrame()  # Return an empty DataFrame if no movie found
    
    # Get similarity scores for the given movie
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    # Get top movie indices (excluding the movie itself)
    top_indices = [i[0] for i in sim_scores[1:num_recommendations + 1]]
    
    # Adjust recommendations based on average ratings
    recommended_movies = movies.iloc[top_indices].copy()  # Create a copy to avoid warning
    recommended_movies['adjusted_score'] = (
        recommended_movies['avg_rating'] * 0.5 +
        recommended_movies['title_genres'].apply(lambda x: cosine_sim[idx][get_movie_index(x)] if get_movie_index(x) is not None else 0) * 0.5
    )
    
    # Sort by adjusted score
    recommended_movies = recommended_movies.sort_values(by='adjusted_score', ascending=False)
    
    return recommended_movies

# Fetch metadata from TMDb
def fetch_metadata(movie_id):
    tmdb_id = links[links["movieId"] == movie_id]["tmdbId"].values
    if len(tmdb_id) == 0:
        return None
    url = f"https://api.themoviedb.org/3/movie/{int(tmdb_id[0])}?api_key={TMDB_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

# FastAPI app initialization
app = FastAPI()


origins = [
    "http://localhost:5173",  # React app's URL
]

# Add CORSMiddleware to handle cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Pydantic model for movie recommendation request
class MovieRequest(BaseModel):
    title: str
    num_recommendations: int = 5

@app.post("/recommend/")
def get_movie_recommendations(request: MovieRequest):
    try:
        recommendations = recommend_movies(request.title, request.num_recommendations)
        if recommendations.empty:
            raise HTTPException(status_code=400, detail=f"No recommendations found for '{request.title}'")

        results = []
        for _, row in recommendations.iterrows():
            metadata = fetch_metadata(row["movieId"])
            if metadata:
                results.append({
                    "title": metadata['title'],
                    "genres": row['genres'],
                    "overview": metadata['overview'],
                    "poster": f"https://image.tmdb.org/t/p/w500{metadata['poster_path']}"
                })
        return {"recommendations": results}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
