from typing import Any, Dict
from helpers.redis import redis_queue_add, redis_queue_get


def queue_doc_task(user_id: str, job_id: str, priority: int, input: str) -> bool:
    return redis_queue_add(job_id, user_id, priority, "process_doc", input)

def queue_link_task(user_id: str, job_id: str, priority: int, input: str) -> bool:
    return redis_queue_add(job_id, user_id, priority, "process_link", input)
 
def queue_status(job_id: str) -> Dict[str, Any] | str:
    return redis_queue_get(job_id)


# queue_type: doc, link
# job_id: str
# user_id: str
# priority: int
# status: pending, completed, failed
# task_function: str
# input: str