import json

from studio.models.file_notification import FileNotification

from .poller import Poller


class Command(Poller):
    def __init__(self):
        self.sqs_queue_url = FileNotification.objects.queue_url

    def handler(self, message):
        sns_message = json.loads(message)
        FileNotification.objects.create_from_queue(sns_message['Message'])
