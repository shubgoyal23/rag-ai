from dotenv import load_dotenv
load_dotenv()
from worker.worker import queue_reader


def main():
    try:
        queue_reader()
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()
    