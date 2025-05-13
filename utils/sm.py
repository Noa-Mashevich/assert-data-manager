#!python
import boto3
import json


aws_client_sm = boto3.client('secretsmanager')

secret_id = 'dev.studio.DB_SECRET'
#response = aws_client_sm.delete_secret(
#    SecretId=secret_id,
#    ForceDeleteWithoutRecovery=True
#)
#print(response)

secret_value = {
    'hostname': 'x',
    'username': 'studio',
    'password': 'x'
}

response = aws_client_sm.create_secret(
    Name=secret_id,
    SecretString=json.dumps(secret_value),
)
print(response)

response = aws_client_sm.get_secret_value(
    SecretId=secret_id
)
print(response)
