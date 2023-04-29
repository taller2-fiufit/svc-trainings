from typing import Union
from boto3.session import Session
from mypy_boto3_sqs import SQSServiceResource
from mypy_boto3_sqs.service_resource import Queue

from src.metrics.config import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    SQS_QUEUE_NAME,
    SQS_REGION,
)
from src.metrics.logging_queue import LoggingQueue


def env_was_initialized() -> bool:
    return (
        AWS_ACCESS_KEY_ID != ""
        and AWS_SECRET_ACCESS_KEY != ""
        and SQS_REGION != ""
        and SQS_QUEUE_NAME != ""
    )


def get_aws_queue() -> Queue:
    assert env_was_initialized()

    # Initiate session
    session = Session(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )

    # Create SQS resource
    sqs: SQSServiceResource = session.resource("sqs", region_name=SQS_REGION)

    # Get queue by name
    queue = sqs.get_queue_by_name(QueueName=SQS_QUEUE_NAME)

    return queue


QUEUE: Union[Queue, LoggingQueue] = (
    get_aws_queue() if env_was_initialized() else LoggingQueue()
)
