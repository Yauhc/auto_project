# -*- coding: utf-8 -*-
import os
import requests
from urllib.parse import urlparse

def download_file(url, save_dir, filename=None):
    """
    Download a file to the local directory and return the file name.
    :param url: URL of the file to download (e.g., https://example.com/file.zip)
    :param save_dir: Directory to save the downloaded file (e.g., Z:\\projects\\auto_project\\download\\downloads)
    :param filename: Optional custom filename for the downloaded file
    :return: Name of the downloaded file
    """
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    # If no filename is specified, extract it from the URL and clean it
    if not filename:
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)  # Extract the file name from the URL path
    
    file_path = os.path.join(save_dir, filename)
    
    try:
        print(f"Downloading {url} to {file_path}...")
        with requests.get(url, stream=True) as response:
            response.raise_for_status()  # Check if the request was successful
            with open(file_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  # Filter out keep-alive chunks
                        file.write(chunk)
        
        print(f"Download completed: {file_path}")
        return filename  # Return the file name
    except requests.exceptions.RequestException as e:
        print(f"Download failed: {e}")
        return None

# Example usage
if __name__ == "__main__":
    url = "https://download.visualstudio.microsoft.com/download/pr/8fada5c7-8417-4239-acc3-bd499af09222/662cfafc84e8b026c2a0c57850d7e0ba3e736d5d774520401a63f55b9fdd7ff9/vs_BuildTools.exe"  # Replace with your download link
    save_dir = os.path.join(os.path.dirname(__file__), "downloads")  # Replace with your save directory
    downloaded_file_name = download_file(url, save_dir)
    if downloaded_file_name:
        print(f"Downloaded file name: {downloaded_file_name}")