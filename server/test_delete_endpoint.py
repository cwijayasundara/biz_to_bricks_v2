#!/usr/bin/env python3
"""
Simple test to verify the delete endpoint works correctly.
"""

import requests

# Cloud Run service URL
SERVICE_URL = "https://document-processing-service-yawfj7f47q-uc.a.run.app"

def test_delete_endpoint():
    """Test the delete endpoint with various scenarios."""
    print("🧪 Testing Delete Endpoint")
    print("=" * 40)
    
    # Test 1: Try to delete a non-existent file (should return 404)
    print("\n1. Testing delete of non-existent file...")
    try:
        response = requests.delete(f"{SERVICE_URL}/deletefile/uploaded_files/nonexistent.txt", timeout=30)
        if response.status_code == 404:
            print("✅ Correctly returned 404 for non-existent file")
        else:
            print(f"❌ Expected 404, got {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error testing non-existent file: {e}")
    
    # Test 2: Try to delete from invalid directory (should return 400)
    print("\n2. Testing delete from invalid directory...")
    try:
        response = requests.delete(f"{SERVICE_URL}/deletefile/invalid_directory/test.txt", timeout=30)
        if response.status_code == 400:
            print("✅ Correctly returned 400 for invalid directory")
        else:
            print(f"❌ Expected 400, got {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error testing invalid directory: {e}")
    
    # Test 3: Upload a test file and then delete it
    print("\n3. Testing upload and delete workflow...")
    test_content = "This is a test file for deletion."
    
    try:
        # Upload a test file
        files = {'file': ('delete_test.txt', test_content.encode(), 'text/plain')}
        upload_response = requests.post(f"{SERVICE_URL}/uploadfile/", files=files, timeout=30)
        
        if upload_response.status_code == 201:
            print("✅ Test file uploaded successfully")
            
            # Verify file exists
            list_response = requests.get(f"{SERVICE_URL}/listfiles/uploaded_files", timeout=30)
            if list_response.status_code == 200:
                files_list = list_response.json()
                if 'delete_test.txt' in files_list['files']:
                    print("✅ Test file confirmed in file list")
                    
                    # Now delete the file
                    delete_response = requests.delete(f"{SERVICE_URL}/deletefile/uploaded_files/delete_test.txt", timeout=30)
                    if delete_response.status_code == 200:
                        print("✅ Test file deleted successfully")
                        print(f"   Response: {delete_response.json()}")
                        
                        # Verify file is gone
                        list_response2 = requests.get(f"{SERVICE_URL}/listfiles/uploaded_files", timeout=30)
                        if list_response2.status_code == 200:
                            files_list2 = list_response2.json()
                            if 'delete_test.txt' not in files_list2['files']:
                                print("✅ Test file confirmed deleted from file list")
                            else:
                                print("❌ Test file still appears in file list after deletion")
                        else:
                            print(f"❌ Error verifying deletion: {list_response2.status_code}")
                    else:
                        print(f"❌ Failed to delete test file: {delete_response.status_code}")
                        print(f"Response: {delete_response.text}")
                else:
                    print("❌ Test file not found in file list after upload")
            else:
                print(f"❌ Error listing files: {list_response.status_code}")
        else:
            print(f"❌ Failed to upload test file: {upload_response.status_code}")
            print(f"Response: {upload_response.text}")
    except Exception as e:
        print(f"❌ Error in upload/delete workflow: {e}")
    
    print("\n" + "=" * 40)
    print("🎯 Delete endpoint test completed!")

if __name__ == "__main__":
    test_delete_endpoint() 