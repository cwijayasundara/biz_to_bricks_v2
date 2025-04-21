import os
import logging
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_core.documents import Document

def create_directory(directory):
    """
    Create a directory if it doesn't exist
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
        logging.info(f"Directory '{directory}' created")
    else:
        logging.info(f"Directory '{directory}' already exists")
    return directory

def list_files(directory: str) -> list:
    """
    List all files in the given directory and return a list of filenames.
    """
    try:
        return os.listdir(directory)
    except Exception as e:
        logging.error(f"Failed to list files in {directory}: {e}")
        return []

def read_file(file_path: str) -> str:
    """
    Read a file and return the content as a string.
    """
    with open(file_path, "r") as f:
        return f.read()

def load_markdown_file(file_path: str) -> str:
    """
    Load a markdown file and return a string of the content.
    """
    loader = UnstructuredMarkdownLoader(file_path)
    documents = loader.load()
    metadata = documents[0].metadata
    # convert the documents to a string
    text = ""
    for document in documents:
        text += document.page_content
    return text, metadata

# Test the load_markdown_file function
# if __name__ == "__main__":
#     file_path = "server/parsed_files/Sample1.md"
#     text, metadata = load_markdown_file(file_path)
#     print(text)
#     print(metadata)