from dotenv import load_dotenv
from worker.worker import queue_reader
load_dotenv()
import uvicorn
# from helpers.server import app

def main():
    # queue_reader()
    uvicorn.run("helpers.server:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()
    