#!/bin/zsh

ENVIRONMENT="stage"
SNAPSHOT_ARN=""
PARAMETERS="VpcId=vpc-0a6d03d7e95ed4751 PrivateSubnets=subnet-0757a35c00aa418ea,subnet-0ba3ee09261250f52 DeploymentEnv=${ENVIRONMENT} Database=studio InstanceType=db.t4g.large Storage=20 HighlyAvailable=false SnapshotARN=${SNAPSHOT_ARN}"

echo "build"
sam build \
  --template-file "../db.yml" \
  --parameter-overrides "${PARAMETERS}"

echo "deploy"
sam deploy \
  --stack-name "veev-${ENVIRONMENT}-studio-db" \
  --template-file "../db.yml" \
  --parameter-overrides "${PARAMETERS}" \
  --s3-bucket veev-aws-sam-cli-managed1 \
  --s3-prefix "veev_${ENVIRONMENT}_studio" \
  --region us-east-1 \
  --capabilities CAPABILITY_IAM \
  --no-confirm-changeset \
  --no-fail-on-empty-changeset

# aws cloudformation delete-stack --stack-name e2e-dev-studio-db