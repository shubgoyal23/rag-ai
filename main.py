from dotenv import load_dotenv
from worker.worker import queue_reader
load_dotenv()
from helpers.server import app
import uvicorn


def main():
    # queue_reader()
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
    