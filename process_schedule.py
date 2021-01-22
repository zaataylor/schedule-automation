#!/usr/bin/python3
import csv
import calendar
import os
import json
import time

import requests

# API key and token for use with Trello API
# NOTE: make sure you set the environment variables on your
# system to these names exactly
API_KEY = os.getenv('TRELLO_API_KEY')
API_TOKEN = os.getenv('TRELLO_API_TOKEN')

# Trello API URL
BASE_API_URL = 'https://api.trello.com'
# Trello Cards API URL
CARDS_URL = BASE_API_URL + '/1/cards/'
# Trello Checklist API URL
CHECKLIST_URL = BASE_API_URL + '/1/checklists'
# Trello Boards API URL
BOARDS_URL = BASE_API_URL + '/1/members/me/boards'

# ID of the CSC 414 Label on your board
# NOTE: You might need to change this to whatever specific label(s)
# you're using on your board. You can get the ID for any given label
# by visiting your Trello board from the browser, then adding '.json'
# to the end of the URL. There should be a JSON key called 'labels' or
# something similar
CSC_414_LABEL_ID = 'YOUR LABEL ID HERE'
# the name of the board to add cards on
BOARD_NAME = 'YOUR BOARD NAME HERE'
# the name of the list to add the cards to
LIST_NAME = 'YOUR LIST NAME HERE'

def get_all_boards(key: str, token: str) -> list:
    """Get a list of all your Trello boards."""
    boards_data = []

    headers = {
        'Accept': 'application/json'
    }

    query = {
        'key': key,
        'token': token
    }
    # get the boards information
    response = requests.request(
        method='GET',
        url=BOARDS_URL,
        headers=headers,
        params=query
    )

    for board in response.json():
        boards_data.append({'id': board['id'], 'name': board['name']})
    
    return boards_data 

def get_lists_for_board(key: str, token: str, board_id: str) -> list:
    """Get all of the lists on a given board."""
    lists_data = []

    lists_url = BASE_API_URL + '/1/boards/{}/lists'.format(board_id)

    headers = {
        'Accept': 'application/json'
    }

    query = {
        'key': key,
        'token': token
    }

    response = requests.request(
        method='GET',
        url=lists_url,
        headers=headers,
        params=query
    )

    for list_item in response.json():
        lists_data.append({'id': list_item['id'], 'name':list_item['name']})

    return lists_data

def process_schedule() -> list:
    """Take a CSV and extract data to use on Trello Cards from each row."""
    items = []
    # change this to whatever CSV file you're pulling from
    with open('data/csc-414-schedule.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        # skips the empty strings at the top of this CSV file
        next(csv_reader)

        # skips the header
        next(csv_reader)

        for row in csv_reader:
            date, lecture, topic, req_readings, addtl_readings, _ = row
            # get the month abbreviation and day
            mnth_abbr, day = date.strip().split(' ')
            # get the index of the month by abbreviation (e.g. 'Jan' -> 1)
            mnth_idx = list(calendar.month_abbr).index(mnth_abbr)
            day = int(day)

            # string replacement handling the weird formatting of the CSV I was using
            topic = topic.strip().replace('\n', '--').replace('----', '--').replace('--', ' || ')

            req_readings = req_readings.strip().split('\n')
            addtl_readings = addtl_readings.strip().split('\n')

            # add relevant data to a tuple
            items.append((mnth_idx, day, lecture, topic, req_readings, addtl_readings))

    return items

def create_card(key: str, token: str, card_details: tuple) -> str:
    """Create a card and return the ID of the created card."""
    headers = {
        'Accept': 'application/json'
    }

    # get ID of Life Management Board
    lm_board_id = None
    for board in get_all_boards(API_KEY, API_TOKEN):
        if board['name'] == BOARD_NAME:
            lm_board_id = board['id']

    # get ID of list named "To Do"
    todo_list_id = None
    for board_list in get_lists_for_board(API_KEY, API_TOKEN, lm_board_id):
        if board_list['name'] == LIST_NAME:
            todo_list_id = board_list['id']

    query = {
        'key': key,
        'token': token,
        'idList': todo_list_id,
        'pos': 'bottom'
    }

    mnth, day, lecture, topic, req_readings, addtl_readings = card_details
    # 5 PM EST, 6 PM EDT, 10 PM UTC
    if day < 10:
        due = '2021-0{}-0{}T22:00:00.000Z'.format(mnth, day)
    else:
        due = '2021-0{}-{}T22:00:00.000Z'.format(mnth, day)

    query['name'] = '{}: {}'.format(lecture, topic)
    query['due'] = due
    query['idLabels'] = [CSC_414_LABEL_ID]


    response = requests.request(
        method='POST',
        url=CARDS_URL,
        headers=headers,
        params=query
    )

    response_data = json.loads(response.text)
    try:
        card_id = response_data['id']
        return card_id
    except:
        print('Request was: {}\nResponse was: {}\nCode: {}\nReason: {}'.format(query, response.text, response.status_code, response.reason))
        raise

def create_checklist(key: str, token: str, card_id: str, checklist_name: str) -> str:
    """Create a checklist with the given name and return the ID."""
    headers = {
        'Accept': 'application/json'
    }

    query = {
        'key': key,
        'token': token,
        'idCard': card_id,
        'name': checklist_name,
        'pos': 'bottom'
    }

    response = requests.request(
        method='POST',
        url=CHECKLIST_URL,
        headers=headers,
        params=query
    )
    response_data = json.loads(response.text)
    try:
        checklist_id = response_data['id']
        return checklist_id
    except:
        print('Request was: {}\nResponse was: {}\nCode: {}\nReason: {}'.format(query, response.text, response.status_code, response.reason))
        raise

def add_item_to_checklist(key: str, token: str, checklist_id: str, item_name: str):
    """Add an item to the given checklist."""
    add_item_url = BASE_API_URL + '/1/checklists/{}/checkItems'.format(checklist_id)

    headers = {
        'Accept': 'application/json'
    }

    query = {
        'key': key,
        'token': token,
        'id': checklist_id,
        'name': item_name,
        'pos': 'bottom'
    }

    response = requests.request(
        method='POST',
        url = add_item_url,
        headers=headers,
        params=query
    )

if __name__ == '__main__':
    # get all items from the schedule
    items = process_schedule()

    checklist_names = ['Required Readings', 'Additional Readings']
    for item in items:
        reqd_readings = item[4]
        addtl_readings = item[5]
        card_id = create_card(API_KEY, API_TOKEN, item)
        checklist_ids = [create_checklist(API_KEY, API_TOKEN, card_id, chkname) for chkname in checklist_names]
        rqd_checklist_id, addtl_checklist_id = checklist_ids

        # add required readings first
        for reading in reqd_readings:
            if bool(reading):
                add_item_to_checklist(API_KEY, API_TOKEN, rqd_checklist_id, reading)

        # then add additional readings
        for reading in addtl_readings:
            if bool(reading):
                add_item_to_checklist(API_KEY, API_TOKEN, addtl_checklist_id, reading)

        time.sleep(2)
       