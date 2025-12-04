# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

patch_all()

import boto3
import os
import json
import logging
import uuid

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb_client = boto3.client("dynamodb")


def handler(event, context):
    table = os.environ.get("TABLE_NAME")
    
    # Log security-relevant context
    logger.info(f"Request ID: {context.request_id}")
    logger.info(f"Function ARN: {context.invoked_function_arn}")
    logger.info(f"Request source IP: {event.get('requestContext', {}).get('identity', {}).get('sourceIp', 'unknown')}")
    logger.info(f"HTTP method: {event.get('httpMethod', 'unknown')}")
    logger.info(f"## Loaded table name from environemt variable DDB_TABLE: {table}")
    
    if event["body"]:
        item = json.loads(event["body"])
        logger.info(f"## Received payload with id: {item.get('id', 'unknown')}")
        year = str(item["year"])
        title = str(item["title"])
        id = str(item["id"])
        dynamodb_client.put_item(
            TableName=table,
            Item={"year": {"N": year}, "title": {"S": title}, "id": {"S": id}},
        )
        message = "Successfully inserted data!"
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": message}),
        }
    else:
        logger.info("## Received request without a payload")
        dynamodb_client.put_item(
            TableName=table,
            Item={
                "year": {"N": "2012"},
                "title": {"S": "The Amazing Spider-Man 2"},
                "id": {"S": str(uuid.uuid4())},
            },
        )
        message = "Successfully inserted data!"
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": message}),
        }
