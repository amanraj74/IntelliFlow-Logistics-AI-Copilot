FROM python:3.10-slim

WORKDIR /app

# Install system dependencies needed for Pathway + ML libs
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Copy Pathway requirements
COPY requirements-pathway.txt .

# Install dependencies (Pathway + FastAPI + Streamlit + ML)
RUN pip install --no-cache-dir -r requirements-pathway.txt


# Copy the full application
COPY . .

# Create necessary directories
RUN mkdir -p data/streams data/output .streamlit

# Streamlit config
RUN echo 'API_BASE = "http://backend:9000"' > .streamlit/secrets.toml

# Expose ports
EXPOSE 8000 8501

# Start services
COPY scripts/start.sh .
RUN chmod +x start.sh

CMD ["./start.sh"]
