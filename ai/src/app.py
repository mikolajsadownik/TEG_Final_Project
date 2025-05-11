# ai/src/app.py
import logging
from services.service import run_ai_service
import time

def main():
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting AI service...")
    run_ai_service()
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
