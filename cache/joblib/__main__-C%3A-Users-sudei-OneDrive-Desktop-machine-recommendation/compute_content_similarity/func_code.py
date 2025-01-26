# first line: 34
@memory.cache
def compute_content_similarity():
    return cosine_similarity(genre_matrix)
