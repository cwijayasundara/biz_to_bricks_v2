import streamlit as st
import requests
import os
import json
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8004"
UPLOAD_API_URL = f"{BASE_URL}/uploadfile/"
LIST_FILES_API_URL = f"{BASE_URL}/listfiles/uploaded_files"
PARSE_FILE_API_URL = f"{BASE_URL}/parsefile/"
SAVE_CONTENT_API_URL = f"{BASE_URL}/savecontent/"
LIST_FILE_FOR_SUMMARIZE = f"{BASE_URL}/listfiles/parsed_files"
SUMMARIZE_CONTENT_API_URL_BASE = f"{BASE_URL}/summarizecontent"
SAMPLE_FILES_DIR = Path("../docs")  # Path to docs folder with sample files

# Set page config for better UI
st.set_page_config(
    page_title="Document Processor",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API utility functions
def make_api_request(url, method="get", data=None, files=None, handle_error=True):
    """General purpose API request handler with error handling"""
    try:
        if method.lower() == "get":
            response = requests.get(url)
        elif method.lower() == "post":
            if files:
                response = requests.post(url, files=files)
            else:
                response = requests.post(url, json=data)
        else:
            return {"error": f"Unsupported method: {method}"}
            
        if response.status_code == 200:
            return response.json()
        else:
            error_msg = f"API Error: {response.status_code}"
            try:
                error_detail = response.json().get("error", response.text)
                error_msg = f"{error_msg} - {error_detail}"
            except:
                error_msg = f"{error_msg} - {response.text}"
                
            if handle_error:
                st.error(error_msg)
            return {"error": error_msg}
    except Exception as e:
        error_msg = f"Connection error: {str(e)}"
        if handle_error:
            st.error(error_msg)
        return {"error": error_msg}

def fetch_files(url, message="Fetching files..."):
    """Fetch files from the specified API endpoint"""
    with st.spinner(message):
        result = make_api_request(url)
        
    if "error" in result:
        return []
    return result.get("files", [])

def main():
    # Apply custom styling
    st.markdown("""
        <style>
        .stTabs [data-baseweb="tab-panel"] {
            padding-top: 1rem;
        }
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("Document Processor 📄")
    st.write("Upload, view, parse, and summarize documents using FastAPI backend.")
    
    # Create tabs for different functionality
    tab1, tab2, tab3, tab4 = st.tabs(["📤 Upload", "📋 View Files", "📝 Parse Files", "📊 Summarize"])
    
    with tab1:
        upload_files()
    
    with tab2:
        view_files()
        
    with tab3:
        parse_files()
        
    with tab4:
        summarize_files_tab()
    
def upload_files():
    st.header("Upload Files")
    
    # Add documentation and instructions
    with st.expander("Instructions", expanded=False):
        st.write("""
        1. Select a sample file from the docs directory
        2. Click 'Upload File' to send it to the server
        3. The server will store the file and return its details
        """)
    
    # Check if docs directory exists and list sample files
    if os.path.exists(SAMPLE_FILES_DIR):
        sample_files = list(SAMPLE_FILES_DIR.glob("*.*"))
        if sample_files:
            sample_file_names = [file.name for file in sample_files]
            selected_sample = st.selectbox(
                "Select a sample file", 
                ["None"] + sample_file_names, 
                key="upload_sample",
                help="Choose a file from the docs directory to upload"
            )
            
            # Display file info if selected
            if selected_sample != "None":
                sample_path = SAMPLE_FILES_DIR / selected_sample
                file_size = os.path.getsize(sample_path)
                st.info(f"Selected: {selected_sample} ({file_size/1024:.1f} KB)")
        else:
            st.warning("No sample files found in docs directory.")
            selected_sample = "None"
    else:
        st.error("Docs directory not found.")
        selected_sample = "None"
    
    # Upload button
    if st.button("Upload File", type="primary", disabled=(selected_sample == "None")):
        if selected_sample != "None":
            # Handle selected sample file from docs directory
            sample_file_path = SAMPLE_FILES_DIR / selected_sample
            with open(sample_file_path, "rb") as file:
                with st.spinner("Uploading file..."):
                    file_content = file.read()
                    files = {"file": (selected_sample, file_content)}
                    result = make_api_request(UPLOAD_API_URL, method="post", files=files)
                
                if "error" not in result:
                    st.success(f"File uploaded successfully!")
                    st.json(result)

def view_files():
    st.header("View Files")
    
    col1, col2 = st.columns([4, 1])
    with col2:
        refresh = st.button("🔄 Refresh", help="Reload the file list from server")
    
    # Get the list of files from the server
    files = fetch_files(LIST_FILES_API_URL, "Loading file list...")
    
    if files:
        st.success(f"Found {len(files)} files on the server")
        
        # Create a table of files
        file_table = "<table style='width:100%'><tr><th>Index</th><th>Filename</th></tr>"
        for idx, file in enumerate(files):
            file_table += f"<tr><td>{idx+1}</td><td>{file}</td></tr>"
        file_table += "</table>"
        
        st.markdown(file_table, unsafe_allow_html=True)
    else:
        st.info("No files found on the server.")

def parse_files():
    st.header("Parse Files")
    
    # Get the list of files from the server
    files = fetch_files(LIST_FILES_API_URL, "Loading files to parse...")
    
    if files:
        selected_file = st.selectbox(
            "Select a file to parse", 
            ["None"] + files, 
            key="parse_file_select",
            help="Choose a file to convert to structured text"
        )
        
        if selected_file != "None":
            st.info(f"Selected: {selected_file}")
            if st.button("Parse File", type="primary"):
                display_parsed_file(selected_file)
    else:
        st.info("No files found on the server to parse.")

def display_parsed_file(filename):
    """Parse a file and display its content with editing capabilities"""
    try:
        with st.spinner(f"Parsing file {filename}..."):
            result = make_api_request(f"{PARSE_FILE_API_URL}{filename}")
        
        if "error" not in result:
            st.success(f"File parsed successfully!")
            
            # Store original content for comparison
            if "original_content" not in st.session_state:
                st.session_state.original_content = {}
                
            text_content = result.get("text_content", "No content found")
            st.session_state.original_content[filename] = text_content
            
            # Edit Parsed Content Expander
            with st.expander("Edit Parsed Content", expanded=True):
                text_area_key = f"edited_content_{filename}"
                if text_area_key not in st.session_state:
                    st.session_state[text_area_key] = text_content
                    
                edited_content = st.text_area(
                    "You can edit the content below:",
                    value=st.session_state[text_area_key],
                    height=500,
                    key=text_area_key
                )
                
                # Save Changes Button
                col1, col2 = st.columns([1, 4])
                with col1:
                    save_clicked = st.button("💾 Save Changes", key=f"save_{filename}")
                    
                if save_clicked:
                    if edited_content != st.session_state.original_content[filename]:
                        with st.spinner("Saving changes..."):
                            save_result = make_api_request(
                                f"{SAVE_CONTENT_API_URL}{filename}", 
                                method="post", 
                                data={"content": edited_content}
                            )
                        
                        if "error" not in save_result:
                            st.success(save_result.get("message", "Changes saved successfully!"))
                            st.session_state.original_content[filename] = edited_content
                            st.session_state[text_area_key] = edited_content
                    else:
                        st.info("No changes detected.")
            
            # Metadata Expander
            with st.expander("Metadata", expanded=False):
                st.json(result.get("metadata", {}))
    except Exception as e:
        st.error(f"An error occurred while parsing: {str(e)}")

def summarize_files_tab():
    st.header("Summarize Content")
    
    with st.expander("About Summarization", expanded=False):
        st.write("""
        This feature uses AI to create concise summaries of parsed documents.
        
        Process:
        1. Select a file from the parsed documents list
        2. Click 'Summarize Content' to generate a summary
        3. The summary will be displayed below
        """)
    
    # Get the list of files from the server
    files = fetch_files(LIST_FILE_FOR_SUMMARIZE, "Loading files to summarize...")
    
    if files:
        col1, col2 = st.columns([3, 1])
        with col1:
            selected_file = st.selectbox(
                "Select a parsed file to summarize", 
                ["None"] + files, 
                key="summarize_file_select",
                help="Choose a parsed file to generate a summary"
            )
        
        if selected_file != "None":
            st.info(f"Ready to summarize: {selected_file}")
            
            # Summarize Button
            if st.button("✨ Generate Summary", key=f"summarize_{selected_file}", type="primary"):
                summarize_and_display(selected_file)
                
            # Display summary if it exists in session state
            summary_key = f"summary_{selected_file}"
            if summary_key in st.session_state:
                with st.expander("Summary", expanded=True):
                    st.markdown(st.session_state[summary_key])
    else:
        st.info("No parsed files found on the server. Parse files first using the 'Parse Files' tab.")

def summarize_and_display(filename):
    """Fetch and display the summary for a file with error handling"""
    summary_key = f"summary_{filename}"
    
    with st.spinner(f"Summarizing {filename}..."):
        result = make_api_request(
            f"{SUMMARIZE_CONTENT_API_URL_BASE}/{filename}",
            handle_error=False
        )
    
    if "error" in result:
        st.error(f"Error summarizing: {result['error']}")
        if summary_key in st.session_state:
            del st.session_state[summary_key]
    else:
        st.success("Summary generated successfully!")
        st.session_state[summary_key] = result.get("summary", "No summary available.")
        
        # Show metadata if available
        if "metadata" in result:
            with st.expander("Summary Metadata", expanded=False):
                st.json(result["metadata"])

if __name__ == "__main__":
    main()

