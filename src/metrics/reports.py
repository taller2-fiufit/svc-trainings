from datetime import datetime
import json
from typing import Callable

from pydantic import BaseModel

from src.metrics.queue import QUEUE


MESSAGE_GROUP_ID = "metrics"
DEDUPLICATION_PREPEND = "trainings"


class UidCounter:
    counter = 0

    @classmethod
    def next(cls) -> str:
        cls.counter += 1
        return f"{DEDUPLICATION_PREPEND}-{cls.counter}"


class TrainingCreationReport(BaseModel):
    service: str = "trainings"
    command: str = "trainingCreated"
    timestamp: datetime


def report_training_creation() -> None:
    body = json.dumps(TrainingCreationReport(timestamp=datetime.now()))
    # Send message to SQS queue
    _ = QUEUE.send_message(
        MessageBody=body,
        # MessageAttributes={},
        MessageDeduplicationId=UidCounter.next(),
        MessageGroupId=MESSAGE_GROUP_ID,
    )


def get_reporter() -> Callable[[], None]:
    return report_training_creation
