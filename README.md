Pre-requisites:

- Install Python 3.12
- Install an IDE like VsCode & a coding assistant like Github Copilot
- Create a virtual env by running
    - python3 -m venv .venv
    - source .venv/bin/activate
    - Or use the VsCode's create Python venv feature
- Run 'pip install -r requirements.txt' to install all the Python dependencies

How to run the server app with the APIs?

- cd server
- uvicorn app:app --reload --port 8004

How to run the sample client?

- cd client
- streamlit run client.py