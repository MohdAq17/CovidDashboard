"""
This python file contains the functions necessary
for parsing and processing the CSV data. In addtition,
it defines methods for the retrieval of covid related data
through the usage of an API and the scheduling of data updates
for the servers' data.
"""

import sched
from uk_covid19 import Cov19API
from scheduler import sched_instance
import global_vars


def parse_csv_data(csv_filename: str) -> list[str]:
    """
    This function takes as input the file name, and returns
    the file rows as a list.
    """
    # Make an empty list.
    file_rows = []
    # Open the file for reading.
    with open(csv_filename, "r", encoding='utf-8') as file:
        # For each line
        line = file.readline()
        while line:
            # Append the line to the file_rows list, while removing
            # Trailing new lines `\n`
            file_rows.append(line.replace("\n", ""))
            line = file.readline()
    return file_rows


def process_covid_csv_data(covid_csv_data: list[str]) -> tuple[int, int, int]:
    """
    This function takes as input a list containing covid related data in
    a predetermined format. When the format matches, the function shall
    return the following calculated variables:
    total_deaths, current_hospital_cases, last7days_cases
    """

    # Define and assume zero count for all.
    total_deaths = 0
    current_hospital_cases = 0
    last7days_cases = 0

    # One count for the outer loop while the other for the inner loop
    outside_count = 0
    inside_count = 0

    # For each row in the recieved list
    for item in covid_csv_data:
        # Exclude the first row by outside_count != 0, and empty items
        # In other words, find the first non blank element after the first row
        # Which is the header.
        if (outside_count != 0 and item.split(',')[4] != '' and total_deaths == 0):
            # Write only once and do not overwrite again due to total_deaths == 0
            total_deaths = int(item.split(',')[4])
        # Take the first data row and get the current_hospital_cases
        if outside_count == 1:
            current_hospital_cases = int(item.split(',')[5])
        # Count 7 rows after finding the first non blank element
        if (outside_count != 0 and item.split(',')[6] != '' and inside_count <= 7):
            if inside_count == 0:
                inside_count += 1
            else:
                # Exclude the first row by the above, as it
                # represents the `yesterday's` incomplete new
                # cases count.
                last7days_cases += int(item.split(',')[6])
                inside_count += 1
        outside_count += 1
    # Return the computed variables.
    return last7days_cases, current_hospital_cases, total_deaths


def covid_API_request(location: str = 'Exeter', location_type: str = 'ltla') -> dict:
    """
    This function will use the `Cov19API` library to get the latest
    COVID-19 related data, similar to the local csv. This information
    includes the area code, area name, area type, date, cumulative deaths,
    hospital cases, and new cases by the specified date.
    """
    # The setup of the filters, to filter the data from the API
    filters = [
        'areaType='+location_type,
        'areaName='+location
    ]
    # The selected columns for retrieval.
    columns = {
        'areaCode': 'areaCode',
        'areaName': 'areaName',
        'areaType': 'areaType',
        'date': 'date',
        'cumDailyNsoDeathsByDeathDate': 'cumDailyNsoDeathsByDeathDate',
        'hospitalCases': 'hospitalCases',
        'newCasesBySpecimenDate': 'newCasesBySpecimenDate',
    }
    # The function setup and call to retrieve the data.
    api = Cov19API(filters=filters, structure=columns)
    data = api.get_json()
    # For when the scheduler runs, update the data for the
    # web interface
    global_vars.local_data_from_api = data
    return data


def schedule_covid_updates(update_interval: int, update_name: str) -> sched.Event:
    """
    With the use of the sched module, this function will schedule
    the execution of covid data updates.
    """
    # Input into the queue the action required with the correct update
    # interval (delay)
    event = sched_instance.enter(
        delay=update_interval, priority=1, action=covid_API_request)
    print("Task:", update_name, " -- Scheduled.")
    return event
