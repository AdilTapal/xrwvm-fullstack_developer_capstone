# Uncomment the imports below before you add the function code
# import requests
import os
from dotenv import load_dotenv

load_dotenv()

def _env_or_default(name, default_value):
    value = os.getenv(name, default_value)
    if not value or not value.startswith(('http://', 'https://')):
        return default_value
    return value


backend_url = _env_or_default('backend_url', "http://localhost:3030")
sentiment_analyzer_url = _env_or_default('sentiment_analyzer_url', "http://localhost:5050/")

# def get_request(endpoint, **kwargs):
# Add code for get requests to back end

# def analyze_review_sentiments(text):
# request_url = sentiment_analyzer_url+"analyze/"+text
# Add code for retrieving sentiments

# def post_review(data_dict):
# Add code for posting review
