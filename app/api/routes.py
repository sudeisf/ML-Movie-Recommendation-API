from fastapi import APIRouter, HTTPException

from app.core.config import settings
from app.schemas.recommendation import MovieRequest, RecommendationItem, RecommendationResponse
from app.services.recommender import MovieRecommender
from app.services.tmdb import TMDbClient

router = APIRouter()

recommender = MovieRecommender(data_dir=settings.data_dir, sample_size=settings.sample_size)
tmdb_client = TMDbClient(api_key=settings.tmdb_api_key)


@router.post("/recommend", response_model=RecommendationResponse)
def get_movie_recommendations(request: MovieRequest) -> RecommendationResponse:
    num_recommendations = min(request.num_recommendations, settings.max_recommendations)
    recommendations = recommender.recommend_movies(request.title, num_recommendations)

    if recommendations.empty:
        raise HTTPException(status_code=404, detail=f"No recommendations found for '{request.title}'")

    results: list[RecommendationItem] = []

    for _, row in recommendations.iterrows():
        tmdb_row = recommender.links[recommender.links["movieId"] == row["movieId"]]["tmdbId"]
        metadata = None
        if not tmdb_row.empty:
            metadata = tmdb_client.fetch_metadata(int(tmdb_row.iloc[0]))

        results.append(
            RecommendationItem(
                title=metadata.get("title", row["title"]) if metadata else row["title"],
                genres=row["genres"],
                overview=metadata.get("overview") if metadata else None,
                poster=(
                    f"https://image.tmdb.org/t/p/w500{metadata.get('poster_path')}"
                    if metadata and metadata.get("poster_path")
                    else None
                ),
            )
        )

    return RecommendationResponse(recommendations=results)
