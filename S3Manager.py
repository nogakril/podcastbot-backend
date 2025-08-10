import boto3
from datetime import datetime

KEY = ""
SECRET = ""


class S3Manager:
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name
        self.session = boto3.Session(aws_access_key_id=KEY,
                                     aws_secret_access_key=SECRET)
        self.s3 = self.session.client('s3')

    def upload_file(self, file_path, folder_key):
        cur_time = datetime.now()
        print("Uploading file. Start time: ", cur_time)
        file_name = file_path.split("/")[-1]
        self.s3.upload_file(file_path, self.bucket_name, f"{folder_key}{file_name}", ExtraArgs={'ACL': 'public-read'})
        print("File uploaded. Time taken: ", datetime.now() - cur_time)
        return f"{folder_key}{file_name}"

    def create_folder(self, timestamp):
        folder_name = f"recordings-{timestamp}"
        folder_key = f"{folder_name}/"
        self.s3.put_object(Bucket=self.bucket_name, Key=folder_key)
        print(f"Folder created: {folder_name}")
        return folder_key

    def get_recording_url(self, file_path, folder_key):
        file_name = file_path.split("/")[-1]
        return f"https://{self.bucket_name}.s3.amazonaws.com/{folder_key}{file_name}"
