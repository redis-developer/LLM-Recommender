
import os
import openai
import pickle
import streamlit as st

from urllib.error import URLError
from redisvl.vectorize.text import HFTextVectorizer
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from app.config import (
    CHAT_MODEL,
    VECTORIZER,
    DATAFILE
)
from app.retrieve import (
    create_retrieval_index,
    retrieve_context,
    make_filter,
    retrieve_hotel_reviews,
    retrieve_hotel_data
)
from app.prompt import (
    make_prompt,
    generate_hyde_prompt,
    format_prompt_reviews,
    get_recommended_hotel_prompt
)

from app.constants import (
    STATES,
    CITIES
)

def recommend_hotel(positive, negative, reviews):

    prompt = make_prompt(positive, negative, reviews)
    retrieval = openai.ChatCompletion.create(
        model=CHAT_MODEL,
        messages=[{'role':"user",
                   'content': prompt}],
        max_tokens=1000)

    # get the response
    response = retrieval['choices'][0]['message']['content']
    return response


def get_hotel_name(recommendation):
    prompt = get_recommended_hotel_prompt(recommendation)
    retrieval = openai.ChatCompletion.create(
        model=CHAT_MODEL,
        messages=[{'role':"user",
                   'content': prompt}],
        max_tokens=1000)

    # get the response
    response = retrieval['choices'][0]['message']['content']
    return response

@st.cache_resource
def vectorizer():
    return HFTextVectorizer(f"sentence-transformers/{VECTORIZER}")

@st.cache_data
def load_data():
    data = pickle.load(open(DATAFILE, "rb"))
    return data

def set_city():
    state = st.session_state["state"]
    return CITIES[state][0]

def main():
    data = load_data()
    INDEX = create_retrieval_index(data)
    EMBEDDING_MODEL = vectorizer()

    try:
        # Defining default values
        defaults = {
            "state": "AL",
            "city": CITIES["AL"][0],
            "positive": "",
            "negative": "",
            "response": "",
            "hotel_info": "",
            "hotel_reviews": "",
            "all_similar_reviews": ""
        }

        # Checking if keys exist in session state, if not, initializing them
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

        col1, col2 = st.columns([4,2])
        with col1:
            st.write("# LLM Hotel Recommendation System")

        st.selectbox("State", STATES, key="state", on_change=set_city)
        st.selectbox("City", CITIES[st.session_state['state']], key="city")
        st.text_input("What would you like in a hotel?", key="positive")
        st.text_input("What would you like to avoid in a hotel?", key="negative")

        if st.button("Find Hotel"):
            with st.spinner("OpenAI and Redis are working to find you a hotel..."):
                # filter
                query_filter = make_filter(st.session_state['state'], st.session_state['city'])

                # make a hyde prompt
                hyde_prompt = generate_hyde_prompt(
                    st.session_state['positive'],
                    st.session_state['negative']
                )

                # Retrieve the context
                context = retrieve_context(INDEX,
                                           hyde_prompt,
                                           EMBEDDING_MODEL,
                                           query_filter=query_filter)

                all_reviews = format_prompt_reviews(context)

                recommendation = recommend_hotel(
                    st.session_state['positive'],
                    st.session_state['negative'],
                    all_reviews
                )

                hotel_name = get_hotel_name(recommendation)
                rating, hotel_reviews = retrieve_hotel_reviews(INDEX, hotel_name)
                reviews = "\n".join([f"{i}. " + review for i, review in enumerate(hotel_reviews, 1)])

                hotel_info = f"Name: {hotel_name} \nAverage Rating: {rating}"
                hotel_data = retrieve_hotel_data(INDEX, hotel_name)
                if hotel_data:
                    hotel_info += "\n" + "\n".join([f"{k}: {v}" for k, v in hotel_data.items()])
                st.session_state['response'] = recommendation
                st.session_state['hotel_info'] = hotel_info
                st.session_state['hotel_reviews'] = reviews
                st.session_state['all_similar_reviews'] = all_reviews


            st.write("### Recommendations")
            st.write(f"{st.session_state['response']}")
            with st.expander("Show Hotel Info"):
                st.text(st.session_state['hotel_info'])
            with st.expander("Show Hotel Reviews"):
                st.text(st.session_state['hotel_reviews'])
            with st.expander("Show All Similar Reviews"):
                st.text(st.session_state['all_similar_reviews'])


    except URLError as e:
        st.error(
            """
            **This demo requires internet access.**
            Connection error: %s
            """
            % e.reason
        )