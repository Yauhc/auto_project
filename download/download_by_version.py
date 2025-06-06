import subprocess
import os
import configparser
from urllib.parse import urlparse
import json

# Read config.ini
config = configparser.ConfigParser()
config.read("config.ini")

artifactory_user = config["artifactory"]["username"]
artifactory_token = config["artifactory"]["token"]

# Download directory
output_dir = os.path.join("utils", "downloads")
os.makedirs(output_dir, exist_ok=True)

def get_version():
    while True:
        version = input("Enter version number (e.g., IRI.26.02.03): ").strip()
        if not version:
            print("Version number cannot be empty.")
            continue
        return version

def find_download_links(version, server_id='nissan-artifactory'):
    jf_exe = os.path.join("utils", "jf.exe")
    download_base = "https://spaws.jp.nissan.biz/artifactory/"

    # Set environment variables for authentication
    env = os.environ.copy()
    env['JFROG_CLI_OFFER_CONFIG'] = 'false'
    env['JFROG_CLI_USER'] = artifactory_user
    env['JFROG_CLI_PASSWORD'] = artifactory_token

    # Search path without date, directly under the version folder
    repository_path = f'CCS_LGe/release/LGE/CDC/NISSAN/{version}/'

    command = [
        jf_exe,
        'rt', 's',
        repository_path + '**',
        '--server-id', server_id,
        '--recursive=true',
        '--include-dirs=false'
    ]

    print(f"Running command: {' '.join(command)}")

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
    )

    if result.returncode != 0:
        print("Error querying Artifactory")
        print(result.stderr)
        return []

    try:
        json_data = json.loads(result.stdout.strip())
    except json.JSONDecodeError:
        print("Failed to parse JSON output")
        return []

    target_files = {
        'RELEASE_IMAGES.tar.gz.aa',
        'RELEASE_IMAGES.tar.gz.ab',
        'NCDCIVI_RELEASE_IMAGES.tar.gz',
        'NCDCMETER_RELEASE_IMAGES.tar.gz'
    }

    download_urls = []
    for item in json_data:
        path = item.get("path", "")
        if any(tf in path for tf in target_files):
            repo = item.get('repo', '')
            full_url = f"{download_base}{repo}/{path}"
            download_urls.append(full_url)

    if not download_urls:
        print("No target files found for this version.")

    return download_urls

def download_file(url, index, total):
    try:
        filename = os.path.basename(urlparse(url).path)
        if not filename:
            raise ValueError("Invalid download URL, unable to parse filename.")

        output_path = os.path.join(output_dir, filename)

        curl_cmd = [
            "curl",
            "-u", f"{artifactory_user}:{artifactory_token}",
            "-o", output_path,
            url
        ]

        print(f"[{index}/{total}] Downloading: {url}")
        print(f"    Saving to: {output_path}")
        subprocess.run(curl_cmd, check=True)
        print("    Download completed.\n")
        return True

    except subprocess.CalledProcessError as e:
        print(f"    Download failed: {e}\n")
    except Exception as e:
        print(f"    Error: {e}\n")
    return False

def main():
    while True:
        version = get_version()
        download_urls = find_download_links(version)

        if not download_urls:
            print("No files found to download. Please check the version and try again.\n")
            continue

        print(f"\nFound {len(download_urls)} files to download. Starting download...\n")

        all_success = True
        for idx, url in enumerate(download_urls, start=1):
            success = download_file(url, idx, len(download_urls))
            if not success:
                all_success = False
                break

        if all_success:
            print("All files downloaded successfully. Program finished.")
            return
        else:
            print("\nSome files failed to download. Please try again.\n")

if __name__ == "__main__":
    main()