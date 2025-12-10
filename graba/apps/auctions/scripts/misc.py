import uuid
import os

def auction_image_upload_to(instance, filename):
    ext = filename.split('.')[-1]  # save file extension
    filename = f"{uuid.uuid4()}.uploaded-auction-image.{ext}"
    return os.path.join("auctions", filename)
