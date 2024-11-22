import PySimpleGUI as sg
import datetime
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import json
import csv
from io import StringIO
import time
import calendar_functions as cf  # Import the functions from calendar_functions.py

# Load the credentials.json file
with open('credentials.json') as cred_file:
    creds_data = json.load(cred_file)

# Authenticate and create the service
flow = InstalledAppFlow.from_client_config(creds_data, scopes=['https://www.googleapis.com/auth/calendar'])
creds = flow.run_local_server(port=0)

service = build('calendar', 'v3', credentials=creds)

# Your calendar ID (usually your email)
calendar_id = '10614405@learner.hkuspace.hku.hk'

# Define the layout of the GUI
layout = [
    [sg.Text('Event Name:', size=(15, 1)), sg.InputText('Aldi', key='event_name')],
    [sg.Text('Event Color:', size=(15, 1)), sg.Combo(values=['None', 'Peacock', 'Grape', 'Tomato', 'Banana', 'Basil', 'Cucumber', 'Blueberry', 'Lavender'], key='event_color')],
    [sg.Text('Shifts CSV:', size=(15, 1)), sg.Multiline('date,start,end\n2024-10-01,12:00,21:00', size=(50, 10), key='shifts_csv')],
    [sg.Button('Load Shifts'), sg.Button('Submit')],
    [sg.HorizontalSeparator()],
    [sg.Listbox(values=[], size=(50, 10), key='shift_list')],
    [sg.Text('Total Working Hours:')],
    [sg.Text('First Fortnight:', size=(15, 1)), sg.Text('', key='first_fortnight_hours')],
    [sg.Text('Second Fortnight:', size=(15, 1)), sg.Text('', key='second_fortnight_hours')],
    [sg.HorizontalSeparator()],
    [sg.Text('Start Date (YYYY-MM-DD):', size=(20, 1)), sg.InputText(key='start_date')],
    [sg.Text('End Date (YYYY-MM-DD):', size=(20, 1)), sg.InputText(key='end_date')],
    [sg.Button('Delete Events')],
]

window = sg.Window('Google Calendar Event Creator', layout)

shifts = []

while True:
    event, values = window.read()
    
    if event in (sg.WIN_CLOSED, 'Cancel'):
        break

    if event == 'Load Shifts':
        try:
            csv_data = StringIO(values['shifts_csv'])
            reader = csv.DictReader(csv_data)
            shifts = [row for row in reader]
            window['shift_list'].update([f"Date: {s['date']}, Start: {s['start']}, End: {s['end']}" for s in shifts])
        except Exception as e:
            sg.popup_error(f'Error parsing CSV data: {e}')

    if event == 'Submit':
        try:
            event_name = values['event_name']
            event_color = values['event_color']
            
            cf.delete_existing_events(service, calendar_id, event_name, shifts)
            
            for shift in shifts:
                cf.add_event(service, calendar_id, event_name, event_color, shift)

            most_common_month, most_common_year = cf.find_most_frequent_month_and_year(shifts)
            first_thursday, third_thursday = cf.find_first_and_third_thursdays(most_common_month, most_common_year)

            first_fortnight_hours = 0
            second_fortnight_hours = 0

            if first_thursday:
                first_thursday_end = first_thursday + datetime.timedelta(days=13)
                first_fortnight_hours = cf.calculate_total_hours(shifts, first_thursday, first_thursday_end)

            if third_thursday:
                third_thursday_end = third_thursday + datetime.timedelta(days=13)
                second_fortnight_hours = cf.calculate_total_hours(shifts, third_thursday, third_thursday_end)

            window['first_fortnight_hours'].update(f"{first_fortnight_hours} hours")
            window['second_fortnight_hours'].update(f"{second_fortnight_hours} hours")
            
            sg.popup('Events Added! Your events have been added to Google Calendar.')
        except Exception as e:
            sg.popup_error(f'Error during submission: {e}')

    if event == 'Delete Events':
        try:
            event_name = values['event_name']
            start_date = values['start_date']
            end_date = values['end_date']
            
            cf.delete_events_within_range(service, calendar_id, event_name, start_date, end_date)
            
            sg.popup('Events Deleted! All events with the specified name within the date range have been removed.')
        except Exception as e:
            sg.popup_error(f'Error during deletion: {e}')

window.close()
