from pydantic import BaseModel, Field


class MovieRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    num_recommendations: int = Field(default=5, ge=1)


class RecommendationItem(BaseModel):
    title: str
    genres: str
    overview: str | None = None
    poster: str | None = None


class RecommendationResponse(BaseModel):
    recommendations: list[RecommendationItem]
