# Uncomment the imports below before you add the function code
import requests
import os
from dotenv import load_dotenv

load_dotenv()


def _env_or_default(name, default_value):
    value = os.getenv(name, default_value)
    if not value or not value.startswith(('http://', 'https://')):
        return default_value
    return value


backend_url = _env_or_default(
    'backend_url', "http://localhost:3030")
sentiment_analyzer_url = _env_or_default(
    'sentiment_analyzer_url', "http://localhost:5050/")


def get_request(endpoint, **kwargs):
    params = ""
    if kwargs:
        for key, value in kwargs.items():
            params = params + key + "=" + value + "&"

    request_url = backend_url + endpoint + "?" + params

    print("GET from {} ".format(request_url))
    try:
        response = requests.get(request_url)
        return response.json()
    except Exception:
        print("Network exception occurred")


def analyze_review_sentiments(text):
    request_url = sentiment_analyzer_url + "analyze/" + text
    try:
        response = requests.get(request_url)
        return response.json()
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        print("Network exception occurred")
# Add code for posting review
def post_review(data_dict):
    request_url = backend_url+"/insert_review"
    try:
        # Call post method of requests library with URL and parameters
        response = requests.post(request_url, json=data_dict)
        return response.json()
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        print("Network exception occurred")
