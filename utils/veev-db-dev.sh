#!/bin/zsh

ENVIRONMENT="dev"
SNAPSHOT_ARN=""
PARAMETERS="VpcId=vpc-0472ea68c16693fcf PrivateSubnets=subnet-0042ba85a0b0681e7,subnet-01a1227b58daca793 DeploymentEnv=${ENVIRONMENT} Database=studio InstanceType=db.t4g.small Storage=5 HighlyAvailable=false SnapshotARN=${SNAPSHOT_ARN}"

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
  --capabilities CAPABILITY_IAM \
  --no-confirm-changeset \
  --no-fail-on-empty-changeset

# aws cloudformation delete-stack --stack-name e2e-dev-studio-db