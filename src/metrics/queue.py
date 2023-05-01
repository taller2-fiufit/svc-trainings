from typing import Union
from boto3.session import Session
from mypy_boto3_sqs import SQSServiceResource
from mypy_boto3_sqs.service_resource import Queue

from src.metrics.config import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    SQS_QUEUE_URL,
)
from src.metrics.logging_queue import LoggingQueue


def env_was_initialized() -> bool:
    return (
        AWS_ACCESS_KEY_ID != ""
        and AWS_SECRET_ACCESS_KEY != ""
        and SQS_QUEUE_URL != ""
    )


def get_aws_queue() -> Queue:
    assert env_was_initialized()

    # Initiate session
    session = Session(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )

    # Obtain region from queue's URL
    sqs_region = SQS_QUEUE_URL.split(".")[1]

    # Create SQS resource
    sqs: SQSServiceResource = session.resource("sqs", region_name=sqs_region)

    # Get queue by name
    queue = sqs.Queue(SQS_QUEUE_URL)

    return queue


QUEUE: Union[Queue, LoggingQueue] = (
    get_aws_queue() if env_was_initialized() else LoggingQueue()
)
