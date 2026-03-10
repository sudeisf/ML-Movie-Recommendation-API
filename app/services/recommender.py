import re
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class MovieRecommender:
    def __init__(self, data_dir: Path, sample_size: int = 1000):
        self.data_dir = data_dir
        self.sample_size = sample_size
        self.movies = pd.DataFrame()
        self.ratings = pd.DataFrame()
        self.links = pd.DataFrame()
        self.cosine_sim = None
        self._load_data()
        self._build_similarity()

    def _read_csv(self, file_name: str) -> pd.DataFrame:
        file_path = self.data_dir / file_name
        if not file_path.exists():
            raise FileNotFoundError(f"Dataset file not found: {file_path}")
        return pd.read_csv(file_path)

    def _load_data(self) -> None:
        self.movies = self._read_csv("movies.csv").iloc[: self.sample_size].copy()
        self.ratings = self._read_csv("ratings.csv").iloc[: self.sample_size].copy()
        self.links = self._read_csv("links.csv").copy()

        self.movies["genres"] = self.movies["genres"].fillna("").str.replace("|", " ", regex=False)
        self.movies["title_genres"] = self.movies["title"].fillna("") + " " + self.movies["genres"]

        avg_ratings = self.ratings.groupby("movieId")["rating"].mean()
        self.movies["avg_rating"] = self.movies["movieId"].map(avg_ratings).fillna(0)

    def _build_similarity(self) -> None:
        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf_matrix = vectorizer.fit_transform(self.movies["title_genres"])
        self.cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

    def get_movie_index(self, title: str) -> int | None:
        normalized_title = re.sub(r"\(\d{4}\)", "", title).strip().lower()
        matching_movies = self.movies[
            self.movies["title"].str.contains(normalized_title, case=False, na=False, regex=False)
        ]
        if matching_movies.empty:
            return None
        return int(matching_movies.index[0])

    def recommend_movies(self, title: str, num_recommendations: int = 10) -> pd.DataFrame:
        idx = self.get_movie_index(title)
        if idx is None:
            return pd.DataFrame()

        sim_scores = list(enumerate(self.cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda item: item[1], reverse=True)
        top_similar = sim_scores[1 : num_recommendations + 1]
        top_indices = [i for i, _ in top_similar]

        recommendations = self.movies.iloc[top_indices].copy()
        similarity_by_index = {i: score for i, score in top_similar}
        recommendations["content_score"] = recommendations.index.to_series().map(similarity_by_index).fillna(0)
        recommendations["adjusted_score"] = (
            recommendations["avg_rating"] * 0.5 + recommendations["content_score"] * 0.5
        )

        return recommendations.sort_values(by="adjusted_score", ascending=False)
