import boto3
from crhelper import CfnResource

helper = CfnResource()
ecs = boto3.client('ecs')


def run_task(cluster, task_definition, subnets, security_groups):
    response = ecs.run_task(
        cluster=cluster,
        launchType='FARGATE',
        networkConfiguration={
            'awsvpcConfiguration': {
                'subnets': subnets,
                'securityGroups': security_groups
            }
        },
        taskDefinition=task_definition
    )
    return response['tasks'][0]['taskArn']


@helper.create
@helper.update
def migrate(event, context):
    properties = event['ResourceProperties']
    cluster = properties['Cluster']
    task_definition = properties['TaskDefinition']
    subnets = properties['Subnets']
    security_groups = properties['SecurityGroups']

    task_arn = run_task(cluster, task_definition, subnets, security_groups)

    helper.Data['TaskArn'] = task_arn
    return task_arn


def handler(event, context):
    helper(event, context)
