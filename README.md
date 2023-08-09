
# LLM Hotel Recommender

The LLM Hotel Recommender is a Streamlit app that uses [Redis](https://redis.com) and the [OpenAI API](https://api.openai.com/) to generate hotel recommendations based on a user's preferences. Because Redis can perform semantic search in addition to other operations like tag and text search
users are able to search for hotels in the US based on a variety of criteria, including:

- State
- City
- Positive Qualities
- Negative Qualities

The application will cite it's sources (reviews) for each recommendation and provide all the reviews that were returned.

## Design

The recommender uses the Hypothetical Document Embeddings (HyDE) approach which uses an LLM (OpenAI in this case)
to generate a fake review based on user input. The system then uses Redis vector search to semantically search
for hotels with reviews that are similar to the fake review. The returned reviews are then passed to another LLM to
generate a recommendation for the user.

![Design](./assets/design.png#gh-light-mode-only)
![Design](./assets/design-dark.png#gh-dark-mode-only)


## Run the Application


### Docker Compose
1. Create your env file:

    ```bash
    $ cp .env.template .env
    ```
    *fill out values, most importantly, your `OPENAI_API_KEY`*

2. Run with docker compose:
    ```bash
    $ docker compose up
    ```
        *add `-d` option to daemonize the processes to the background if you wish.*

    Issues with dependencies? Try force-building with no-cache:
    ```
    $ docker compose build --no-cache
    ```

3. Navigate to:
    ```
    http://localhost:8501/
    ```


### Local

1. Create your env file:

    ```bash
    $ cp .env.template .env
    ```
    *fill out values, most importantly, your `OPENAI_API_KEY`*

2. Clone the repo:
    ```bash
    $ git clone https://github.com/RedisVentures/llm-recommender.git

3. Install dependencies:
    ```bash
    $ pip install -r requirements.txt
    ```

3. Run the app:
    ```bash
    $ streamlit run run.py
    ```


## Known Bugs

1. Hotels by the same name in different cities are not handled well

## Future Work

1. Add more search criteria (GeoFilter, Price, etc.)
2. Dataset is relatively sparse
3. Use OpenAI Functions or parsing to extract Hotel name from recommendation instead of LLM
