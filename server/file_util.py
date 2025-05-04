import os
import logging
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_core.documents import Document
from pathlib import Path as FilePath
from typing import Optional

EDITED_FILE_PATH = "edited_files"
PARSED_FILE_PATH = "parsed_files"

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

def get_file_path(directory: str, filename: str, extension: Optional[str] = None) -> str:
    """Construct file path with proper handling"""
    base_name = filename.split(".")[0] if "." in filename else filename
    if extension:
        return str(FilePath(directory) / f"{base_name}{extension}")
    return str(FilePath(directory) / filename)

def load_edited_file_or_parsed_file(filename: str):
    """
    This function loads the edited file if it exists, otherwise it loads the parsed file.
    Raises FileNotFoundError if neither exists.
    """
    edited_file_path = get_file_path(EDITED_FILE_PATH, filename, extension=".md")
    parsed_file_path = get_file_path(PARSED_FILE_PATH, filename, extension=".md")
    print("DEBUG: Checking for file at", os.path.abspath(edited_file_path))
    print("DEBUG: Checking for file at", os.path.abspath(parsed_file_path))
    if os.path.exists(edited_file_path):
        return load_markdown_file(edited_file_path)
    elif os.path.exists(parsed_file_path):
        return load_markdown_file(parsed_file_path)
    else:
        raise FileNotFoundError(f"Neither {edited_file_path} nor {parsed_file_path} exists.")
    
# Test the load_markdown_file function
# if __name__ == "__main__":
#     file_path = "server/parsed_files/Sample1.md"
#     text, metadata = load_markdown_file(file_path)
#     print(text)
#     print(metadata)