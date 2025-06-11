from datetime import datetime
import os
from redis import Redis, RedisError
from typing import Any, Dict
from dotenv import load_dotenv

load_dotenv()
def get_redis_connection() -> Redis:
    """Create and return a Redis connection using environment variables."""
    return Redis(
        host=os.getenv("REDIS_HOST"),
        port=int(os.getenv("REDIS_PORT")),
        password=os.getenv("REDIS_PWD"),
        decode_responses=True
    )

redis_conn = get_redis_connection()

def redis_list_add(key: str, value: str) -> bool:
    try:
        if redis_conn.ping():
            redis_conn.lpush(key, value)
            return True
    except RedisError as e:
        print(f"Redis error: {e}")
    return False

def redis_queue_add(job_id: str, user_id: str, task_function: str, input: str, doc_id: str) -> bool:
    """
    Add a job to the queue.
    
    Args:
        job_id (str): Unique identifier for the job.
        user_id (str): Identifier for the user associated with the job.
        task_function (str): Name of the function to execute.
        input (str): Input to be passed to the task function.
        
    Returns:
        bool: True if the job was added to the queue, False otherwise.
    """
    if not job_id or not user_id or not task_function or not input:
        raise ValueError("Job ID, user ID, task function, and input must not be empty")

    try:
        if redis_conn.ping():
            redis_conn.lpush("task_queue", job_id)
            redis_conn.hset("task_data:"+job_id, mapping={"user_id": user_id, "task_function": task_function, "input": input, "status": "pending", "retry": 0, "created_at": datetime.now().isoformat(), "doc_id": doc_id, "response": ""})
            return True
    except RedisError as e:
        # Log error appropriately in production
        print(f"Redis error: {e}")
    return False

def redis_queue_get_data(job_id: str) -> Dict[str, Any] | str:
    """
    Get the status of a job from the queue.
    
    Args:
        job_id (str): Unique identifier for the job.
        
    Returns:
        Dict[str, Any]: Job data if found, otherwise error message.
    """
    try:
        if redis_conn.ping():
            job_data = redis_conn.hgetall("task_data:"+job_id)
            if job_data:
                return job_data
            else:
                return "Job not found"
    except RedisError as e:
        # Log error appropriately in production
        print(f"Redis error: {e}")
    return "Redis connection error"

def redis_get_queue_item(timeout: int = 15) -> str | None:
    try:
        if redis_conn.ping():
            task = redis_conn.brpop("task_queue", timeout=timeout)
            if task:
                redis_list_add("task_processed", task[1])
                return task[1]
    except RedisError as e:
        # Log error appropriately in production 
        print(f"Redis error: {e}")
    return None

def redis_queue_data_change_status(job_id: str, status: str, response: str) -> Dict[str, Any] | str:
    try:
        if redis_conn.ping():
            job_data = redis_conn.hgetall("task_data:"+job_id)
            if job_data:
                job_data["status"] = status
                job_data["response"] = response
                redis_conn.hset("task_data:"+job_id, mapping=job_data)
                return True
            else:
                return "Job not found"
    except RedisError as e:
        # Log error appropriately in production
        print(f"Redis error: {e}")
    return "Redis connection error"
