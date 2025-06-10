from helpers.redis import redis_get_queue_item, redis_queue_data_change_status, redis_queue_get_data
from worker.process_doc import process_doc_handler, process_links_handler, process_message_handler


def queue_reader():
    while True:
        try:
            job_id = redis_get_queue_item(timeout=0)
            if job_id:
                job_data = redis_queue_get_data(job_id)
                if job_data:
                    task = job_data["task_function"]
                    redis_queue_data_change_status(job_id, "processing", response="task started")
                    if task == "process_doc":
                        resp = process_doc_handler(job_id, job_data)
                    elif task == "process_link":
                        resp = process_links_handler(job_id, job_data)
                    elif task == "process_message":
                        resp = process_message_handler(job_id, job_data)
                        
                    if resp:
                        redis_queue_data_change_status(job_id, "completed", resp)
                    else:
                        redis_queue_data_change_status(job_id, "failed", response="Invalid task function")
        except Exception as e:
            print("queue_reader",e)
            redis_queue_data_change_status(job_id, "failed", response=str(e))
            