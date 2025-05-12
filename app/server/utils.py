import json
import sys

from django.conf import settings


def is_migration():
    return (
        'makemigrations' in sys.argv
        or 'showmigrations' in sys.argv
        or 'migrate' in sys.argv
        or 'flush' in sys.argv
    )


def is_test():
    return 'test' in sys.argv


def get_object(key):
    from studio.models.stack import Stack

    if is_test() or is_migration():
        return 'placeholder_message_id'

    s3_bucket = Stack.objects.output(
        settings.AWS_REGION, settings.AWS_STACK_STORAGE, 'Bucket'
    )
    response = settings.AWS_CLIENT_S3.get_object(Bucket=s3_bucket, Key=key)
    return response


def put_object(key, body):
    from studio.models.stack import Stack

    if is_test() or is_migration():
        return 'placeholder_message_id'

    s3_bucket = Stack.objects.output(
        settings.AWS_REGION, settings.AWS_STACK_STORAGE, 'Bucket'
    )
    settings.AWS_CLIENT_S3.put_object(Bucket=s3_bucket, Key=key, Body=body)


def copy_object(source_key, target_key):
    from studio.models.stack import Stack

    if is_test() or is_migration():
        return 'placeholder_message_id'

    s3_bucket = Stack.objects.output(
        settings.AWS_REGION, settings.AWS_STACK_STORAGE, 'Bucket'
    )
    settings.AWS_CLIENT_S3.copy_object(
        Bucket=s3_bucket,
        CopySource=f'/{s3_bucket}/{source_key}',
        Key=target_key,
        ACL='private',
    )


def invoke_lambda(lambda_arn, payload):
    json_payload = json.dumps(payload)
    payload = bytes(json_payload, encoding='utf8')

    response = settings.AWS_CLIENT_LAMBDA.invoke(FunctionName=lambda_arn, Payload=payload)

    payload = response.get('Payload', '').read().decode('utf-8')
    status_code = response.get('StatusCode')
    execution_error = response.get('FunctionError', '')
    if status_code >= 400 or execution_error:
        error_message = (
            f"{lambda_arn} invocation failed. "
            f"StatusCode: {status_code}; "
            f"FunctionError: '{execution_error}'; "
            f"Payload: `{payload}`"
        )
        raise Exception(error_message)

    return json.loads(payload)
