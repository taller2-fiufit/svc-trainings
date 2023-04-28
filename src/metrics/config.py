import os

# AWS access key details
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID") or ""
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY") or ""

# Region
SQS_REGION = "sa-east-1"

# Name of the queue
SQS_QUEUE_NAME = "MetricsQueue.fifo"
