import os
import boto3
from botocore import UNSIGNED
from botocore.client import Config
import requests

bucket_name = "ai-for-eng"

def get_pt_files(repo_owner="anhminhnguyen3110", repo_name="Road-damaged-dectection-models", folder_path="", bucket_name=bucket_name, prefix=""):
    # Try to get .pt files from GitHub
    try:
        pt_files = get_pt_files_from_github(repo_owner, repo_name, folder_path)
        source = 'github'
        pt_files = [file['name'] for file in pt_files]
        # throw an exception if no .pt files are found
        return pt_files, source
    except Exception as e:
        print(f"An error occurred while accessing GitHub: {e}")
        # If GitHub fails, try S3
        try:
            pt_files = get_pt_files_from_s3(bucket_name, prefix)
            source = 's3'
            return pt_files, source
        except Exception as e:
            print(f"An error occurred while accessing S3: {e}")
            return None, None

def get_pt_files_from_github(repo_owner, repo_name, folder_path):
    api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{folder_path}"
    response = requests.get(api_url)
    response.raise_for_status()
    files = response.json()
    pt_files = [file for file in files if file['name'].endswith('.pt')]
    return pt_files

def get_pt_files_from_s3(bucket_name, prefix=''):
    s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED), region_name='ap-southeast-2')
    paginator = s3.get_paginator('list_objects_v2')
    page_iterator = paginator.paginate(Bucket=bucket_name, Prefix=prefix)
    pt_files = []
    for page in page_iterator:
        if 'Contents' in page:
            pt_files.extend([obj['Key'] for obj in page['Contents'] if obj['Key'].endswith('.pt')])
    return pt_files

def check_and_download_model(pt_file, source, bucket_name=bucket_name):
    if not os.path.exists('models'):
        os.makedirs('models')
    if source == 'github':
        local_file_path = os.path.join('models', pt_file)
        if os.path.exists(local_file_path):
            print(f"{pt_file} already exists. Skipping download.")
        else:
            try:
                download_url = pt_file['download_url']
                response = requests.get(download_url)
                response.raise_for_status()
                with open(local_file_path, 'wb') as file:
                    file.write(response.content)
                print(f"Downloaded from GitHub: {local_file_path}")
            except Exception as e:
                print(f"Failed to download {pt_file} from GitHub: {e}")
                # If download from GitHub fails, try S3
                try:
                    key = pt_file
                    download_file_from_s3(key, local_file_path, bucket_name)
                except Exception as e:
                    print(f"Failed to download {key} from S3: {e}")
    elif source == 's3':
        local_file_path = os.path.join('models', os.path.basename(pt_file))
        if os.path.exists(local_file_path):
            print(f"{os.path.basename(pt_file)} already exists. Skipping download.")
        else:
            try:
                download_file_from_s3(pt_file, local_file_path, bucket_name)
            except Exception as e:
                print(f"Failed to download {pt_file} from S3: {e}")
    else:
        print("Unknown source.")

def download_file_from_s3(key, local_path, bucket_name):
    s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED), region_name='ap-southeast-2')
    s3.download_file(bucket_name, key, local_path)
    print(f"Downloaded from S3: {local_path}")

if __name__ == "__main__":
    pt_files, source = get_pt_files()
    print(pt_files)
    # if pt_files and source:
    #     for pt_file in pt_files:
    #         check_and_download_model(pt_file, source)
    # else:
    #     print("Failed to retrieve .pt files from both GitHub and S3.")