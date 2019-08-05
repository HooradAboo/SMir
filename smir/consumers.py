import datetime
import json

import requests
from channels import Group
from googleapiclient.discovery import build

from smir.models import UserCredentials
from smir.mqtt import client
from smir.utils import refresh_token


def on_ws_connect(message):
    message.reply_channel.send({"accept": True})
    Group("mqtt").add(message.reply_channel)


def on_ws_disconnect(message):
    Group("mqtt").discard(message.reply_channel)


def on_mqtt_message(message):
    topic = message.content["topic"]
    payload = message.content["payload"].decode("utf-8")
    msg = "{}: {}".format(topic, payload)
    print(payload)
    if topic == 'user/request_info' or topic == 'camera/signup/done':
        try:
            UserCredentials.objects.get(user__username=payload)
            creds = refresh_token(payload)
            weather = requests.get(
                'http://api.openweathermap.org/data/2.5/weather?q=Tehran&appid=27929b8af5125779eaa943429a05ef19&units=metric')
            service = build('calendar', 'v3', credentials=creds)
            time = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
            print('Getting the upcoming 10 events')
            events_result = service.events().list(calendarId='primary', timeMin=time,
                                                  maxResults=10, singleEvents=True,
                                                  orderBy='startTime').execute()
            events = events_result.get('items', [])
            user_events = []
            if not events:
                user_events = 'No upcoming events found.'
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                user_events.append({'event': event['summary'], 'date': start})
            print(user_events)
            task_service = build('tasks', 'v1', credentials=creds)
            results = task_service.tasklists().list(maxResults=10).execute()
            items = results.get('items', [])
            all_tasks = []
            if not items:
                all_tasks = 'No task lists found.'
            else:
                for item in items:
                    user_tasks = []
                    tasks = task_service.tasks().list(tasklist=item['id']).execute()
                    tasks = tasks.get('items', [])
                    if tasks:
                        for task in tasks:
                            user_tasks.append(task['title'])
                    all_tasks.append({'task_list': item['title'], 'tasks': user_tasks})
                print(all_tasks)
            data = {'calendar': user_events, 'tasks': all_tasks, 'weather': weather.json(), 'name': payload}
            data_json = json.dumps(data)
            client.publish(topic="user/info", payload=data_json)
        except UserCredentials.DoesNotExist:
            client.publish(topic="user/info", payload="User not found")
