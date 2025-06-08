from datetime import datetime
import os
from redis import Redis, RedisError
from typing import Any, Dict, List

def get_redis_connection() -> Redis:
    """Create and return a Redis connection using environment variables."""
    return Redis(
        host=os.getenv("REDIS_HOST"),
        port=int(os.getenv("REDIS_PORT")),
        password=os.getenv("REDIS_PWD"),
        decode_responses=True
    )

redis_conn = get_redis_connection()

def redis_queue_add(job_id: str, user_id: str, priority: int, task_function: str, input: str) -> bool:
    """
    Add a job to the queue.
    
    Args:
        job_id (str): Unique identifier for the job.
        user_id (str): Identifier for the user associated with the job.
        priority (int): Priority level of the job.
        task_function (str): Name of the function to execute.
        input (str): Input to be passed to the task function.
        
    Returns:
        bool: True if the job was added to the queue, False otherwise.
    """
    if not job_id or not user_id or not priority or not task_function or not input:
        raise ValueError("Job ID, user ID, priority, task function, and input must not be empty")

    try:
        if redis_conn.ping():
            redis_conn.zadd("task_queue", {job_id: priority})
            redis_conn.hset("task_data:"+job_id, mapping={"user_id": user_id, "task_function": task_function, "input": input, "status": "pending", "retry": 0, "created_at": datetime.now().isoformat(), "response": ""})
            return True
    except RedisError as e:
        # Log error appropriately in production
        print(f"Redis error: {e}")
    return False

def redis_queue_get(job_id: str) -> Dict[str, Any] | str:
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

def redis_get_queue_items() -> str | None:
    try:
        if redis_conn.ping():
            task = redis_conn.zpopmax("task_queue", 1)
            if task:
                return task[0][0]
    except RedisError as e:
        # Log error appropriately in production
        print(f"Redis error: {e}")
    return None

def redis_get_queue_data(job_id: str) -> Dict[str, Any] | str:
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

def redis_queue_data_change_status(job_id: str, status: str) -> Dict[str, Any] | str:
    try:
        if redis_conn.ping():
            job_data = redis_conn.hgetall("task_data:"+job_id)
            if job_data:
                job_data["status"] = status
                redis_conn.hset("task_data:"+job_id, mapping=job_data)
                return True
            else:
                return "Job not found"
    except RedisError as e:
        # Log error appropriately in production
        print(f"Redis error: {e}")
    return "Redis connection error"
