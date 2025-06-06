import subprocess
import os
import configparser
from urllib.parse import urlparse
import datetime

# Read config.ini
config = configparser.ConfigParser()
config.read("config.ini")

artifactory_user = config["artifactory"]["username"]
artifactory_token = config["artifactory"]["token"]

# Download directory
output_dir = os.path.join("utils", "downloads")
os.makedirs(output_dir, exist_ok=True)

def get_version_and_date():
    while True:
        version = input("Enter version number (e.g., IRI.26.02.03): ").strip()
        if not version:
            print("  Version number cannot be empty.")
            continue

        date_str = input("Enter release date (YYYYMMDD): ").strip()
        if not date_str:
            print("  Date cannot be empty.")
            continue
        try:
            datetime.datetime.strptime(date_str, "%Y%m%d")
        except ValueError:
            print("  Invalid date format. Please use YYYYMMDD.")
            continue

        return version, date_str

def build_download_links(version, date_str):
    base_url = f"https://spaws.jp.nissan.biz/artifactory/CCS_LGe/release/LGE/CDC/NISSAN/{version}/{date_str}/01.Android_Board_QNX"
    return [
        f"{base_url}/mcu/NCDCIVI_RELEASE_IMAGES.tar.gz",
        f"{base_url}/mcu/NCDCMETER_RELEASE_IMAGES.tar.gz",
        f"{base_url}/RELEASE_IMAGES.tar.gz.aa",
        f"{base_url}/RELEASE_IMAGES.tar.gz.ab"
    ]

def download_file(url, index, total, env):
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
        subprocess.run(curl_cmd, check=True, env=env)
        print("    Download completed.\n")
        return True

    except subprocess.CalledProcessError as e:
        print(f"    Download failed: {e}\n")
    except Exception as e:
        print(f"    Error: {e}\n")
    return False

def main():
    while True:
        version, date_str = get_version_and_date()
        download_urls = build_download_links(version, date_str)

        print(f"\nGenerated {len(download_urls)} download links. Starting download...\n")

        all_success = True
        for idx, url in enumerate(download_urls, start=1):
            success = download_file(url, idx, len(download_urls), env=os.environ.copy())
            if not success:
                all_success = False
                break  # Stop on first failure

        if all_success:
            print("All files downloaded successfully. Program finished.")
            return
        else:
            print("\nSome files failed to download. Please re-enter version and date to retry.\n")

if __name__ == "__main__":
    main()
