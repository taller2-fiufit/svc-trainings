import pytest
import asyncio


# https://stackoverflow.com/questions/71925980/cannot-perform-operation-another-operation-is-in-progress-in-pytest
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
