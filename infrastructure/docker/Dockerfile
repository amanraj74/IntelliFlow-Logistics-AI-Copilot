FROM python:3.8-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
COPY requirements-dev.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p data/streams data/output .streamlit

# Set up Streamlit config
RUN echo 'API_BASE = "http://backend:8000"' > .streamlit/secrets.toml

# Expose ports for FastAPI and Streamlit
EXPOSE 8000 8501

# Start both services using a shell script
COPY scripts/start.sh .
RUN chmod +x start.sh

CMD ["./start.sh"]
