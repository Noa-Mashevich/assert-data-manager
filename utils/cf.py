#!python
import boto3


aws_client_cf = boto3.client('cloudformation')

stack_name = 'test'
response = aws_client_cf.describe_stacks(
    StackName=stack_name
)
print(response)
