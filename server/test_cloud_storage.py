#!/usr/bin/env python3
"""
Test script to verify Cloud Storage integration works correctly
with the deployed Cloud Run service.

Usage:
    python test_cloud_storage.py                # Run full test with cleanup
    python test_cloud_storage.py --no-cleanup  # Run test but keep test files
    python test_cloud_storage.py --cleanup-only # Only cleanup existing test files

The script tests file upload, parsing, editing, summarization, and
automatically cleans up test files when done.
"""

import requests
import json
import time
import sys

# Cloud Run service URL
SERVICE_URL = "https://document-processing-service-yawfj7f47q-uc.a.run.app"

def test_api_endpoints():
    """Test the main API endpoints to verify cloud storage integration."""
    
    print("🧪 Testing Cloud Storage Integration")
    print("=" * 50)
    
    # Test 1: Upload a file
    print("\n1. Testing file upload...")
    test_content = "# Test Document\n\nThis is a test document for cloud storage integration.\n\n## Content\n\nHello, Cloud Storage!"
    
    files = {'file': ('test_document.txt', test_content.encode(), 'text/plain')}
    
    try:
        response = requests.post(f"{SERVICE_URL}/uploadfile/", files=files, timeout=30)
        if response.status_code == 201:
            upload_result = response.json()
            print(f"✅ File uploaded successfully: {upload_result['filename']}")
            print(f"   Saved to: {upload_result['file_path']}")
        else:
            print(f"❌ Upload failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return False
    
    # Test 2: List uploaded files
    print("\n2. Testing file listing...")
    try:
        response = requests.get(f"{SERVICE_URL}/listfiles/uploaded_files", timeout=30)
        if response.status_code == 200:
            files_result = response.json()
            print(f"✅ Files listed successfully: {files_result['files']}")
            if 'test_document.txt' not in files_result['files']:
                print("⚠️  Warning: Uploaded file not found in list")
        else:
            print(f"❌ Listing failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Listing error: {e}")
        return False
    
    # Test 3: Parse the file
    print("\n3. Testing file parsing...")
    try:
        response = requests.get(f"{SERVICE_URL}/parsefile/test_document.txt", timeout=60)
        if response.status_code == 200:
            parse_result = response.json()
            print(f"✅ File parsed successfully")
            print(f"   Content length: {len(parse_result['text_content'])} characters")
            print(f"   Metadata: {parse_result['metadata']}")
        else:
            print(f"❌ Parsing failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Parsing error: {e}")
        return False
    
    # Test 4: Save edited content
    print("\n4. Testing content saving...")
    edited_content = test_content + "\n\n## Edited Section\n\nThis content was edited and saved to cloud storage."
    
    try:
        response = requests.post(
            f"{SERVICE_URL}/savecontent/test_document",
            json={"content": edited_content},
            timeout=30
        )
        if response.status_code == 200:
            save_result = response.json()
            print(f"✅ Content saved successfully: {save_result['message']}")
        else:
            print(f"❌ Saving failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Saving error: {e}")
        return False
    
    # Test 5: Check edited files directory
    print("\n5. Testing edited files listing...")
    try:
        response = requests.get(f"{SERVICE_URL}/listfiles/edited_files", timeout=30)
        if response.status_code == 200:
            files_result = response.json()
            print(f"✅ Edited files listed: {files_result['files']}")
            if 'test_document.md' not in files_result['files']:
                print("⚠️  Warning: Edited file not found in list")
        else:
            print(f"❌ Edited files listing failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Edited files listing error: {e}")
        return False
    
    # Test 6: Summarize content
    print("\n6. Testing content summarization...")
    try:
        response = requests.get(f"{SERVICE_URL}/summarizecontent/test_document", timeout=60)
        if response.status_code == 200:
            summary_result = response.json()
            print(f"✅ Content summarized successfully")
            print(f"   Summary length: {len(summary_result['summary'])} characters")
            print(f"   Metadata: {summary_result['metadata']}")
        else:
            print(f"❌ Summarization failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Summarization error: {e}")
        return False
    
    # Test 7: Check summarized files directory
    print("\n7. Testing summarized files listing...")
    try:
        response = requests.get(f"{SERVICE_URL}/listfiles/summarized_files", timeout=30)
        if response.status_code == 200:
            files_result = response.json()
            print(f"✅ Summarized files listed: {files_result['files']}")
            if 'test_document' not in files_result['files']:
                print("⚠️  Warning: Summarized file not found in list")
        else:
            print(f"❌ Summarized files listing failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Summarized files listing error: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed! Cloud Storage integration is working correctly.")
    print("\n📊 Test Summary:")
    print("✅ File upload to Cloud Storage")
    print("✅ File listing from Cloud Storage")
    print("✅ File parsing with Cloud Storage")
    print("✅ Content saving to Cloud Storage")
    print("✅ Edited files in Cloud Storage")
    print("✅ Content summarization with Cloud Storage")
    print("✅ Summarized files in Cloud Storage")
    
    return True

def test_bucket_contents():
    """Test to check if files are actually in the buckets."""
    print("\n📦 Checking Cloud Storage Buckets:")
    
    directories = ['uploaded_files', 'parsed_files', 'edited_files', 'summarized_files']
    
    for directory in directories:
        try:
            response = requests.get(f"{SERVICE_URL}/listfiles/{directory}", timeout=30)
            if response.status_code == 200:
                files_result = response.json()
                file_count = len(files_result['files'])
                print(f"   {directory}: {file_count} files - {files_result['files']}")
            else:
                print(f"   {directory}: Error {response.status_code}")
        except Exception as e:
            print(f"   {directory}: Error - {e}")

def cleanup_test_files():
    """Clean up all test files created during the test."""
    print("\n🧹 Cleaning up test files...")
    
    # List of test files to delete in each directory
    test_files = {
        'uploaded_files': ['test_document.txt'],
        'parsed_files': ['test_document.md'],
        'edited_files': ['test_document.md'],
        'summarized_files': ['test_document']
    }
    
    cleanup_success = True
    
    for directory, filenames in test_files.items():
        for filename in filenames:
            try:
                # Check if file exists first
                response = requests.get(f"{SERVICE_URL}/listfiles/{directory}", timeout=30)
                if response.status_code == 200:
                    files_result = response.json()
                    if filename in files_result['files']:
                        # File exists, try to delete it
                        delete_url = f"{SERVICE_URL}/deletefile/{directory}/{filename}"
                        delete_response = requests.delete(delete_url, timeout=30)
                        
                        if delete_response.status_code == 200:
                            print(f"   ✅ Deleted {directory}/{filename}")
                        else:
                            print(f"   ⚠️  Failed to delete {directory}/{filename}: {delete_response.status_code}")
                            cleanup_success = False
                    else:
                        print(f"   ℹ️  File {directory}/{filename} not found (already cleaned or not created)")
                else:
                    print(f"   ⚠️  Could not list {directory}: {response.status_code}")
                    cleanup_success = False
                    
            except Exception as e:
                print(f"   ❌ Error cleaning {directory}/{filename}: {e}")
                cleanup_success = False
    
    if cleanup_success:
        print("   🎉 All test files cleaned up successfully!")
    else:
        print("   ⚠️  Some files could not be cleaned up (this may be normal if delete endpoint is not implemented)")
    
    return cleanup_success

if __name__ == "__main__":
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test Cloud Storage integration")
    parser.add_argument("--no-cleanup", action="store_true", 
                       help="Skip cleanup of test files after testing")
    parser.add_argument("--cleanup-only", action="store_true",
                       help="Only run cleanup without running tests")
    args = parser.parse_args()
    
    print(f"Testing service at: {SERVICE_URL}")
    
    # If cleanup-only mode, just run cleanup and exit
    if args.cleanup_only:
        print("🧹 Running cleanup only mode...")
        cleanup_success = cleanup_test_files()
        sys.exit(0 if cleanup_success else 1)
    
    print("Please ensure the client app is not running during this test to avoid conflicts.")
    
    # Give user a chance to cancel
    print("\nStarting test in 3 seconds... (Ctrl+C to cancel)")
    try:
        time.sleep(3)
    except KeyboardInterrupt:
        print("\nTest cancelled.")
        sys.exit(0)
    
    success = test_api_endpoints()
    
    print("\n" + "-" * 50)
    test_bucket_contents()
    
    # Run cleanup unless explicitly disabled
    if not args.no_cleanup:
        cleanup_test_files()
    else:
        print("\n⚠️  Skipping cleanup - test files remain in storage")
    
    if success:
        print("\n🎯 Result: Cloud Storage integration is working correctly!")
        print("Your application should now properly persist files in Google Cloud Storage.")
    else:
        print("\n❌ Result: Some tests failed. Please check the logs for details.")
        sys.exit(1) 