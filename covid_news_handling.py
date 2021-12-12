"""
This python file contains the functions necessary
for the retrieval of covid related news through the
usage of an API and the scheduling of news data
updates for the servers' data.
"""

import json
import sched
import requests
from scheduler import sched_instance
import global_vars


def news_API_request(covid_terms: str = 'Covid COVID-19 coronavirus') -> dict:
    """
    This function accepts as input the search terms
    and returns the news data in a dict format.
    Please note that this function uses a private
    API key, make sure to update it with your own
    using the config.json.
    """
    # Retrieve the API key from the config.json file, please update
    # with your own private key.
    with open("config.json", "r", encoding='utf-8') as jsonfile:
        config_data = json.load(jsonfile)
    # Set up the request url while configuring the
    # parameters
    url = 'https://newsapi.org/v2/everything?'
    url += 'q=' + covid_terms.replace(' ', ' OR ')
    url += '&apiKey=' + config_data['news_api_key']
    # Make the HTTPS GET request
    response = requests.get(url)
    # For when the scheduler runs, update the news data for
    # the web interface
    global_vars.news_articles = response.json()['articles']
    # Return the data
    return response.json()


def update_news(update_name: str, update_interval: int = 15) -> sched.Event:
    """
    With the use of the sched module, this function will schedule
    the execution of covid news updates.
    """
    # Input into the queue the action required with the correct update
    # interval (delay)
    event = sched_instance.enter(
        delay=update_interval, priority=2, action=news_API_request)
    print("Task:", update_name, " -- Scheduled.")
    return event


def remove_unwanted_news(news_articles: list, news_to_be_excluded: list) -> list:
    """
    This function recieves as input two lists of news.
    One being the main news and the other being the
    news to be excluded and returns the list of kept news.
    news_articles - news_to_be_excluded
    """
    # Create a new list, iterating over each element in
    # news_articles, and keeping it only if it is not
    # found in the news_to_be_excluded.
    return [kept_news for kept_news in news_articles if \
                not kept_news['title'] in news_to_be_excluded]
