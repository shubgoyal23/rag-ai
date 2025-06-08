
from helpers.redis import redis_get_queue_data, redis_get_queue_items, redis_queue_data_change_status
from helpers.storage import download_from_gcs

def process_doc(input: str):
    doc = download_from_gcs(input)
    pass

def process_link(input: str):
    pass


def queue_reader():
    while True:
        job_id = redis_get_queue_items()
        if job_id:
            job_data = redis_get_queue_data(job_id)
            if job_data:
                if job_data["status"] == "pending":
                    redis_queue_data_change_status(job_id, "in_progress")
                    if job_data["task_function"] == "process_doc":
                        process_doc(job_data["input"])
                    elif job_data["task_function"] == "process_link":
                        process_link(job_data["input"])
                    job_data["status"] = "completed"
                    redis_queue_data_change_status(job_id, "completed")