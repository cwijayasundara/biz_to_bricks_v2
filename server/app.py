from fastapi import FastAPI, UploadFile, File, Body, HTTPException, status, Path, Query
from fastapi.responses import JSONResponse
from file_util import create_directory, list_files as list_directory, load_markdown_file
from file_parser import parse_file_with_llama_parse
from doc_summarizer import summarize_text_content
from pydantic import BaseModel, Field
import os
from pathlib import Path as FilePath
import logging
from typing import Dict, List, Any, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define path constants
UPLOADED_FILE_PATH = "uploaded_files"
PARSED_FILE_PATH = "parsed_files"
EDITED_FILE_PATH = "edited_files"
SUMMARIZED_FILE_PATH = "summarized_files"

# Initialize FastAPI app
app = FastAPI(
    title="Document Processing API",
    description="API for uploading, parsing, editing, and summarizing documents",
    version="1.0.0"
)

# Define data models
class ContentUpdate(BaseModel):
    """Model for content update requests"""
    content: str = Field(..., description="The edited content to save")

class ErrorResponse(BaseModel):
    """Model for error responses"""
    error: str = Field(..., description="Error message")

class SuccessResponse(BaseModel):
    """Model for success responses"""
    status: str = Field("success", description="Status of the operation")
    message: str = Field(..., description="Success message")

class FileResponse(BaseModel):
    """Model for file-related responses"""
    filename: str = Field(..., description="Name of the file")
    file_path: str = Field(..., description="Path where the file is stored")

class FilesListResponse(BaseModel):
    """Model for file listing responses"""
    files: List[str] = Field(..., description="List of file names")

# Helper functions
def ensure_directories_exist():
    """Ensure all required directories exist"""
    for directory in [UPLOADED_FILE_PATH, PARSED_FILE_PATH, EDITED_FILE_PATH, SUMMARIZED_FILE_PATH]:
        create_directory(directory)

def get_file_path(directory: str, filename: str, extension: Optional[str] = None) -> str:
    """Construct file path with proper handling"""
    base_name = filename.split(".")[0] if "." in filename else filename
    if extension:
        return str(FilePath(directory) / f"{base_name}{extension}")
    return str(FilePath(directory) / filename)

# Ensure directories exist at startup
@app.on_event("startup")
async def startup_event():
    """Initialize resources on application startup"""
    ensure_directories_exist()
    logger.info("Application started, directories initialized")

# API Routes
@app.post("/uploadfile/", response_model=FileResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a file to the server.
    
    Args:
        file: The file to upload
        
    Returns:
        Information about the uploaded file
    """
    logger.info(f"Received upload request for file: {file.filename}")
    
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must have a filename"
        )
    
    file_path = get_file_path(UPLOADED_FILE_PATH, file.filename)
    
    try:
        # Save the uploaded file
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        logger.info(f"File saved to {file_path}")
        return {
            "filename": file.filename, 
            "file_path": file_path
        }
    except Exception as e:
        logger.error(f"Error saving file {file.filename}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving file: {str(e)}"
        )

@app.get("/listfiles/{directory}", response_model=FilesListResponse)
async def list_files(directory: str = Path(..., description="Directory to list files from")):
    """
    List all files in the specified directory.
    
    Args:
        directory: The directory to list files from
        
    Returns:
        List of files in the directory
    """
    logger.info(f"Listing files in directory: {directory}")
    
    try:
        files = list_directory(directory)
        return {"files": files}
    except Exception as e:
        logger.error(f"Error listing files in {directory}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing files: {str(e)}"
        )

@app.get("/parsefile/{filename}")
async def parse_uploaded_file(filename: str = Path(..., description="Name of the file to parse")):
    """
    Parse an uploaded file into markdown format.
    
    Args:
        filename: Name of the file to parse
        
    Returns:
        Parsed text content and metadata
    """
    logger.info(f"Parsing file: {filename}")
    
    try:
        # Check if the parsed file already exists
        base_filename = filename.split(".")[0]
        parsed_file_path = get_file_path(PARSED_FILE_PATH, base_filename, extension=".md")
        uploaded_file_path = get_file_path(UPLOADED_FILE_PATH, filename)
        
        text_content = ""
        metadata: Dict[str, Any] = {}
        
        if os.path.exists(parsed_file_path):
            logger.info(f"Using existing parsed file: {parsed_file_path}")
            with open(parsed_file_path, "r") as f:
                text_content = f.read()
            metadata = {
                "file_name": base_filename, 
                "file_path": f"{PARSED_FILE_PATH}/{base_filename}"
            }
        else:
            logger.info(f"Parsing new file: {uploaded_file_path}")
            text_content, metadata = parse_file_with_llama_parse(uploaded_file_path)
            metadata["file_name"] = base_filename
            metadata["file_path"] = f"{PARSED_FILE_PATH}/{base_filename}"
            
            # Save the parsed content
            create_directory(PARSED_FILE_PATH)
            with open(parsed_file_path, "w") as f:
                f.write(text_content)
            logger.info(f"Saved parsed content to {parsed_file_path}")
            
        return {"text_content": text_content, "metadata": metadata}
        
    except FileNotFoundError:
        logger.error(f"File not found for parsing: {filename}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File {filename} not found"
        )
    except Exception as e:
        logger.error(f"Error parsing file {filename}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error parsing file: {str(e)}"
        )

@app.post("/savecontent/{filename}", response_model=SuccessResponse)
async def save_content(
    filename: str = Path(..., description="Name of the file to save content for"),
    content_update: ContentUpdate = Body(..., description="Content to save")
):
    """
    Save edited content to a file.
    
    Args:
        filename: Name of the file to save content for
        content_update: The content to save
        
    Returns:
        Success message
    """
    logger.info(f"Saving content for file: {filename}")
    
    try:
        create_directory(EDITED_FILE_PATH)
        file_path = get_file_path(EDITED_FILE_PATH, filename, extension=".md")
        
        with open(file_path, "w") as f:
            f.write(content_update.content)
            
        logger.info(f"Content saved to {file_path}")
        return {
            "status": "success", 
            "message": f"Content for {filename} saved successfully"
        }
    except Exception as e:
        logger.error(f"Error saving content for {filename}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving content: {str(e)}"
        )

@app.get("/summarizecontent/{filename}")
async def summarize_content(
    filename: str = Path(..., description="Name of the file to summarize")
):
    """
    Parse a file from the parsed_files directory and return its summary.
    
    Args:
        filename: Name of the file to summarize
        
    Returns:
        Summary of the file content and metadata
    """
    logger.info(f"Summarizing file: {filename}")
    
    try:
        file_path = get_file_path(PARSED_FILE_PATH, filename)
        summarized_file_path = get_file_path(SUMMARIZED_FILE_PATH, filename)
        
        # Check if the summarized file already exists
        if os.path.exists(summarized_file_path):
            logger.info(f"Using existing summarized file: {summarized_file_path}")
            with open(summarized_file_path, "r") as f:
                summary = f.read()
            metadata = {
                "file_name": filename, 
                "file_path": f"{SUMMARIZED_FILE_PATH}/{filename}"
            }
            return {"summary": summary, "metadata": metadata}
        
        # Load and summarize the file
        logger.info(f"Loading file for summarization: {file_path}")
        text_content, metadata = load_markdown_file(file_path)
        
        logger.info(f"Generating summary for {filename}")
        summary = summarize_text_content(text_content)
        
        # Save the summary
        create_directory(SUMMARIZED_FILE_PATH)
        metadata["file_name"] = filename
        metadata["file_path"] = f"{SUMMARIZED_FILE_PATH}/{filename}"
        
        with open(summarized_file_path, "w") as f:
            f.write(summary)
            
        logger.info(f"Summary saved to {summarized_file_path}")
        return {"summary": summary, "metadata": metadata}
        
    except FileNotFoundError:
        logger.error(f"File not found for summarization: {file_path}")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"File {filename} not found in parsed_files directory"}
        )
    except Exception as e:
        logger.error(f"Error during summarization for {filename}: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": f"Failed to summarize file: {str(e)}"}
        )

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "An unexpected error occurred"}
    )
