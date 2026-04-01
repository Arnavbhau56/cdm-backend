# Cloudinary storage service: uploads a PDF to Cloudinary and returns the secure URL.
# Local file cleanup is the caller's responsibility — do not delete here.

import cloudinary
import cloudinary.uploader
import os

cloudinary.config(
    cloud_name=os.environ['CLOUDINARY_CLOUD_NAME'],
    api_key=os.environ['CLOUDINARY_API_KEY'],
    api_secret=os.environ['CLOUDINARY_API_SECRET'],
)


def upload_to_cloudinary(local_path: str, public_id: str) -> str:
    """Upload PDF at local_path to Cloudinary. Returns the secure_url. Does NOT delete the local file."""
    result = cloudinary.uploader.upload(
        local_path,
        public_id=public_id,
        resource_type='raw',
        type='upload',
        access_mode='public',
        overwrite=True,
        invalidate=True,
    )
    return result['secure_url']
