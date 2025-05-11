# Document Processing Server

A FastAPI server for uploading, parsing, editing, summarizing, and querying documents using LlamaParse, OpenAI, and Pinecone.

## Features

- Document upload and storage
- PDF parsing with LlamaParse
- Document editing and summarization
- Vector search with Pinecone
- Hybrid search combining dense vectors and sparse BM25 encoding

## Environment Setup

Before running the server, you need to create a `.env` file with the following credentials:

```
OPENAI_API_KEY=your_openai_api_key
LLAMA_CLOUD_API_KEY=your_llama_cloud_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=your_pinecone_environment
```

## Running with Docker

### Option 1: Build from project root

1. Build the Docker image from the project root:

```bash
# Run from project root directory
docker build -t document-processing-server -f server/Dockerfile .
```

2. Run the container:

```bash
# Create necessary directories if they don't exist
mkdir -p server/uploaded_files server/parsed_files server/edited_files server/summarized_files server/bm25_indexes

# Run the container
docker run -d -p 8004:8004 --name doc-server -e OPENAI_API_KEY=your-key-here -e LLAMA_CLOUD_API_KEY=your-key-here -e PINECONE_API_KEY=your-key-here -e PINECONE_ENVIRONMENT=your-env-here -v $(pwd)/server/uploaded_files:/app/uploaded_files -v $(pwd)/server/parsed_files:/app/parsed_files -v $(pwd)/server/edited_files:/app/edited_files -v $(pwd)/server/summarized_files:/app/summarized_files -v $(pwd)/server/bm25_indexes:/app/bm25_indexes document-processing-server
```

### Option 2: Build from server directory

1. Navigate to the server directory:

```bash
cd server
```

2. Build the Docker image:

```bash
docker build -t document-processing-server .
```

3. Run the container:

```bash
# Create necessary directories
mkdir -p uploaded_files parsed_files edited_files summarized_files bm25_indexes

# Run the container
docker run -d -p 8004:8004 --name doc-server -e OPENAI_API_KEY=your-key-here -e LLAMA_CLOUD_API_KEY=your-key-here -e PINECONE_API_KEY=your-key-here -e PINECONE_ENVIRONMENT=your-env-here -v $(pwd)/uploaded_files:/app/uploaded_files -v $(pwd)/parsed_files:/app/parsed_files -v $(pwd)/edited_files:/app/edited_files -v $(pwd)/summarized_files:/app/summarized_files -v $(pwd)/bm25_indexes:/app/bm25_indexes document-processing-server
```

The server will be accessible at: http://localhost:8004

## API Endpoints

- `POST /uploadfile/` - Upload a document
- `GET /listfiles/{directory}` - List files in a directory
- `GET /parsefile/{filename}` - Parse an uploaded file to markdown
- `POST /savecontent/{filename}` - Save edited content
- `GET /summarizecontent/{filename}` - Generate a summary for a file
- `POST /ingestdocuments/{filename}` - Ingest a document into Pinecone and BM25 indexes
- `POST /hybridsearch/` - Perform hybrid search query

## Document Processing Flow

1. Upload a document using `/uploadfile/`
2. Parse the document to markdown with `/parsefile/{filename}`
3. Edit the content if needed with `/savecontent/{filename}`
4. Summarize the document with `/summarizecontent/{filename}`
5. Ingest the document with `/ingestdocuments/{filename}`
6. Query the document with `/hybridsearch/`

## Docker Compose

# Create a docker-compose.yml file
cat > docker-compose.yml << 'EOF'
version: '3'
services:
  doc-server:
    image: document-processing-server
    ports:
      - "8004:8004"
    environment:
      - OPENAI_API_KEY=your-key-here
      - LLAMA_CLOUD_API_KEY=your-key-here
      - PINECONE_API_KEY=your-key-here
      - PINECONE_ENVIRONMENT=your-env-here
    volumes:
      - ./uploaded_files:/app/uploaded_files
      - ./parsed_files:/app/parsed_files
      - ./edited_files:/app/edited_files
      - ./summarized_files:/app/summarized_files
      - ./bm25_indexes:/app/bm25_indexes
EOF

# Run with docker-compose
docker-compose up -d 

# Navigate to server directory
cd server

# Enable Container Registry API if not enabled
gcloud services enable containerregistry.googleapis.com

# Build and tag the image
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/document-processing-server 

gcloud config set project YOUR_PROJECT_ID 

gsutil mb gs://YOUR_PROJECT_ID-uploaded-files
gsutil mb gs://YOUR_PROJECT_ID-parsed-files
gsutil mb gs://YOUR_PROJECT_ID-edited-files
gsutil mb gs://YOUR_PROJECT_ID-summarized-files
gsutil mb gs://YOUR_PROJECT_ID-bm25-indexes 

## Google Cloud Run Deployment

To deploy your server to Google Cloud Run, follow these steps:

1. **Set up authentication and project**
```bash
# Login to GCP (this opens a browser window)
gcloud auth login

# Configure Docker to use gcloud as a credential helper
gcloud auth configure-docker

# Set your project (replace with your actual project ID)
gcloud config set project YOUR_PROJECT_ID
```

2. **Enable required APIs**
```bash
# Enable Artifact Registry API (newer than Container Registry)
gcloud services enable artifactregistry.googleapis.com

# Enable Cloud Run API
gcloud services enable run.googleapis.com

# Enable Cloud Build API
gcloud services enable cloudbuild.googleapis.com
```

3. **Create an Artifact Registry repository**
```bash
# Create a Docker repository in Artifact Registry
gcloud artifacts repositories create document-processing \
    --repository-format=docker \
    --location=us-central1 \
    --description="Docker repository for document processing service"
```

4. **Grant necessary permissions** (if you get permission errors)
```bash
# Grant yourself the Cloud Build Editor role
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="user:YOUR_EMAIL@gmail.com" \
    --role="roles/cloudbuild.builds.editor"

# Grant Service Account Token Creator role
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="user:YOUR_EMAIL@gmail.com" \
    --role="roles/iam.serviceAccountTokenCreator"
```

5. **Build and push your Docker image**
```bash
# Navigate to server directory
cd server

# Build and push to Artifact Registry
gcloud builds submit --tag us-central1-docker.pkg.dev/YOUR_PROJECT_ID/document-processing/document-processing-server:latest
```

6. **Deploy to Cloud Run**
```bash
gcloud run deploy document-processing-service \
    --image us-central1-docker.pkg.dev/YOUR_PROJECT_ID/document-processing/document-processing-server:latest \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 2Gi \
    --port 8080 \
    --set-env-vars="OPENAI_API_KEY=YOUR_OPENAI_KEY,LLAMA_CLOUD_API_KEY=YOUR_LLAMA_KEY,PINECONE_API_KEY=YOUR_PINECONE_KEY,PINECONE_ENVIRONMENT=YOUR_PINECONE_ENV"
```

> **Note about ports:** Cloud Run expects your container to listen on port 8080 by default. The Dockerfile has been updated to use the PORT environment variable, which Cloud Run sets to 8080 automatically.

7. **Create Cloud Storage buckets for persistence**
```bash
gsutil mb -l us-central1 gs://YOUR_PROJECT_ID-uploaded-files
gsutil mb -l us-central1 gs://YOUR_PROJECT_ID-parsed-files
gsutil mb -l us-central1 gs://YOUR_PROJECT_ID-edited-files
gsutil mb -l us-central1 gs://YOUR_PROJECT_ID-summarized-files
gsutil mb -l us-central1 gs://YOUR_PROJECT_ID-bm25-indexes
```

> **Note:** For production use, store your API keys in Secret Manager instead of environment variables. 