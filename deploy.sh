#!/bin/bash

aws cloudformation package --s3-bucket sam-deployments-941817831 --template-file template.yml --output-template-file packaged-template.yml && aws cloudformation deploy --template-file packaged-template.yml --stack-name mcpanel --capabilities CAPABILITY_IAM
