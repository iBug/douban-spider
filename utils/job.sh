#!/bin/bash

case "$1" in
  1) REGION='ap-northeast-1';;
  2) REGION='ap-southeast-1';;
  3) REGION='us-west-2';;
  4) REGION='us-west-1';;
  *) exit 1;;
esac

case "$2" in
  1) ACTION='stop-instances';;
  2) ACTION='start-instances';;
  *) exit 1;;
esac

INSTANCES="$(aws --output text --region "$REGION" ec2 describe-instances --filters "Name=instance-type,Values=t2.nano,Name=instance-state-name,Values=stopped" --query "Reservations[].Instances[].InstanceId" | tr '[:space:]' ' ')"
echo "Instances: $INSTANCES"

if grep -qiP 'i-0[0-9a-f]+' <<< "$INSTANCES"; then
  echo "Running $ACTION on $REGION"
  aws --output json --region "$REGION" ec2 "$ACTION" --instance-ids $INSTANCES
fi
