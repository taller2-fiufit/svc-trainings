from boto3.session import Session

# TODO: poetry add boto3

# TODO: get from env
AWS_ACCESS_KEY_ID = ""
AWS_SECRET_ACCESS_KEY = ""
QUEUE_NAME = ""

# Initiate session
session = Session(aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

# TODO: deactivate metrics when not in main deployment. Alt: use message_group_id to filter.

# Create SQS resource
sqs = session.resource('sqs')

# Get queue by name
queue = sqs.get_queue_by_name(QUEUE_NAME)


# Send message to SQS queue
response = queue.send_message(
    MessageBody= "string",
    MessageAttributes={},
    MessageDeduplicationId="string",
    MessageGroupId="metrics",
)
