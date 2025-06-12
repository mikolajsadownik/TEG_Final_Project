FROM python:3.11-slim

WORKDIR /app

# ----- zależności systemowe PDF → jeśli potrzebujesz pokazów PDF w UI -----
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential  && \
    rm -rf /var/lib/apt/lists/*

# ----- instalacja Pythona -----
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ----- kod źródłowy -----
COPY src ./src

EXPOSE 8501
CMD ["python", "-m", "streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
