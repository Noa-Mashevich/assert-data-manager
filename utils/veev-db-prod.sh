#!/bin/zsh

ENVIRONMENT="prod"
SNAPSHOT_ARN=""
PARAMETERS="VpcId=vpc-04272b09bec7fff46 PrivateSubnets=subnet-0a2e7eff6a926b41b,subnet-063b9bba84394990a DeploymentEnv=${ENVIRONMENT} Database=studio InstanceType=db.t4g.small Storage=20 HighlyAvailable=true SnapshotARN=${SNAPSHOT_ARN}"

echo "build"
sam build \
  --template-file "../db.yml" \
  --parameter-overrides "${PARAMETERS}"

echo "deploy"
sam deploy \
  --stack-name "veev-${ENVIRONMENT}-studio-db" \
  --template-file "../db.yml" \
  --parameter-overrides "${PARAMETERS}" \
  --s3-bucket veev-aws-sam-cli-managed2 \
  --s3-prefix "veev_${ENVIRONMENT}_studio" \
  --region us-east-1 \
  --capabilities CAPABILITY_IAM \
  --no-confirm-changeset \
  --no-fail-on-empty-changeset