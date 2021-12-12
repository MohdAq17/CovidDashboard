"""
This file contains the server logic utilizing four
other files that are well documented. The logic contained
within this file acts as an informative COVID-19 tracking
dashboard that is very helpful when trying to attain updates
on the recent developments of COVID-19.
"""

import time
import json
import logging
from flask import Flask, render_template, request
import global_vars
from scheduler import sched_instance
from covid_news_handling import news_API_request
from covid_news_handling import update_news
from covid_news_handling import remove_unwanted_news
from covid_data_handler import parse_csv_data
from covid_data_handler import process_covid_csv_data
from covid_data_handler import covid_API_request
from covid_data_handler import schedule_covid_updates
from time_conversions import hhmm_to_seconds


# Initialize the logging mechanism
logging.basicConfig(filename='sys.log', level=logging.INFO,
                    format="%(levelname)s | %(asctime)s | %(message)s")

app = Flask(__name__)

# Useful for rapid development, for production comment the following
# line. This allows the webpage to refresh and update content whenever
# any file changes
app.debug = True

# Data structures for handling the deleted news
# and updates respectively
deleted_news_list = []
updates_list = []

# Basic information passed to the HTML template, customizable
# through the json.config.
try:
    with open("config.json", "r", encoding='utf-8') as jsonfile:
        config_data = json.load(jsonfile)
except Exception:
    logging.critical('Config file could not be opened, '
                     'please check the path or the existence of the file.')

try:
    # File name/path for the CSV data to be embedded
    file_name = config_data['file_name']
    # The main title of the dashboard
    title = config_data['title']
    # The image name/filepath for the dashboard logo/banner
    image = config_data['image']
    # A prompt message to specify the type of update in the
    # updates column found in the dashboard.
    covid_content = config_data['covid_content']
    news_content = config_data['news_content']
except Exception:
    logging.critical('One or more keys have not been found in the '
                     'config.json file, please ensure all of the keys/parameters configured.')

try:
    # Retrieve the news articles using the function call
    global_vars.news_articles = news_API_request()['articles']

    # Retrieve the covid data using the function call
    global_vars.local_data_from_api = covid_API_request()
except:
    logging.error('Could not complete the fetching of Covid and/or News data '
                  'through the APIs. Please check the network connection or the API key')

try:
    # Parse the csv data, deduce the location provided in the
    # CSV data and by the function call, calculate the
    # last7days_cases, current_hospital_cases, total_deaths
    # variables required for the interface.
    csv_covid_data = parse_csv_data(file_name)
    nation_location = csv_covid_data[1].split(',')[1]
    last7days_cases, current_hospital_cases, total_deaths = process_covid_csv_data(
        csv_covid_data)
except:
    logging.error('Could not parse the local CSV data, please '
                  'check the existence/correctness of the file and its\' name/path')


@app.route("/index", methods=['GET'])
def home():
    """
    The webserver containing the elements and logic needed
    to calculate the required information and render it in the
    HTML template.
    """
    # For the lifetime of the server, use the following global variables.
    global deleted_news_list
    global updates_list
    global sched_instance

    # The implemented HTML template has the following meta tag
    # <meta http-equiv="refresh" content="60;url='/index'">
    # which refreshed the website. The following statement checks
    # the queue for any possible data update, and when the delay
    # or time interval passes, it becomes ready for execution
    # and the following line executes it.
    logging.info('Next scheduled update: %s Seconds', str(sched_instance.run(blocking=False)))

    # Assume zero infections and then traverse the
    # last 7 days data, excluding the first
    # as it is incomplete, and sum the number of infections
    local_7day_infections = 0
    for day in global_vars.local_data_from_api['data'][1:8]:
        local_7day_infections += day['newCasesBySpecimenDate']
    # Retrieve dynamically the area name from the data
    # retrieved from the function call.
    location = global_vars.local_data_from_api['data'][0]['areaName']

    # If a delete update button has been pressed, retrieve the identifier
    # which is the title of the update
    delete_update = request.args.get('update_item')
    if delete_update:
        logging.info('Deleting the following update: %s', delete_update)
        # Traverse all the updates list elements
        for i in range(len(updates_list)):
            # If the title matches the input of the user (by pressing
            # the delete button on the update)
            if updates_list[i]['title'] == delete_update:
                # Cancel the scheduled element and remove it from the
                # queue
                try:
                    sched_instance.cancel(updates_list[i]['event_handler'])
                # If the element is not in the queue anymore, (if it is already
                # executed), do not halt the application, proceed with the
                # remaining logic, of removing from the web interface.
                except ValueError:
                    logging.warning('The event_handler could not be found, '
                                    'might already be executed')
                # And delete it from the updates_list, to remove it from
                # the interface
                del updates_list[i]
                logging.info('Deleted the following update: %s', delete_update)
                break

    # If the delete button of the news is pressed,
    # maintain the list of unwanted news.
    delete_news = request.args.get('notif')
    if delete_news:
        logging.info('Deleting the following news: %s', delete_news)
        if delete_news not in deleted_news_list:
            deleted_news_list.append(delete_news)
            logging.info('Deleted the following news: %s', delete_news)

    # After that, use the function call to subtract the unwanted news articles
    # and update the list.
    global_vars.news_articles = remove_unwanted_news(
        news_articles=global_vars.news_articles, news_to_be_excluded=deleted_news_list)

    # Check if the add update form has been clicked and includes the mandatory
    # textfield for the label.
    update_text = request.args.get('two')
    if update_text:
        logging.info('Adding the following update: %s', update_text)

        # If the user entered the text field, start preparing to make an update
        # by first taking the remaining parameters.
        update_time = request.args.get('update')
        repeat_flag = request.args.get('repeat')
        covid_data_flag = request.args.get('covid-data')
        news_flag = request.args.get('news')

        # Then take a time stamp for the current time and calculate the absolute
        # difference between the user entered time and the time of adding the
        # update.
        curr_time = time.localtime(time.time())
        current_time = str(curr_time.tm_hour)+':'+str(curr_time.tm_min)
        update_interval = abs(hhmm_to_seconds(
            update_time)-hhmm_to_seconds(current_time))

        # Then prepare an informative string, used in the ['content'] part of the
        # update.
        update_content = ', initiated at ' + str(curr_time.tm_year)+'-' + \
            str(curr_time.tm_mday)+'-'+str(curr_time.tm_mday)+' - ' + \
            str(curr_time.tm_hour)+':'+str(curr_time.tm_min)+':' + \
            str(curr_time.tm_sec)
        update_content += ', with a delay of (Seconds) '

        # If the covid data flag is selected (update the covid data)
        # Use the function call to add an update to the queue, and
        # append the update to the updates_list for proper viewing
        # in the interface.
        if covid_data_flag:
            event = schedule_covid_updates(update_interval, update_text)
            updates_list.append({'title': update_text, 'content': covid_content +
                                update_content+str(update_interval), 'event_handler': event})
            logging.info('Added the following update: %s %s %s',
                         covid_content, update_content, str(update_interval))
            if repeat_flag:
                event = schedule_covid_updates(
                    update_interval+86400, update_text)
                updates_list.append({'title': update_text, 'content':
                                     covid_content + update_content+str(update_interval+86400),
                                     'event_handler': event})
                logging.info('Added the following update: %s %s %s through'
                             'the usage of the repeat flag.',
                             covid_content, update_content, str(update_interval+86400))

        # The same is true as for the covid_data_flag.
        if news_flag:
            event = update_news(update_text, update_interval=update_interval)
            updates_list.append({'title': update_text, 'content': news_content +
                                update_content+str(update_interval), 'event_handler': event})
            logging.info('Added the following update: %s %s %s',
                         news_content, update_content, str(update_interval))
            if repeat_flag:
                event = update_news(
                    update_text, update_interval=update_interval+86400)
                updates_list.append({'title': update_text, 'content': news_content +
                                    update_content+str(update_interval+86400),
                                    'event_handler': event})
                logging.info('Added the following update: %s %s %s '
                             'through the usage of the repeat flag.',
                             news_content, update_content, str(update_interval+86400))

    # After setting all the variables in the proper format, pass them to the template
    # for flask to prepare the HTML's response.
    return render_template("index.html",news_articles=global_vars.news_articles,
                           nation_location=nation_location,
                           national_7day_infections=last7days_cases,
                           deaths_total=total_deaths, hospital_cases=current_hospital_cases,
                           location=location, local_7day_infections=local_7day_infections,
                           image=image, title=title, updates=updates_list)

if __name__ == "__main__":
    # Run the flask backend server application
    app.run()
