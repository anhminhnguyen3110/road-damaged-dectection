import os
import boto3
from botocore import UNSIGNED
from botocore.client import Config

bucket_name = "ai-for-eng"

def get_pt_files_from_s3(bucket_name = bucket_name, prefix=''):
    # Create an S3 client with unsigned config (no credentials needed)
    s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED), region_name='ap-southeast-2')
    
    try:
        paginator = s3.get_paginator('list_objects_v2')
        page_iterator = paginator.paginate(Bucket=bucket_name, Prefix=prefix)

        pt_files = []
        for page in page_iterator:
            if 'Contents' in page:
                pt_files.extend([obj['Key'] for obj in page['Contents'] if obj['Key'].endswith('.pt')])
        
        return pt_files

    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def download_file(bucket_name, key, local_path):
    s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED), region_name='ap-southeast-2')
    try:
        s3.download_file(bucket_name, key, local_path)
        print(f"Downloaded: {local_path}")
    except Exception as e:
        print(f"Failed to download {key}: {e}")

def check_and_download_model(bucket_name, key):
    # Create the 'models' directory if it doesn't exist
    if not os.path.exists('models'):
        os.makedirs('models')

    # Path to the local file
    local_file_path = os.path.join('models', os.path.basename(key))

    # Check if the file already exists
    if os.path.exists(local_file_path):
        print(f"{os.path.basename(key)} already exists. Skipping download.")
    else:
        # Download the file from S3
        download_file(bucket_name, key, local_file_path)

if __name__ == "__main__":
    prefix = ""  # If your files are in a subfolder, specify the prefix here

    pt_files = get_pt_files_from_s3(bucket_name, prefix)
    print(pt_files)
    # for key in pt_files:
    #     check_and_download_model(bucket_name, key)