# first line: 49
@memory.cache
def precompute_collaborative_predictions():
    all_movie_ids = ratings_sampled["movieId"].unique()
    predictions = {}
    for user_id in ratings_sampled["userId"].unique():
        user_predictions = {
            movie_id: model.predict(user_id, movie_id).est
            for movie_id in all_movie_ids if movie_id not in ratings_sampled[ratings_sampled["userId"] == user_id]["movieId"].values
        }
        predictions[user_id] = user_predictions
    return predictions
