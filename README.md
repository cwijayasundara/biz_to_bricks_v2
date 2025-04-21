Pre-requisites:

- Install Python 3.12
- Install an IDE like VsCode & a coding assistant like Github Copilot
- Create a virtual env by running
    - python3 -m venv .venv
    - source .venv/bin/activate
    - Or use the VsCode's create Python venv feature
- Run 'pip install -r requirements.txt' to install all the Python dependencies
- Create a .env file with the below keys and values:
    OPENAI_API_KEY='<your openai key>'
    LLAMA_CLOUD_API_KEY='<your llamacloud api key>'
    LANGSMITH_API_KEY='<your langsmith key>'
    PINECONE_API_KEY='<your pinecone api key>'
    PINECONE_ENVIRONMENT=gcp-starter

How to run the server app with the APIs?

- cd server
- uvicorn app:app --reload --port 8004

How to run the sample client?

- cd client
- streamlit run client.py