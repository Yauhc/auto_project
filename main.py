from download.fetcher import download_file
from extract.unzipper import unzip_file
import os

if __name__ == "__main__":
    # Step 1: Download the file
    url = "https://tmp-hd105.vx-cdn.com/file-681db20216049-681db21135932/checker.zip"  # Replace with your download link
    save_dir = os.path.join(os.path.dirname(__file__), "download", "downloads")  # Use relative path
    downloaded_file_name = download_file(url, save_dir)

    if downloaded_file_name:
        # Step 2: Get the full path of the downloaded file
        zip_path = os.path.join(save_dir, downloaded_file_name)

        # Step 3: Unzip the file
        extract_to = os.path.join(os.path.dirname(__file__), "extract", "output")  # Use relative path
        extracted_path = unzip_file(zip_path, extract_to)

        print(f"Downloaded file: {zip_path}")
        print(f"Files extracted to: {extracted_path}")