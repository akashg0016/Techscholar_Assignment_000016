import os
import pytest
from fastapi.testclient import TestClient
from main import app, UPLOAD_DIR

client = TestClient(app)

@pytest.fixture
def setup_and_teardown():
    # Setup: Ensure the upload directory exists and is empty before each test
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
    yield
    # Teardown: Clean up the upload directory after each test
    for filename in os.listdir(UPLOAD_DIR):
        file_path = os.path.join(UPLOAD_DIR, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)

def test_upload_file(setup_and_teardown):
    # Test uploading a file
    file_path = "D:/Tech_Scholar/my_fastapi_project/Krishna_Resume.pdf"
    with open(file_path, "wb") as f:
        f.write(b"This is a test file.")

    with open(file_path, "rb") as f:
        response = client.post("/upload/", files={"file": f})
    
    assert response.status_code == 200
    assert response.json()["message"] == "File uploaded successfully"

def test_get_file(setup_and_teardown):
    # Test retrieving a file
    uploaded_filename = None
    file_path = None

    # Upload the file
    upload_response = upload_test_file()

    # Retrieve the uploaded filename
    if upload_response.status_code == 200:
        uploaded_filename = upload_response.json()["file_path"].split("/")[-1]
        file_path = f"{UPLOAD_DIR}/{uploaded_filename}"

    assert uploaded_filename is not None
    assert file_path is not None

    # Write content to the file
    with open(file_path, "wb") as f:
        f.write(b"This is a test file.")
    
    # Retrieve the file and check content
    response = client.get(f"/files/{uploaded_filename}")
    
    assert response.status_code == 200
    assert response.content == b"This is a test file."


def upload_test_file():
    # Helper function to upload a test file
    file_path = "D:/Tech_Scholar/my_fastapi_project/Krishna_Resume.pdf"
    with open(file_path, "rb") as f:
        return client.post("/upload/", files={"file": f})
