FROM python:3.10-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p .streamlit data/streams/drivers

# Create secrets.toml file
RUN mkdir -p .streamlit && \
    echo 'API_BASE = "http://localhost:8000"' > .streamlit/secrets.toml

# Expose port for the API
EXPOSE 8000

# Command to run the application
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]