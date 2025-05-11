# Biz To Bricks

A document processing and querying system with FastAPI backend and Streamlit frontend.

## Features

- Document upload and storage
- PDF parsing with LlamaParse
- Document editing and summarization
- Vector search with Pinecone
- Hybrid search combining dense vectors and sparse BM25 encoding

## Project Structure

- `server/` - FastAPI backend for document processing
- `client/` - Streamlit frontend for user interaction

## Environment Setup

Create a `.env` file in the project root with the following credentials:

```
OPENAI_API_KEY=your_openai_api_key
LLAMA_CLOUD_API_KEY=your_llama_cloud_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=your_pinecone_environment
```

## Running with Docker

### Build and run the server

```bash
# Navigate to the server directory
cd server

# Build the Docker image
docker build -t document-processing-server .

# Create necessary directories if they don't exist
mkdir -p uploaded_files parsed_files edited_files summarized_files bm25_indexes

# Run the server container - Method 1 (using --env-file)
# Make sure your .env file exists in the parent directory
docker run -d -p 8004:8004 --name doc-server \
  --env-file ../.env \
  -v $(pwd)/uploaded_files:/app/uploaded_files \
  -v $(pwd)/parsed_files:/app/parsed_files \
  -v $(pwd)/edited_files:/app/edited_files \
  -v $(pwd)/summarized_files:/app/summarized_files \
  -v $(pwd)/bm25_indexes:/app/bm25_indexes \
  document-processing-server

# Alternative Method 2 (specifying environment variables directly)
# docker run -d -p 8004:8004 --name doc-server \
#   -e OPENAI_API_KEY="your-openai-api-key" \
#   -e LLAMA_CLOUD_API_KEY="your-llama-cloud-api-key" \
#   -e PINECONE_API_KEY="your-pinecone-api-key" \
#   -e PINECONE_ENVIRONMENT="your-pinecone-environment" \
#   -v $(pwd)/uploaded_files:/app/uploaded_files \
#   -v $(pwd)/parsed_files:/app/parsed_files \
#   -v $(pwd)/edited_files:/app/edited_files \
#   -v $(pwd)/summarized_files:/app/summarized_files \
#   -v $(pwd)/bm25_indexes:/app/bm25_indexes \
#   document-processing-server
```

### Troubleshooting Docker

If you encounter an error related to missing API keys:

1. Verify your .env file exists and contains valid API keys
2. Check the file path in the --env-file flag (it should point to a valid .env file)
3. Try Method 2 above, directly specifying the environment variables
4. To see if env variables are set correctly, you can check the container:
   ```bash
   docker exec doc-server env | grep OPENAI
   ```

### Run the client (locally for now)

```bash
# Navigate to client directory from project root
cd client

# Install requirements
pip install -r requirements.txt

# Run the Streamlit app
streamlit run client.py
```

The server will be accessible at: http://localhost:8004
The client will be accessible at: http://localhost:8501

## API Documentation

Once the server is running, API documentation is available at:
- http://localhost:8004/docs - Swagger UI
- http://localhost:8004/redoc - ReDoc