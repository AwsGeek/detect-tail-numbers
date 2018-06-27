#!/bin/bash
region=$1
bucket=$2
stack=$3

aws --region $region cloudformation package --template-file template.yaml --s3-bucket $bucket --output-template-file package.yaml
aws --region $region cloudformation deploy --template-file package.yaml --stack-name $stack --capabilities CAPABILITY_IAM
