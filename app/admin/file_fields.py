"""Custom file upload fields for SQLAdmin."""
import os
import uuid
from pathlib import Path
from typing import Any, Optional
from starlette.requests import Request
from starlette.datastructures import UploadFile
from sqladmin.forms import ModelConverter
from wtforms import FileField
from wtforms.validators import Optional as OptionalValidator
from app.config import settings


class FileUploadField(FileField):
    """Custom file upload field that saves files and returns the path."""
    
    def __init__(self, label=None, validators=None, upload_dir="files", **kwargs):
        if validators is None:
            validators = [OptionalValidator()]
        super().__init__(label, validators, **kwargs)
        self.upload_dir = upload_dir
    
    def process_formdata(self, valuelist):
        """Process the uploaded file and save it."""
        if valuelist and valuelist[0]:
            file_data = valuelist[0]
            # Handle file upload from form (bytes or file-like object)
            if hasattr(file_data, 'read') and hasattr(file_data, 'filename') and file_data.filename:
                # Generate unique filename
                file_ext = os.path.splitext(file_data.filename)[1]
                unique_filename = f"{uuid.uuid4()}{file_ext}"
                
                # Create upload directory if it doesn't exist
                upload_path = Path(settings.uploads_path) / self.upload_dir
                upload_path.mkdir(parents=True, exist_ok=True)
                
                # Save file
                file_path = upload_path / unique_filename
                with open(file_path, "wb") as buffer:
                    if hasattr(file_data, 'read'):
                        file_data.seek(0)  # Reset file pointer
                        buffer.write(file_data.read())
                    else:
                        buffer.write(file_data)
                
                # Return the relative path to store in database
                self.data = f"/uploads/{self.upload_dir}/{unique_filename}"
            elif isinstance(file_data, str) and file_data.strip():
                # Keep existing value if it's a string (editing without new file)
                self.data = file_data
            else:
                self.data = None
        else:
            # No file uploaded, keep existing value if any
            pass


class ImageUploadField(FileUploadField):
    """Custom image upload field that saves images."""
    
    def __init__(self, label=None, validators=None, **kwargs):
        super().__init__(label, validators, upload_dir="images", **kwargs)


class DocumentUploadField(FileUploadField):
    """Custom document upload field that saves files."""
    
    def __init__(self, label=None, validators=None, **kwargs):
        super().__init__(label, validators, upload_dir="files", **kwargs)