FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt ./requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application code
COPY . ./

# Create directories for uploaded, parsed, edited and summarized files
RUN mkdir -p uploaded_files parsed_files edited_files summarized_files bm25_indexes

# Expose the port the app runs on - use PORT env variable with fallback to 8004
ENV PORT=${PORT:-8004}
EXPOSE ${PORT}

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# NOTE: The following environment variables MUST be provided when running the container:
# - OPENAI_API_KEY
# - LLAMA_CLOUD_API_KEY
# - PINECONE_API_KEY
# - PINECONE_ENVIRONMENT
# Either use --env-file or specify them individually with -e flags

# Command to run the application - use PORT env variable with fallback to 8004
CMD uvicorn app:app --host 0.0.0.0 --port ${PORT} 