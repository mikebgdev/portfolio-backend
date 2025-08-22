"""File utilities for encoding and handling uploaded files."""

import base64
import logging
import mimetypes
import os
from pathlib import Path
from typing import Any, Dict, Optional

from app.config import settings

logger = logging.getLogger(__name__)


def get_mime_type(file_path: str) -> str:
    """Get MIME type for a file."""
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type:
        return mime_type

    # Fallback for common file types
    ext = Path(file_path).suffix.lower()
    fallback_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".gif": "image/gif",
        ".pdf": "application/pdf",
        ".doc": "application/msword",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".txt": "text/plain",
    }
    return fallback_types.get(ext, "application/octet-stream")


def encode_file_to_base64(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Encode a file to base64 data URL format.

    Args:
        file_path: Path to the file (relative to uploads directory or absolute)

    Returns:
        Dict with 'data' (base64 data URL) and 'mime_type', or None if file not found
    """
    if not file_path:
        return None

    try:
        # Handle both absolute paths and relative paths from uploads
        if file_path.startswith("/uploads/"):
            # Remove leading /uploads/ and prepend the actual uploads directory
            relative_path = file_path[9:]  # Remove '/uploads/'
            full_path = Path(settings.uploads_path) / relative_path
        else:
            full_path = Path(file_path)

        if not full_path.exists():
            logger.warning(f"File not found: {full_path}")
            return None

        # Check file size (limit to 10MB for Base64)
        file_size = full_path.stat().st_size
        if file_size > 10 * 1024 * 1024:  # 10MB
            logger.warning(
                f"File too large for Base64 encoding: {full_path} ({file_size} bytes)"
            )
            return None

        # Read and encode file
        with open(full_path, "rb") as file:
            file_content = file.read()
            base64_content = base64.b64encode(file_content).decode("utf-8")

        mime_type = get_mime_type(str(full_path))
        data_url = f"data:{mime_type};base64,{base64_content}"

        return {
            "data": data_url,
            "mime_type": mime_type,
            "size": file_size,
            "filename": full_path.name,
        }

    except Exception as e:
        logger.error(f"Error encoding file {file_path}: {e}")
        return None


def get_file_info(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Get file information without encoding to Base64.

    Args:
        file_path: Path to the file

    Returns:
        Dict with file info or None if file not found
    """
    if not file_path:
        return None

    try:
        if file_path.startswith("/uploads/"):
            relative_path = file_path[9:]
            full_path = Path(settings.uploads_path) / relative_path
        else:
            full_path = Path(file_path)

        if not full_path.exists():
            return None

        file_size = full_path.stat().st_size
        mime_type = get_mime_type(str(full_path))

        return {
            "mime_type": mime_type,
            "size": file_size,
            "filename": full_path.name,
            "path": file_path,
        }

    except Exception as e:
        logger.error(f"Error getting file info {file_path}: {e}")
        return None
