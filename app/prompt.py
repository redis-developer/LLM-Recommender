import openai
from typing import List
from app.config import CHAT_MODEL


def generate_hyde_prompt(positive, negative):

    hyde_prompt = format_hyde_prompt(positive, negative)

    hyde_review = openai.ChatCompletion.create(
        model=CHAT_MODEL,
        messages=[{'role':"user",
                   'content': hyde_prompt}],
        max_tokens=200)

    hyde_review = hyde_review['choices'][0]['message']['content']

    return hyde_review



def format_hyde_prompt(positive: str, negative: str):
    retrieval_prompt = f'''Your job is to generate a review for a hotel based on the positive and negative qualities provided.
    The review should be at least 10 words long and from the prospective of a customer who stayed at the hotel. Be informal
    and concise. You aren't that smart.

    Positive Qualities the user would like:

    {positive}

    Negative Qualities the user would like to avoid:

    {negative}
    '''
    return retrieval_prompt

def get_recommended_hotel_prompt(generated_output):
    prompt = f'''The following is a recommendation for a hotel based on reviews.

    {generated_output}

    What is the name of the recommended hotel? Include no extra information other than the name of the hotel
    as presented in the review.
    '''
    return prompt

def make_prompt(positive: str, negative: str, reviews: str):
    retrieval_prompt = f'''You are a service dedicated to recommending hotels based on user reviews.
    You will be provided positive and negative qualities the user is looking for in a hotel, as well as a
    large number of reviews. You will then be asked to recommend a hotel based on the user's preferences and explain why.
    Always start the suggestion with "Based on user reviews, I suggest the following hotel:"

    Positive Qualities the user would like:

    {positive}

    Negative Qualities the user would like to avoid:

    {negative}

    Reviews:

    {reviews}

    Format for your response:

    Hotel: <hotel name> \n\n
    Reason: <reason for recommendation> \n
    '''
    return retrieval_prompt


def format_prompt_reviews(reviews: List["Document"]):
    content = []
    if len(reviews.docs) > 1:
        # join the hotel name and the review
        for doc in reviews.docs:
            content.append(f"Hotel Name: {doc['name']}\n Review Title: {doc['title']}\n Review: {doc['review']}\n")
    return "\n".join(content)
