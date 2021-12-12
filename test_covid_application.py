import json
import sched
from covid_news_handling import news_API_request
from covid_news_handling import update_news
from covid_data_handler import parse_csv_data
from covid_data_handler import covid_API_request
from covid_data_handler import schedule_covid_updates
from covid_news_handling import remove_unwanted_news
# From covid_data_handler import process_covid_csv_data

with open("config.json", "r", encoding='utf-8') as jsonfile:
    config_data = json.load(jsonfile)

def test_parse_csv_data_schema():
    # To ensure the first row of the csv 
    # Follows the necessary data format
    data = parse_csv_data(config_data['file_name'])
    assert data[0] == 'areaCode,areaName,areaType,date,cumDailyNsoDeathsByDeathDate,hospitalCases,newCasesBySpecimenDate'

def test_parse_csv_data_number_of_rows():
    # To ensure all the rows have seven attributes
    data = parse_csv_data(config_data['file_name'])
    for row in data:
        assert len(row.split(',')) == 7

def test_covid_API_request_default_values():
    # To ensure the default parameters retrieve exeter
    # ltla data
    data = covid_API_request()
    assert data['data'][0]['areaCode'] == 'E07000041'
    assert data['data'][0]['areaName'] == 'Exeter'
    assert data['data'][0]['areaType'] == 'ltla'

def test_covid_API_request_passed_params():
    # To ensure the ability of specifying the location
    # and location type that they work
    data = covid_API_request(location='England',location_type='nation')
    assert data['data'][0]['areaCode'] == 'E92000001'
    assert data['data'][0]['areaName'] == 'England'
    assert data['data'][0]['areaType'] == 'nation'

def test_schedule_covid_updates_return_type():
    # To ensure that the scheduling function returns
    # the event, this is necessary for cancelling the 
    # scheduled task
    event = schedule_covid_updates(update_interval=10, update_name='update test')
    assert isinstance(event, sched.Event)

def test_news_API_request_status():
    # To test the connection to the news provider
    assert news_API_request()['status'] == 'ok'

def test_news_API_request_schema():
    # To ensure that the title and content is retrieved 
    # for news articles 
    news_articles = news_API_request()
    assert news_articles['articles'][0]['title']
    assert news_articles['articles'][0]['content']

def test_update_news_return_type():
    # To ensure that the scheduling function returns
    # the event, this is necessary for cancelling the 
    # scheduled task
    event = update_news('test')
    assert isinstance(event, sched.Event)

def test_remove_news():
    # To test the removal of news articles
    news_articles = {
        "articles": [
            {
                "author": "Jon Fingas",
                "title": "Texas Apple store closes due to COVID-19 outbreak",
                "content": "Apple has generally been cautious in dealing with COVID-19 even as it loosens store policies, but that apparently wasnt enough to prevent an outbreak among staff. NBC Newsreports the Apple store in … [+1463 chars]"
            },
            {
                "author": "Jacqueline Howard, CNN",
                "title": "Mounting evidence highlights the importance of Covid-19 boosters",
                "content": "(CNN)As the world learns more about the Omicron coronavirus variant and Delta continues to cause Covid-19 cases to rise around much of the United States, the need for booster shots becomes clearer th… [+8433 chars]"
            }
        ]
    }
    news_to_be_excluded = ["Texas Apple store closes due to COVID-19 outbreak", ]
    assert remove_unwanted_news(news_articles['articles'], news_to_be_excluded) == [{
        "author": "Jacqueline Howard, CNN",
        "title": "Mounting evidence highlights the importance of Covid-19 boosters",
        "content": "(CNN)As the world learns more about the Omicron coronavirus variant and Delta continues to cause Covid-19 cases to rise around much of the United States, the need for booster shots becomes clearer th… [+8433 chars]"
    }]
