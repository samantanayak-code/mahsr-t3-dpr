"""
Media Upload Utility
Handles photo/video uploads with compression and Supabase Storage integration
"""

import os
import io
from datetime import datetime
from typing import Tuple, Optional
from PIL import Image
import streamlit as st


MAX_FILE_SIZE = 10 * 1024 * 1024
MAX_IMAGE_SIZE = 5 * 1024 * 1024
IMAGE_QUALITY = 85
MAX_IMAGE_DIMENSION = 1920

ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
ALLOWED_VIDEO_TYPES = ['video/mp4', 'video/mpeg', 'video/quicktime', 'video/x-msvideo']


def get_file_extension(file_name: str) -> str:
    """Get file extension from filename"""
    return os.path.splitext(file_name)[1].lower()


def is_image(file_type: str) -> bool:
    """Check if file is an image"""
    return file_type in ALLOWED_IMAGE_TYPES


def is_video(file_type: str) -> bool:
    """Check if file is a video"""
    return file_type in ALLOWED_VIDEO_TYPES


def compress_image(image_bytes: bytes, file_type: str) -> Tuple[bytes, bool]:
    """
    Compress image if it exceeds size limit

    Args:
        image_bytes: Original image bytes
        file_type: MIME type of image

    Returns:
        Tuple of (compressed_bytes, was_compressed)
    """
    try:
        original_size = len(image_bytes)

        if original_size <= MAX_IMAGE_SIZE:
            return image_bytes, False

        image = Image.open(io.BytesIO(image_bytes))

        if image.mode in ('RGBA', 'LA', 'P'):
            image = image.convert('RGB')

        width, height = image.size
        if width > MAX_IMAGE_DIMENSION or height > MAX_IMAGE_DIMENSION:
            if width > height:
                new_width = MAX_IMAGE_DIMENSION
                new_height = int(height * (MAX_IMAGE_DIMENSION / width))
            else:
                new_height = MAX_IMAGE_DIMENSION
                new_width = int(width * (MAX_IMAGE_DIMENSION / height))

            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        output = io.BytesIO()
        format_map = {
            'image/jpeg': 'JPEG',
            'image/jpg': 'JPEG',
            'image/png': 'PNG',
            'image/webp': 'WEBP'
        }
        save_format = format_map.get(file_type, 'JPEG')

        if save_format in ['JPEG', 'WEBP']:
            image.save(output, format=save_format, quality=IMAGE_QUALITY, optimize=True)
        else:
            image.save(output, format=save_format, optimize=True)

        compressed_bytes = output.getvalue()

        if len(compressed_bytes) < original_size:
            return compressed_bytes, True
        else:
            return image_bytes, False

    except Exception as e:
        print(f"Error compressing image: {str(e)}")
        return image_bytes, False


def validate_file(file, file_type: str) -> Tuple[bool, str]:
    """
    Validate uploaded file

    Args:
        file: Uploaded file object
        file_type: MIME type

    Returns:
        Tuple of (is_valid, error_message)
    """
    if file is None:
        return False, "No file selected"

    if file.size > MAX_FILE_SIZE:
        max_mb = MAX_FILE_SIZE / (1024 * 1024)
        return False, f"File size exceeds {max_mb:.0f}MB limit"

    if not (is_image(file_type) or is_video(file_type)):
        return False, "Only images (JPEG, PNG, WEBP) and videos (MP4, MPEG, MOV, AVI) are allowed"

    return True, ""


def generate_storage_path(site_code: str, report_date: str, activity_name: str, file_name: str) -> str:
    """
    Generate organized storage path for media files

    Args:
        site_code: Site code (e.g., TCB-407)
        report_date: Report date (YYYY-MM-DD)
        activity_name: Activity name
        file_name: Original file name

    Returns:
        Storage path string
    """
    date_obj = datetime.fromisoformat(report_date)
    year = date_obj.strftime('%Y')
    month = date_obj.strftime('%m')

    activity_clean = activity_name.replace(' ', '_').replace('/', '_')

    timestamp = datetime.now().strftime('%H%M%S')
    file_ext = get_file_extension(file_name)
    unique_filename = f"{activity_clean}_{timestamp}{file_ext}"

    path = f"{site_code}/{year}/{month}/{report_date}/{unique_filename}"

    return path


def upload_media_to_storage(supabase, file_bytes: bytes, storage_path: str, file_type: str) -> Tuple[bool, str]:
    """
    Upload media file to Supabase Storage

    Args:
        supabase: Supabase client
        file_bytes: File content as bytes
        storage_path: Path in storage bucket
        file_type: MIME type

    Returns:
        Tuple of (success, error_message)
    """
    try:
        bucket_name = 'dpr-media'

        response = supabase.storage.from_(bucket_name).upload(
            storage_path,
            file_bytes,
            file_options={"content-type": file_type}
        )

        return True, ""

    except Exception as e:
        error_msg = str(e)
        if "already exists" in error_msg.lower():
            return False, "File with this name already exists. Please try again."
        return False, f"Upload failed: {error_msg}"


def save_media_record(supabase, report_id: str, activity_name: str, file_name: str,
                     storage_path: str, file_type: str, file_size: int,
                     compressed: bool, user_id: str) -> Tuple[bool, str]:
    """
    Save media file record to database

    Args:
        supabase: Supabase client
        report_id: Report ID
        activity_name: Activity name
        file_name: Original file name
        storage_path: Storage path
        file_type: MIME type
        file_size: File size in bytes
        compressed: Whether file was compressed
        user_id: User ID who uploaded

    Returns:
        Tuple of (success, error_message)
    """
    try:
        data = {
            'report_id': report_id,
            'activity_name': activity_name,
            'file_name': file_name,
            'file_path': storage_path,
            'file_type': file_type,
            'file_size': file_size,
            'compressed': compressed,
            'uploaded_by': user_id
        }

        response = supabase.table('media_files').insert(data).execute()

        return True, ""

    except Exception as e:
        return False, f"Database error: {str(e)}"


def get_media_for_report(supabase, report_id: str) -> list:
    """
    Get all media files for a report

    Args:
        supabase: Supabase client
        report_id: Report ID

    Returns:
        List of media file records
    """
    try:
        response = supabase.table('media_files')\
            .select('*')\
            .eq('report_id', report_id)\
            .order('uploaded_at', desc=True)\
            .execute()

        return response.data if response.data else []

    except Exception as e:
        print(f"Error fetching media: {str(e)}")
        return []


def get_media_url(supabase, storage_path: str) -> Optional[str]:
    """
    Get public URL for media file

    Args:
        supabase: Supabase client
        storage_path: Path in storage bucket

    Returns:
        Public URL or None
    """
    try:
        bucket_name = 'dpr-media'

        response = supabase.storage.from_(bucket_name).get_public_url(storage_path)

        return response

    except Exception as e:
        print(f"Error getting media URL: {str(e)}")
        return None


def delete_media_file(supabase, media_id: str, storage_path: str) -> Tuple[bool, str]:
    """
    Delete media file from storage and database

    Args:
        supabase: Supabase client
        media_id: Media file ID
        storage_path: Path in storage bucket

    Returns:
        Tuple of (success, error_message)
    """
    try:
        bucket_name = 'dpr-media'

        supabase.storage.from_(bucket_name).remove([storage_path])

        supabase.table('media_files').delete().eq('id', media_id).execute()

        return True, ""

    except Exception as e:
        return False, f"Delete failed: {str(e)}"


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted string (e.g., "2.5 MB")
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def process_and_upload_media(supabase, uploaded_file, report_id: str, activity_name: str,
                            site_code: str, report_date: str, user_id: str) -> Tuple[bool, str]:
    """
    Complete workflow: validate, compress (if image), upload, and save record

    Args:
        supabase: Supabase client
        uploaded_file: Streamlit uploaded file object
        report_id: Report ID
        activity_name: Activity name
        site_code: Site code
        report_date: Report date
        user_id: User ID

    Returns:
        Tuple of (success, message)
    """
    is_valid, error_msg = validate_file(uploaded_file, uploaded_file.type)
    if not is_valid:
        return False, error_msg

    file_bytes = uploaded_file.read()
    compressed = False

    if is_image(uploaded_file.type):
        file_bytes, compressed = compress_image(file_bytes, uploaded_file.type)

    storage_path = generate_storage_path(site_code, report_date, activity_name, uploaded_file.name)

    success, error = upload_media_to_storage(supabase, file_bytes, storage_path, uploaded_file.type)
    if not success:
        return False, error

    success, error = save_media_record(
        supabase,
        report_id,
        activity_name,
        uploaded_file.name,
        storage_path,
        uploaded_file.type,
        len(file_bytes),
        compressed,
        user_id
    )

    if not success:
        return False, error

    size_str = format_file_size(len(file_bytes))
    compression_note = " (compressed)" if compressed else ""
    return True, f"File uploaded successfully: {size_str}{compression_note}"
def upload_image_to_storage(image_file, bucket_name, file_path):
    """
    Upload an image file to cloud storage (Supabase Storage)
    
    Args:
        image_file: The image file object from Streamlit file uploader
        bucket_name: Name of the storage bucket in Supabase
        file_path: Path where the file should be stored
    
    Returns:
        URL of the uploaded file or None if upload fails
    """
    try:
        import supabase
        
        # Initialize Supabase client
        supabase_url = st.secrets["supabase_url"]
        supabase_key = st.secrets["supabase_key"]
        client = supabase.create_client(supabase_url, supabase_key)
        
        # Upload file
        response = client.storage.from_(bucket_name).upload(
            path=file_path,
            file=image_file
        )
        
        # Return public URL
        return client.storage.from_(bucket_name).get_public_url(file_path)
    
    except Exception as e:
        st.error(f"Upload failed: {str(e)}")
        return None
