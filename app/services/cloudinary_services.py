import cloudinary.uploader
from fastapi import UploadFile


def upload_image(
    file: UploadFile,
    folder: str
):
    response =  cloudinary.uploader.upload(
        file.file,
        asset_folder = folder,
        resource_type = "image"
    )

    # if not response:
    #     raise an exception for image errors, ill do that later

    return {
        "url": response["secure_url"],
        "public_id": response["public_id"],
    }
    
    