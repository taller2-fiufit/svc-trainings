import os

# AWS access key details
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID") or ""
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY") or ""

# Region
SQS_REGION = os.environ.get("SQS_REGION") or ""

# Name of the queue
SQS_QUEUE_NAME = os.environ.get("SQS_QUEUE_NAME") or ""
