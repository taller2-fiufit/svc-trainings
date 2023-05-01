from typing import Mapping
from mypy_boto3_sqs.type_defs import MessageAttributeValueTypeDef

from src.logging import info


class LoggingQueue:
    url: str = "https://sqs.ex-north-x.amazonaws.example.com/xx/TestQueue.fifo"

    def send_message(
        self,
        MessageBody: str = "",
        MessageAttributes: Mapping[str, MessageAttributeValueTypeDef] = {},
        MessageDeduplicationId: str = "",
        MessageGroupId: str = "",
    ) -> None:
        msg = {
            "MessageBody": MessageBody,
            "MessageAttributes": MessageAttributes,
            "MessageDeduplicationId": MessageDeduplicationId,
            "MessageGroupId": MessageGroupId,
        }
        info(str(msg))
