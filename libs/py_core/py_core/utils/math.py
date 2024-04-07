from numpy import dot
from numpy.linalg import norm

def cosine_similarity(a: list[float], b:list[float])->float:
    return dot(a, b)/(norm(a)*norm(b))
