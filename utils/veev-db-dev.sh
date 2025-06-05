#!/bin/zsh

ENVIRONMENT="dev"
SNAPSHOT_ARN=""
PARAMETERS="VpcId=vpc-07fd53624ee8e82e8 PrivateSubnets=subnet-00def7448f25aa454,subnet-02b9f68ab2eb0503a DeploymentEnv=${ENVIRONMENT} Database=studio InstanceType=db.t4g.small Storage=5 HighlyAvailable=false SnapshotARN=${SNAPSHOT_ARN}"

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