#!/bin/bash

sam build && \
    sam deploy \
        --s3-bucket sam-deployments-941817831 \
        --stack-name mcpanel \
        --capabilities CAPABILITY_IAM
