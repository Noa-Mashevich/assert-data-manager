import logging
import signal

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection, reset_queries, close_old_connections
from sentry_sdk import capture_exception


logger = logging.getLogger(__name__)


def close_db():
    reset_queries()
    close_old_connections()
    connection.close()


def signal_handler(signal, frame):
    global run
    run = False
    logger.warning('Received signal to stop polling')
    close_db()


class Poller(BaseCommand):
    def handle(self, *args, **options):
        global run
        run = True
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        settings.DATABASES['default']['CONN_MAX_AGE'] = 0
        try:
            while run:
                self.poll()
        except BaseException as e:
            logger.exception(e)
            capture_exception(e)
        finally:
            close_db()

    def poll(self):
        response = settings.AWS_CLIENT_SQS.receive_message(
            QueueUrl=self.sqs_queue_url,
            MaxNumberOfMessages=10,
            VisibilityTimeout=10,
            WaitTimeSeconds=15,
        )
        messages = response.get('Messages', [])

        count = len(messages)
        if count > 0:
            logger.warning(f'Received {count} messages')

        for message in messages:
            message_id = message['MessageId']
            logger.warning(f'Processing message {message_id}')
            try:
                body = message['Body']
                receipt_handle = message['ReceiptHandle']
                self.handler(body)
                settings.AWS_CLIENT_SQS.delete_message(
                    QueueUrl=self.sqs_queue_url,
                    ReceiptHandle=receipt_handle,
                )
            except BaseException as e:
                logger.error(f'Failed to process message {message_id} with body {body}')
                logger.exception(e)
                capture_exception(e)
            finally:
                close_db()
