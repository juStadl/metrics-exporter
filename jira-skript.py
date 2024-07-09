import requests, logging
from requests.auth import HTTPBasicAuth
from datadog import initialize, statsd
from datetime import datetime
import time

# Jira Credentials
JIRA_URL = "https://testo-web.atlassian.net"
USERNAME = "jstadler@testo.de"
API_TOKEN = "ATATT3xFfGF01-E_Jx_tA6a6oGRLemUbMhwIfMAwRylmCWVo8z7DECWiOa5hXJxCDfXMQAOiE0Y86Nfz4ZRgwQMUJ3ISZEI4nMx_dt7qbfiQyqVK9h2KkwOAtjpdzWASlJHkPx0IVYdVgQR3k7i-4R8dJ44MDuCAbG1-9ngs-H-5LI9GCAEGdQo=8106C6A7"
PROJECT_KEY = "SAVF"

# Statsd-Initialiserung (DataDog Agent)
options = {
    'statsd_host': '127.0.0.1',  
    'statsd_port': 8125          
}
initialize(**options)

# Authentifizierung
auth = HTTPBasicAuth(USERNAME, API_TOKEN)

# Logging Initialisierung
logging.basicConfig(level=logging.ERROR)

# Anzahl offener Bugs ( Metrik )
def open_bugs_metric(board_id, board_name):

# Die Teams werden durch ihre Board IDs gefiltert.
# Um weitere Teams zu ergänzen, Board-ID im Dictionary 'boards' hinzufügen

    try:
        jql = f"project={PROJECT_KEY} AND issuetype=Bug AND sprint in openSprints() AND status != 'Done'"
        url = f"{JIRA_URL}/rest/agile/1.0/board/{board_id}/issue"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        } 
        params = {
           "jql" : jql
        }

        response = requests.get(url, headers=headers, auth=auth, params=params)
        response.raise_for_status()

        data = response.json()
        issues = data["total"]

        # Metrik an Datadog senden
        statsd.gauge("jira.open_bugs", issues, tags=[f"Team:{board_name}"])

    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching amount of open bugs frim Jira: {e}")
        return None 

# Sammeln aller geschlossenen Bugs ( Hilfsfunktion )    
def get_all_done_bugs_by_boardId(board_id):
    try:
        jql = f"project={PROJECT_KEY} AND issuetype=Bug AND status='Done'"
        url = f"{JIRA_URL}/rest/agile/1.0/board/{board_id}/issue"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        params = {
            "jql": jql
        }

        response = requests.get(url, headers=headers, auth=auth, params=params)
        response.raise_for_status()

        data = response.json()
        issues = data["issues"]

        issues_list = []
        for issue in issues:
            issues_list.append(issue)

        return issues_list
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching amount of bugs with status 'DONE' by Board-ID: {e}")
        return None
    
# Zeit in Stunden, bis Bugs abgearbeitet wurden ( Metrik )
def average_bug_resolution_time_metric(board_id, board_name):
    try:
        issues = get_all_done_bugs_by_boardId(board_id)

        for issue in issues:
            creationDate = str(issue["fields"]["created"])
            endDate = str(issue["fields"]["statuscategorychangedate"])

            if creationDate and endDate:
                dt_creationDate = datetime.strptime(creationDate, "%Y-%m-%dT%H:%M:%S.%f%z")
                dt_endDate = datetime.strptime(endDate, "%Y-%m-%dT%H:%M:%S.%f%z")

                time_diff_seconds = (dt_endDate - dt_creationDate).total_seconds()
                time_diff_hours = time_diff_seconds / 3600   
                statsd.histogram("jira.bug_resolution_time", time_diff_hours, tags=[f"Team:{board_name}"])

            else:
                logging.error("Failed to retriebe issues")

    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to collecht Average Bug Resolution Time Metric: {e}")
        return None

# Anzahl aller Bugs pro Zeiteinheit ( Metrik )
def bug_frequency_metric(board_id, board_name):
    try:
        jql = f"project={PROJECT_KEY} AND issuetype=Bug"
        url = f"{JIRA_URL}/rest/agile/1.0/board/{board_id}/issue"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        } 
        auth = (USERNAME, API_TOKEN)
        params = {
           "jql" : jql
        }

        response = requests.get(url, headers=headers, auth=auth, params=params)
        response.raise_for_status()

        data = response.json()
        bugs = data["total"]

        statsd.histogram("jira.bug_frequency", bugs, tags=[f"Team:{board_name}"])

    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching bugs from Jira: {e}")
        return None
        
# Durchschnittszeit, in der eine Story auf 'Done' gesetzt wird    
def lead_time_for_changes_metric(board_id, board_name):
    try:
        jql = f"project={PROJECT_KEY} AND sprint in openSprints() AND issuetype='Story' AND status='Done'"
        url = f"{JIRA_URL}/rest/agile/1.0/board/{board_id}/issue"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        } 
        auth = (USERNAME, API_TOKEN)
        params = {
            "jql" : jql
        }

        response = requests.get(url, headers=headers, auth=auth, params=params)
        response.raise_for_status()

        data = response.json()
        stories = data["issues"]

        for story in stories:
            creationDate = story["fields"]["created"]
            endDate = story["fields"]["statuscategorychangedate"]


            if creationDate and endDate:
                dt_creationDate = datetime.strptime(creationDate, "%Y-%m-%dT%H:%M:%S.%f%z")
                dt_endDate = datetime.strptime(endDate, "%Y-%m-%dT%H:%M:%S.%f%z")

                time_diff_seconds = (dt_endDate - dt_creationDate).total_seconds()
                time_diff_hours = time_diff_seconds / 3600
                time_diff_days = time_diff_hours / 24   
                statsd.histogram("jira.lead_time_for_change", time_diff_days, tags=[f"Team:{board_name}"])

            else:
                logging.error("Failed to retrieve issues")

    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data from Jira: {e}")
        return None

# Anzahl der Bugs pro Stories in einem aktiven Sprint
def change_failure_rate_metric(board_id, board_name):    
    try:
        jql_bugs = f"project={PROJECT_KEY} AND sprint in openSprints() AND issuetype=Bug"
        jql_stories = f"project={PROJECT_KEY} AND sprint in openSprints() AND issuetype=Story"
        url = f"{JIRA_URL}/rest/agile/1.0/board/{board_id}/issue"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        } 
        auth = (USERNAME, API_TOKEN)
        params_bugs = {
            "jql" : jql_bugs
        }
        params_stories = {
            "jql" : jql_stories
        }

        response_bugs = requests.get(url, headers=headers, auth=auth, params=params_bugs)
        response_bugs.raise_for_status()
        
        repsonse_stories = requests.get(url, headers=headers, auth=auth, params=params_stories)
        repsonse_stories.raise_for_status()
        

        data_bugs = response_bugs.json()
        data_stories = repsonse_stories.json()

        count_of_bugs = data_bugs["total"]
        count_of_stories = data_stories["total"]

        change_failure_rate = (count_of_bugs / count_of_stories)

        statsd.histogram("jira.change_failure_rate", change_failure_rate, tags=[f"Team:{board_name}"])

    except requests.exceptions.RequestException as e:
        logging.error(f"Error calculating metric (Change Failure Rate): {e}")

    
# Mainfunktion, um Metrikfunktionen aufzurufen
if __name__ == "__main__":
    # Boards
    boards = {
        214:"Pi",
        213:"Delta"
}
    try:
        for boards_id, boards_name in boards.items():
            open_bugs_metric(boards_id, boards_name)
            bug_frequency_metric(boards_id, boards_name)
            average_bug_resolution_time_metric(boards_id, boards_name)
            lead_time_for_changes_metric(boards_id, boards_name)
            change_failure_rate_metric(boards_id, boards_name)
        logging.info("Finished schedule")    
       
    except Exception as e:
           logging.error(f"Error in Mainmethod: {e}")
