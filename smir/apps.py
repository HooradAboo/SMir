from django.apps import AppConfig


class SmirConfig(AppConfig):
    name = 'smir'

    def ready(self):
        from smir.mqtt import client
        client.loop_start()
