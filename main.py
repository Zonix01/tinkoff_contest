import asyncio
from enum import Enum
from typing import Optional
import concurrent.futures
from dataclasses import dataclass
from datetime import datetime, timedelta
import random


class Response(Enum):
    Success = 1
    RetryAfter = 2
    Failure = 3


class ApplicationStatusResponse(Enum):
    Success = 1
    Failure = 2


@dataclass
class ApplicationResponse:
    application_id: str
    status: ApplicationStatusResponse
    description: str
    last_request_time: datetime
    retriesCount: Optional[int]


async def get_application_status1(identifier: str) -> Response:
    return random.choice([x for x in Response])


async def get_application_status2(identifier: str) -> Response:
    return random.choice([x for x in Response])


async def perform_operation(identifier: str) -> ApplicationResponse:
    timeout_seconds = timedelta(seconds=15).total_seconds()
    loop = asyncio.get_running_loop()
    executor = concurrent.futures.ThreadPoolExecutor()

    retries_count = 0
    elapsed_time = 0
    start_time = datetime.utcnow()

    while elapsed_time < timeout_seconds:
        task1 = loop.run_in_executor(executor, get_application_status1, identifier)
        task2 = loop.run_in_executor(executor, get_application_status2, identifier)

        done, _ = await asyncio.wait({task1, task2})

        responses = [await task.result() for task in done]

        end_time = datetime.utcnow()
        elapsed_time = (end_time - start_time).total_seconds()

        if all(response == Response.Success for response in responses):
            status = ApplicationStatusResponse.Success
            description = "Both services succeeded"
            break
        elif any(response == Response.RetryAfter for response in responses):
            retries_count += 1
            await asyncio.sleep(1)
        else:
            status = ApplicationStatusResponse.Failure
            description = "Both or one services failed"
            break
    else:
        status = ApplicationStatusResponse.Failure
        description = "Operation timed out"

    return ApplicationResponse(identifier, status, description, end_time, retries_count)


async def main():
    application_id = 'example_id'
    application_response = await perform_operation(application_id)
    print(application_response)


if __name__ == '__main__':
    asyncio.run(main())
