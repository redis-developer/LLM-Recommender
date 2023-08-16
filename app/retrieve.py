
from redisvl.query import VectorQuery
from redisvl.query.filter import Tag, FilterExpression
from redisvl.index import SearchIndex
from typing import List, Dict, Union, Any

from app.config import REDIS_ADDRESS, SCHEMA


def create_retrieval_index(data):
    index = SearchIndex.from_yaml(SCHEMA)
    index.connect(url=REDIS_ADDRESS)
    if index.exists():
        index = SearchIndex.from_existing('hotelsindex', REDIS_ADDRESS)
    else:
        index.create(overwrite=True)
        # load data
        index.load(data)
    return index


def retrieve_context(index, search_prompt, vectorizer, query_filter=None):

      # Embed the query
    query_embedding = vectorizer.embed(search_prompt)

    # Get the top result from the index
    vector_query = VectorQuery(
        vector=query_embedding,
        vector_field_name="embedding",
        return_fields=["review", "name", "title", "address", "city", "state"],
        filter_expression=query_filter,
        num_results=30,
    )

    results = index.query(vector_query)
    return results


def retrieve_top_three_hotels(results: List[Dict[str, Any]]):
    # count the number of reviews for each hotel and return the three with the most reviews
    hotel_reviews: Dict[str, List[int, List[str]]] = {}
    hotel_data: Dict[str, Dict] = {}

    def get_fields(doc):
        return {
            "name": doc["name"],
            "address": doc["address"],
            "city": doc["city"],
            "state": doc["state"],
            "title": doc["title"],
            "review": doc["review"],
        }

    for doc in results:
        hash_key = str(hash(doc["name"] + doc["address"] + doc["city"] + doc["state"]))
        if hash_key in hotel_reviews:
            hotel_reviews[hash_key][0] += 1
            hotel_reviews[hash_key][1].append(doc["review"])

        else:
            hotel_reviews[hash_key] = [1, [doc["review"]]]
            hotel_data[hash_key] = get_fields(doc)

    top_three = sorted(hotel_reviews.items(), key=lambda x: x[1][0], reverse=True)[:3]
    top_three_hotels = []
    for hash_key, review_data in top_three:
        reviews = review_data[1]
        hotel = hotel_data[hash_key]
        top_three_hotels.append({**hotel, "reviews": reviews})
    return top_three_hotels


def make_filter(state: str = None, city: str = None) -> Union[FilterExpression, None]:
    state_tag = Tag("state")
    city_tag = Tag("city")
    if state and city:
        return (state_tag == state) & (city_tag == city)
    elif state:
        return state_tag == state
    elif city:
        return city_tag == city
    else:
        return None
