from dotenv import load_dotenv
load_dotenv()
from worker.worker import queue_reader


def main():
    print("Worker started")
    queue_reader()

if __name__ == "__main__":
    main()
    