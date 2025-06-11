import os
import zipfile
import tarfile
import shutil
from collections import defaultdict

# Relative paths
DOWNLOAD_DIR = os.path.join("utils", "downloads")
EXTRACT_DIR = os.path.join("utils", "extracted")

def unzip_file(zip_path, extract_to):
    zip_name = os.path.splitext(os.path.basename(zip_path))[0]
    target_dir = os.path.join(extract_to, zip_name)
    os.makedirs(target_dir, exist_ok=True)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(target_dir)
    print(f"Unzipped {zip_path} to {target_dir}")
    os.remove(zip_path)  # Delete source file after extraction
    print(f"Deleted source file {zip_path}")
    return target_dir

def extract_tar_gz(tar_gz_path, extract_to):
    base_name = os.path.splitext(os.path.splitext(os.path.basename(tar_gz_path))[0])[0]
    target_dir = os.path.join(extract_to, base_name)
    os.makedirs(target_dir, exist_ok=True)
    print(f"Extracting {tar_gz_path} to {target_dir}...")
    with tarfile.open(tar_gz_path, 'r:gz') as tar:
        tar.extractall(path=target_dir)
    print(f"Extraction complete: {target_dir}")
    os.remove(tar_gz_path)  # Delete source file after extraction
    print(f"Deleted source file {tar_gz_path}")

def merge_files(file_parts, output_file):
    if os.path.exists(output_file):
        os.remove(output_file)
    with open(output_file, 'wb') as merged_file:
        for part in sorted(file_parts):
            with open(part, 'rb') as part_file:
                merged_file.write(part_file.read())
    print(f"Merged files into {output_file}")

    # Delete the part files after merging
    for part in file_parts:
        os.remove(part)
        print(f"Deleted part file {part}")

    return output_file

def clear_extract_dir(extract_dir):
    if os.path.exists(extract_dir):
        for item in os.listdir(extract_dir):
            item_path = os.path.join(extract_dir, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
        print(f"Cleared all contents of {extract_dir}")
    else:
        os.makedirs(extract_dir)
        print(f"Created extract directory: {extract_dir}")

def find_and_process_all(download_dir, extract_dir):
    clear_extract_dir(extract_dir)

    merged_tar_groups = defaultdict(list)

    for file in os.listdir(download_dir):
        file_path = os.path.join(download_dir, file)
        if file.endswith(".zip"):
            print(f"Processing zip file: {file_path}")
            unzip_file(file_path, extract_dir)

        elif any(file.endswith(ext) for ext in [".tar.gz.aa", ".tar.gz.ab", ".tar.gz.ac", ".tar.gz.ad"]):
            base = file.split(".tar.gz.")[0] + ".tar.gz"
            merged_tar_groups[base].append(file_path)

        elif file.endswith(".tar.gz"):
            print(f"Processing tar.gz file: {file_path}")
            extract_tar_gz(file_path, extract_dir)

    for base_name, parts in merged_tar_groups.items():
        merged_path = os.path.join(download_dir, base_name)
        print(f"Merging parts into: {merged_path}")
        merge_files(parts, merged_path)
        extract_tar_gz(merged_path, extract_dir)

if __name__ == "__main__":
    find_and_process_all(DOWNLOAD_DIR, EXTRACT_DIR)
