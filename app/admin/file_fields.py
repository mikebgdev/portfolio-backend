"""Custom file upload fields for SQLAdmin."""

import os
import uuid
from pathlib import Path

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
            # Handle file upload from form
            if (
                hasattr(file_data, "filename")
                and file_data.filename
                and file_data.filename.strip()
            ):
                # Generate unique filename
                file_ext = os.path.splitext(file_data.filename)[1]
                unique_filename = f"{uuid.uuid4()}{file_ext}"

                # Create upload directory if it doesn't exist
                upload_path = Path(settings.uploads_path) / self.upload_dir
                upload_path.mkdir(parents=True, exist_ok=True)

                # Save file
                file_path = upload_path / unique_filename

                # Handle different file object types
                try:
                    with open(file_path, "wb") as buffer:
                        if hasattr(file_data, "stream"):
                            # FileStorage object from werkzeug/WTForms
                            file_data.stream.seek(0)
                            buffer.write(file_data.stream.read())
                        elif hasattr(file_data, "file"):
                            # Some other file-like object
                            file_data.file.seek(0)
                            buffer.write(file_data.file.read())
                        elif hasattr(file_data, "read"):
                            # Direct file object
                            if hasattr(file_data, "seek"):
                                file_data.seek(0)
                            content = file_data.read()
                            if isinstance(content, str):
                                content = content.encode("utf-8")
                            buffer.write(content)
                        else:
                            # Raw bytes
                            buffer.write(file_data)

                    # Return the relative path to store in database
                    self.data = f"/uploads/{self.upload_dir}/{unique_filename}"
                except Exception as e:
                    # If file processing fails, don't save and keep existing value
                    print(f"Error processing file upload: {e}")
                    self.data = None
            elif isinstance(file_data, str) and file_data.strip():
                # Keep existing value if it's a string (editing without new file)
                self.data = file_data
            else:
                self.data = None


class ImageUploadField(FileUploadField):
    """Custom image upload field that saves images."""

    def __init__(self, label=None, validators=None, **kwargs):
        super().__init__(label, validators, upload_dir="images", **kwargs)


class DocumentUploadField(FileUploadField):
    """Custom document upload field that saves files."""

    def __init__(self, label=None, validators=None, **kwargs):
        super().__init__(label, validators, upload_dir="files", **kwargs)
