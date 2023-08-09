
import openai
from redisvl.query import TagFilter, VectorQuery
from redisvl.index import SearchIndex
from redis.commands.search.query import Query

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
        hybrid_filter=query_filter,
        num_results=30
    )

    results = index.query(vector_query)
    return results

def retrieve_hotel_data(index, hotel_name):
    query = TagFilter("name", hotel_name)
    results = index.search(str(query))
    if results:
        data = results.docs[0].__dict__
        return {
            "address": data["address"],
            "city": data["city"],
            "state": data["state"],
            "categories": data["categories"]
        }
    return None


def retrieve_hotel_reviews(index, hotel_name):
    rating = 0
    reviews = []
    query = TagFilter("name", hotel_name)
    results = index.search(str(query))
    if results:
        for doc in results.docs:
            reviews.append(doc["review"])
            rating += int(doc["rating"])
        rating = rating / len(results.docs)
    return rating, reviews

def make_filter(state: str = None, city: str = None) -> TagFilter:
    if state is None and city is None:
        return None
    elif state is None:
        query_filter = TagFilter("city", city)
    elif city is None:
        query_filter = TagFilter("state", state)
    else:
        query_filter = TagFilter("state", state)
        city_filter = TagFilter("city", city)
        query_filter += city_filter
    return query_filter


