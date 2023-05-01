import os

# AWS access key details
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID") or ""
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY") or ""

# Name of the queue
SQS_QUEUE_URL = os.environ.get("SQS_QUEUE_URL") or ""
