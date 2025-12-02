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
    
    # Log request context for security auditing
    request_context = event.get("requestContext", {})
    logger.info(json.dumps({
        "event": "request_received",
        "request_id": context.request_id,
        "source_ip": request_context.get("identity", {}).get("sourceIp"),
        "user_agent": request_context.get("identity", {}).get("userAgent"),
        "request_time": request_context.get("requestTime"),
        "table": table,
    }))
    
    try:
        if event.get("body"):
            item = json.loads(event["body"])
            logger.info(json.dumps({
                "event": "processing_request",
                "item_id": item.get("id"),
            }))
            
            year = str(item["year"])
            title = str(item["title"])
            id = str(item["id"])
            
            dynamodb_client.put_item(
                TableName=table,
                Item={"year": {"N": year}, "title": {"S": title}, "id": {"S": id}},
            )
            
            logger.info(json.dumps({
                "event": "dynamodb_write_success",
                "item_id": id,
                "table": table,
            }))
            
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"message": "Successfully inserted data!"}),
            }
        else:
            logger.info(json.dumps({"event": "no_payload_received"}))
            default_id = str(uuid.uuid4())
            
            dynamodb_client.put_item(
                TableName=table,
                Item={
                    "year": {"N": "2012"},
                    "title": {"S": "The Amazing Spider-Man 2"},
                    "id": {"S": default_id},
                },
            )
            
            logger.info(json.dumps({
                "event": "dynamodb_write_success",
                "item_id": default_id,
                "table": table,
            }))
            
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"message": "Successfully inserted data!"}),
            }
    except Exception as e:
        logger.error(json.dumps({
            "event": "error",
            "error_type": type(e).__name__,
            "error_message": str(e),
            "request_id": context.request_id,
        }))
        raise
