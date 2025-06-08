from dotenv import load_dotenv
load_dotenv()
import uvicorn
# from helpers.server import app

def main():
    uvicorn.run("helpers.server:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()
    