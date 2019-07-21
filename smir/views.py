import datetime
import json

from django.shortcuts import render, redirect
from googleapiclient.discovery import build
from smir.models import UserCredentials
from .utils import refresh_token
from .mqtt import client


def index(request):
    if request.user.is_authenticated:
        try:
            UserCredentials.objects.get(user=request.user)
            return redirect('/profile')
        except UserCredentials.DoesNotExist:
            return redirect('user_face_data')

    else:
        return redirect('/login')


def my_login(request):
    return render(request, 'login.html')


def profile(request):
    creds = refresh_token(request.user.username)
    service = build('gmail', 'v1', credentials=creds)

    # Call the Gmail API
    results = service.users().labels().list(userId=request.user.username).execute()
    labels = results.get('labels', [])

    if not labels:
        print('No labels found.')
    else:
        print('Labels:')
        for label in labels:
            print(label['name'])
    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])
    print(events)
    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])

    task_service = build('tasks', 'v1', credentials=creds)

    # Call the Tasks API
    results = task_service.tasklists().list(maxResults=10).execute()
    items = results.get('items', [])
    user_tasks = []
    if not items:
        print('No task lists found.')
    else:
        print('Task lists:')
        for item in items:
            print(u'{0} ({1})'.format(item['title'], item['id']))
            tasks = task_service.tasks().list(tasklist=item['id']).execute()
            for task in tasks['items']:
                user_tasks.append(task['title'])
        print(user_tasks)
        tasks_json = json.dumps(user_tasks)
        client.publish(topic="user/info", payload=tasks_json)
    return render(request, 'profile.html', {'events': events})
