from enum import Enum

import boto3
from crhelper import CfnResource

helper = CfnResource()
ecs = boto3.client('ecs')


class TaskStatus(Enum):
    RUNNING = 0
    STOPPED_ERROR = 1
    STOPPED_OK = 2


def get_task(cluster, task_arn):
    response_tasks = ecs.describe_tasks(
        cluster=cluster,
        tasks=[task_arn]
    )
    tasks = response_tasks['tasks']

    if not tasks:
        raise Exception('Task {} not found'.format(task_arn))

    return tasks[0]


def get_task_status(instance):
    status = instance['lastStatus']
    print('Task status {}'.format(status))
    if status != 'STOPPED':
        return TaskStatus.RUNNING

    containers = instance['containers']
    for container in containers:
        exit_code = container['exitCode']
        print('Migration exit code {}'.format(exit_code))
        if exit_code > 0:
            return TaskStatus.STOPPED_ERROR

    return TaskStatus.STOPPED_OK


@helper.poll_create
@helper.poll_update
def poll(event, context):
    properties = event['ResourceProperties']
    cluster = properties['Cluster']
    task_arn = properties['TaskArn']

    task = get_task(cluster, task_arn)

    task_status = get_task_status(task)
    if task_status == TaskStatus.STOPPED_ERROR:
        raise Exception('The migration failed')
        # Use for migration debugging:
        # print('The migration failed')
        # return True
    elif task_status == TaskStatus.STOPPED_OK:
        print('The migration completed')
        return True

    print('The migration is still running')
    return None


def handler(event, context):
    helper(event, context)
