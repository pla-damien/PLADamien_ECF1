from minio import Minio
import requests
from io import BytesIO

class MinioImageStorage:
    def __init__(self, endpoint, access_key, secret_key, bucket):
        self.client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=False
        )
        self.bucket = bucket

        if not self.client.bucket_exists(bucket):
            self.client.make_bucket(bucket)

    def upload_image_from_url(self, image_url: str, object_name: str):
        response = requests.get(image_url, stream=True)
        response.raise_for_status()

        image_bytes = BytesIO(response.content)

        self.client.put_object(
            bucket_name=self.bucket,
            object_name=object_name,
            data=image_bytes,
            length=len(response.content),
            content_type="image/jpeg"
        )
