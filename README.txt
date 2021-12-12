Project Overview
This code base contains the necessary architecture for hosting a web server application. This application acts as a customizable Covid-19 dashboard.
The dashboard combines multiple data sources into one useful view to give an overview of the recent updates and status of the pandemic.
The application integrates two main sources, the first being Covid-19 related data/metrics such as, latest count of hospital cases, new infections and deaths.
The second is news articles related to Covid-19, which can be read to gain better understanding of the current status of the pandemic.

The codebase can be found at - https://github.com/MohdAq17/CovidDashboard

Installation
1- Please ensure python is installed in your system (https://www.python.org/downloads/)
2- Please ensure the requirements.txt are installed in your current python environment.
3- Please alter the config.json and edit as applicable/required. Note the API key must be set in place, obtain your API key through https://newsapi.org/.
4- Please run through the command line prompt (either CMD or PowerShell) the following commands within the project directory:
- pytest : To test the server before actually hosting it.
- python.exe main.py : To run and host the server.  Note that this will host a development server. Use a production server as necessary.
5- Please open your browser and navigate to: http://127.0.0.1:5000/index where you will be able to use the web application and view the pandemic status.

Usage
1- To update the underlying data, you can schedule update by using the form embedded in the webpage.
2- You can cancel scheduled updates by using the (close) icon on individual updates (after adding them, they will be visible).
3- You can remove news articles by also using the (close) icon on the individual news article.
4- The webpage refreshes periodically, but the data does not. For data to be updated, kindly consider point 1 to schedule updates.
5- The updates and removed news articles will remain saved until the server restarts.

Technical Details
The code is written entirely in python and uses the following packages (List can also be found in requirements.txt)
-flask
This acts as the web framework used to build the web application. For further documentation please visit: https://flask.palletsprojects.com/en/2.0.x/
-uk-covid19
This is a python package used to retrieve the Covid-19 related data metrics. For further documentation please visit: https://publichealthengland.github.io/coronavirus-dashboard-api-python-sdk/
-requests
To retrieve the news articles, the requests python package was used in conjunction with https://newsapi.org/.
-pytest
Unit tests were developed in the following files that conform with and can be invoked by pytest:
test_covid_application.py
test_covid_data_handler.py
test_news_data_handling.py

Enhancements and Further Development
The codebase has two main features:
1- It is written with consideration to the PEP 20 guidelines (https://www.python.org/dev/peps/pep-0020/), so when extending the codebase, wherever applicable, please do continue applying the guidelines.
2- It uses structured commenting that should explain what the code intends to do.
This makes further development and diving into the codebase a breeze. The following is an overview of the file architecture:
|   config.json
|   covid_data_handler.py
|   covid_news_handling.py
|   global_vars.py
|   main.py
|   nation_2021-10-28.csv
|   README.txt
|   requirements.txt
|   scheduler.py
|   sys.log
|   test_covid_application.py
|   test_covid_data_handler.py
|   test_news_data_handling.py
|   time_conversions.py
+---static
|   \---images
|           dashboard_logo.jpg
\---templates
        index.html
