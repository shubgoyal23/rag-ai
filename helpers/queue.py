from typing import Any, Dict
from helpers.redis import redis_queue_add, redis_queue_get_data


def queue_task_helper(user_id: str, job_id: str, type: str, input: str, doc_id: str) -> bool:
    return redis_queue_add(job_id, user_id, type, input, doc_id)

 
def queue_status(job_id: str) -> Dict[str, Any] | str:
    return redis_queue_get_data(job_id)


# queue_type: doc, link
# job_id: str
# user_id: str
# priority: int
# status: pending, completed, failed
# task_function: str
# input: str