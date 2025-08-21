"""File storage configuration for fastapi-storages."""
import os
from pathlib import Path
from fastapi_storages import FileSystemStorage
from app.config import settings


# Ensure upload directories exist
uploads_path = Path(settings.uploads_path)
uploads_path.mkdir(exist_ok=True)
(uploads_path / "files").mkdir(exist_ok=True)
(uploads_path / "images").mkdir(exist_ok=True)

# Configure storage backends
file_storage = FileSystemStorage(path=str(uploads_path / "files"))
image_storage = FileSystemStorage(path=str(uploads_path / "images"))