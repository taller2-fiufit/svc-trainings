from boto3.session import Session
from mypy_boto3_sqs import SQSServiceResource
from mypy_boto3_sqs.service_resource import Queue

# TODO: get from env
AWS_ACCESS_KEY_ID = "ZLPMFFJKJKOJ6AFKSKAF"
AWS_SECRET_ACCESS_KEY = "LGJISas15b/khoksdms56551xdsgdsgsg3s1gd1+"
QUEUE_NAME = "MetricsQueue.fifo"
REGION = "sa-east-1"


def get_aws_queue() -> Queue:
    # Initiate session
    session = Session(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )

    # Create SQS resource
    sqs: SQSServiceResource = session.resource("sqs", region_name=REGION)

    # Get queue by name
    queue = sqs.get_queue_by_name(QueueName=QUEUE_NAME)

    return queue


QUEUE = get_aws_queue()
