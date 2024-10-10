import os
import requests

repo_owner = "anhminhnguyen3110"
repo_name = "Road-damaged-dectection-models"
folder_path = ""

def get_pt_files_from_github(repo_owner = "anhminhnguyen3110", repo_name = "Road-damaged-dectection-models", folder_path=""):
    # GitHub API URL for the repository content
    api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{folder_path}"
    try:
        response = requests.get(api_url)
        response.raise_for_status()  

        files = response.json()
        pt_files = [file for file in files if file['name'].endswith('.pt')]
        return pt_files

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return []

def download_file(url, local_path):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Ensure the request was successful
        with open(local_path, 'wb') as file:
            file.write(response.content)
        # print(f"Downloaded: {local_path}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to download {url}: {e}")

def check_and_download_model(pt_file):
    # Create the 'models' directory if it doesn't exist
    if not os.path.exists('models'):
        os.makedirs('models')

    # Path to the local file
    local_file_path = os.path.join('models', pt_file['name'])

    # Check if the file already exists
    if os.path.exists(local_file_path):
        print(f"{pt_file['name']} already exists. Skipping download.")
    else:
        # Download the file from GitHub
        download_url = pt_file['download_url']
        download_file(download_url, local_file_path)