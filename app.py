from dotenv import load_dotenv
load_dotenv()
from worker.worker import queue_reader


def main():
    queue_reader()

if __name__ == "__main__":
    main()
    