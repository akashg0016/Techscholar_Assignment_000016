from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from cryptography.fernet import Fernet
import os
import logging

app = FastAPI()

# Generate a key for encryption
key = Fernet.generate_key()
cipher_suite = Fernet(key)

# Directory to store uploaded files
UPLOAD_DIR = "D:/Tech_Scholar/my_fastapi_project/uploads"  # Path to the directory where uploaded files will be stored

# Ensure the upload directory exists
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Read file contents
        contents = await file.read()

        # Encrypt file contents
        encrypted_contents = cipher_suite.encrypt(contents)

        # Save encrypted contents to file
        filename = os.path.join(UPLOAD_DIR, file.filename)
        with open(filename, "wb") as f:
            f.write(encrypted_contents)

        return {"message": "File uploaded successfully", "file_path": f"/files/{file.filename}"}
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files/{filename}")
async def get_file(filename: str):
    temp_filepath = None
    try:
        # Ensure file exists
        filepath = os.path.join(UPLOAD_DIR, filename)
        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="File not found")

        # Read encrypted file contents
        with open(filepath, "rb") as f:
            encrypted_contents = f.read()

        # Decrypt file contents
        decrypted_contents = cipher_suite.decrypt(encrypted_contents)

        # Write decrypted contents to a temporary file
        temp_filepath = os.path.join(UPLOAD_DIR, f"temp_{filename}")
        with open(temp_filepath, "wb") as f:
            f.write(decrypted_contents)

        return FileResponse(temp_filepath, filename=filename)

    except Exception as e:
        logger.error(f"Error retrieving file: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up the temporary file
        if temp_filepath and os.path.exists(temp_filepath):
            os.remove(temp_filepath)
