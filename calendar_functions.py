# calendar_functions.py

import datetime
from googleapiclient.discovery import build
from collections import Counter

# Function to delete existing events within a date range
def delete_events_within_range(service, calendar_id, event_name, start_date, end_date):
    start_time = datetime.datetime.strptime(start_date, "%Y-%m-%d").isoformat() + 'Z'
    end_time = (datetime.datetime.strptime(end_date, "%Y-%m-%d") + datetime.timedelta(days=1)).isoformat() + 'Z'
    
    events_result = service.events().list(calendarId=calendar_id, timeMin=start_time, timeMax=end_time, singleEvents=True).execute()
    events = events_result.get('items', [])
    
    for event in events:
        if event['summary'] == event_name:
            service.events().delete(calendarId=calendar_id, eventId=event['id']).execute()

# Function to delete existing events
def delete_existing_events(service, calendar_id, event_name, shifts):
    start_date = min(shift["date"] for shift in shifts)
    end_date = max(shift["date"] for shift in shifts)
    
    start_time = datetime.datetime.strptime(start_date, "%Y-%m-%d").isoformat() + 'Z'
    end_time = (datetime.datetime.strptime(end_date, "%Y-%m-%d") + datetime.timedelta(days=1)).isoformat() + 'Z'
    
    events_result = service.events().list(calendarId=calendar_id, timeMin=start_time, timeMax=end_time, singleEvents=True).execute()
    events = events_result.get('items', [])
    
    for event in events:
        if event['summary'] == event_name:
            service.events().delete(calendarId=calendar_id, eventId=event['id']).execute()

# Function to add a new event using the system's timezone
def add_event(service, calendar_id, event_name, event_color, shift):
    date = shift["date"]
    start_time = datetime.datetime.strptime(date + " " + shift["start"], "%Y-%m-%d %H:%M")
    end_time = datetime.datetime.strptime(date + " " + shift["end"], "%Y-%m-%d %H:%M")
    
    color_ids = {
        'None': '0', 'Peacock': '7', 'Grape': '9', 'Tomato': '11',
        'Banana': '5', 'Basil': '2', 'Cucumber': '10',
        'Blueberry': '8', 'Lavender': '6'
    }
    
    # Set the timezone to 'Australia/Sydney'
    timezone = 'Australia/Sydney'
    
    start_time = start_time.isoformat()
    end_time = end_time.isoformat()
    
    event = {
        'summary': event_name,
        'start': {
            'dateTime': start_time,
            'timeZone': timezone,
        },
        'end': {
            'dateTime': end_time,
            'timeZone': timezone,
        },
        'colorId': color_ids[event_color],
    }
    
    service.events().insert(calendarId=calendar_id, body=event).execute()

# Function to find the most frequent month and year
def find_most_frequent_month_and_year(shifts):
    months = [datetime.datetime.strptime(shift["date"], "%Y-%m-%d").month for shift in shifts]
    years = [datetime.datetime.strptime(shift["date"], "%Y-%m-%d").year for shift in shifts]
    
    month_counts = Counter(months)
    year_counts = Counter(years)
    
    most_common_month, _ = month_counts.most_common(1)[0]
    most_common_year, _ = year_counts.most_common(1)[0]
    
    return most_common_month, most_common_year

# Function to find the first and third Thursdays
def find_first_and_third_thursdays(month, year):
    thursdays = []
    
    for day in range(1, 32): 
        try:
            date = datetime.datetime(year, month, day)
        except ValueError:
            break 
        
        if date.weekday() == 3:
            thursdays.append(date)
    
    if len(thursdays) < 3:
        return None, None  
    
    return thursdays[0], thursdays[2]

# Function to calculate total working hours
def calculate_total_hours(shifts, start_date, end_date):
    total_hours = 0
    for shift in shifts:
        shift_date = datetime.datetime.strptime(shift["date"], "%Y-%m-%d")
        if start_date <= shift_date <= end_date:
            start_time = datetime.datetime.strptime(shift["date"] + " " + shift["start"], "%Y-%m-%d %H:%M")
            end_time = datetime.datetime.strptime(shift["date"] + " " + shift["end"], "%Y-%m-%d %H:%M")
            shift_hours = (end_time - start_time).seconds / 3600
            total_hours += shift_hours
    return total_hours
