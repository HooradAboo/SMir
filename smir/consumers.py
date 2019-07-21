import json

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
    msg = "{}: {}".format(message.content["topic"],
                          message.content["payload"].decode("utf-8"))
    print(message.content["payload"].decode("utf-8"))
    if message.content["topic"] == 'user/request_info':
        try:
            UserCredentials.objects.get(user__username=message.content["payload"].decode("utf-8"))
            creds = refresh_token(message.content["payload"].decode("utf-8"))
            task_service = build('tasks', 'v1', credentials=creds)
            results = task_service.tasklists().list(maxResults=10).execute()
            items = results.get('items', [])
            user_tasks = []
            if not items:
                user_tasks = 'No task lists found.'
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
        except UserCredentials.DoesNotExist:
            client.publish(topic="user/info", payload="User not found")
    Group("mqtt").send({
        "text": msg
    })
