import requests
from bs4 import BeautifulSoup
import os
import re
from urllib.parse import urljoin

def get_latest_file_url(base_url):
    """
    Fetch the latest file URL from the given website.
    :param base_url: The URL of the website to scrape.
    :return: The URL of the latest file, or None if not found.
    """
    try:
        response = requests.get(base_url)
        response.raise_for_status()  # Check for HTTP request errors
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all file links (adjust the selector based on the website structure)
        file_links = soup.find_all('a', href=True)
        file_urls = [link['href'] for link in file_links if link['href'].endswith('.zip')]  # Example: filter .zip files

        if file_urls:
            # Assuming the latest file is the first one in the list
            latest_file_url = file_urls[0]
            print(f"Latest file URL: {latest_file_url}")
            return latest_file_url
        else:
            print("No files found on the website.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the website: {e}")
        return None

def get_all_file_urls(base_url):
    """
    Fetch all file URLs from the given website, including those triggered by JS buttons.
    """
    try:
        response = requests.get(base_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        file_urls = []

        # 1. 先抓取传统的<a href="...">文件链接
        exts = ('.zip', '.rar', '.tar.gz', '.tar', '.7z', '.gz', '.bz2', '.xz', '.exe', '.pdf', '.doc', '.docx', '.pyc')
        file_links = soup.find_all('a', href=True)
        file_urls += [urljoin(base_url, link['href']) for link in file_links if link['href'].lower().endswith(exts)]

        # 2. 再抓取<button onclick="TL.download_direct('...')">类型的链接
        button_links = soup.find_all('button', onclick=True)
        for btn in button_links:
            m = re.search(r"TL\.download_direct\('([a-zA-Z0-9]+)'\)", btn['onclick'])
            if m:
                file_id = m.group(1)
                # 你需要根据实际规则拼接下载链接，这里举例：
                # 假设你能从页面其它地方或接口获得完整的下载URL
                # 这里直接拼接示例（实际可能需要更多参数）
                download_url = f"https://tmp-hd101.vx-cdn.com/file-{file_id}-6825522c559ff/__init__.cpython-310.pyc"
                file_urls.append(download_url)

        if file_urls:
            print(f"Found file URLs: {file_urls}")
            return file_urls
        else:
            print("No files found on the website.")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the website: {e}")
        return []

def download_file(url, save_dir):
    """
    Download a file from the given URL and save it to the specified directory.
    :param url: The URL of the file to download.
    :param save_dir: The directory to save the downloaded file.
    :return: The name of the downloaded file, or None if failed.
    """
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    file_name = url.split("/")[-1]
    file_path = os.path.join(save_dir, file_name)

    try:
        print(f"Downloading {url} to {file_path}...")
        with requests.get(url, stream=True) as response:
            response.raise_for_status()
            with open(file_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
        print(f"Download completed: {file_path}")
        return file_name
    except requests.exceptions.RequestException as e:
        print(f"Download failed: {e}")
        return None

if __name__ == "__main__":
    # Step 1: Get all file URLs
    website_url = "https://www.ttttt.link/?tmpui_page=/app&listview=workspace"
    file_urls = get_all_file_urls(website_url)

    # Step 2: Download all files
    if file_urls:
        save_directory = os.path.join(os.path.dirname(__file__), "downloads")
        for url in file_urls:
            download_file(url, save_directory)