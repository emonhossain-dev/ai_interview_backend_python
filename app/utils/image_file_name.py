import uuid
import time
import os

def generate_image_name(email: str, ext: str):
    safe_email = email.split("@")[0]  # শুধু username part
    random_part = uuid.uuid4().hex[:6]  # random 6 chars
    timestamp = int(time.time())  # current unix time

    filename = f"{safe_email}_{random_part}_{timestamp}.{ext}"
    return filename