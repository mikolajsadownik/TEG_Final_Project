# backend/src/app.py
import logging
from services.service import run_backend_service
import time

def main():
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting Backend service...")
    run_backend_service()
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
