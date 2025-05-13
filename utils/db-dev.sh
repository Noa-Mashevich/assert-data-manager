#!/bin/zsh

ENVIRONMENT="dev"
SNAPSHOT_ARN=""
PARAMETERS="VpcId=vpc-0df37fa28593dad4e PrivateSubnets=subnet-0bc5a566f52ea1e09,subnet-0aa84d4f12dbfb323 DeploymentEnv=${ENVIRONMENT} Database=studio InstanceType=db.t4g.small Storage=5 HighlyAvailable=false SnapshotARN=${SNAPSHOT_ARN}"

echo "build"
sam build \
  --template-file "../db.yml" \
  --parameter-overrides "${PARAMETERS}"

echo "deploy"
sam deploy \
  --stack-name "e2e-${ENVIRONMENT}-studio-db" \
  --template-file "../db.yml" \
  --parameter-overrides "${PARAMETERS}" \
  --s3-bucket aws-sam-cli-managed-default-samclisourcebucket-28m720vdnyft \
  --s3-prefix "e2e_${ENVIRONMENT}_studio" \
  --capabilities CAPABILITY_IAM \
  --no-confirm-changeset \
  --no-fail-on-empty-changeset

# aws cloudformation delete-stack --stack-name e2e-dev-studio-db