import os
import zipfile
import tarfile

def unzip_file(zip_path, extract_to):
    """
    Extract a zip file into a folder named after the zip file, preserving folder structure and names.
    :param zip_path: Path to the zip file (e.g., Z:\\projects\\auto_project\\download\\downloads\\checker.zip)
    :param extract_to: Directory to extract the contents to (e.g., Z:\\projects\\auto_project\\extract\\output)
    :return: Path to the extraction directory
    """
    # Ensure the extraction directory exists
    if not os.path.exists(extract_to):
        os.makedirs(extract_to)

    # Create a subdirectory named after the zip file (without extension)
    zip_name = os.path.splitext(os.path.basename(zip_path))[0]
    target_dir = os.path.join(extract_to, zip_name)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # Extract the zip file into the target directory
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(target_dir)

    return target_dir

def unzip_multiple_files(zip_paths, extract_to):
    """
    Extract multiple zip files into separate folders named after each zip file.
    :param zip_paths: List of paths to zip files.
    :param extract_to: Directory to extract the contents to.
    """
    for zip_path in zip_paths:
        print(f"Extracting {zip_path}...")
        extracted_path = unzip_file(zip_path, extract_to)
        print(f"Files extracted to: {extracted_path}")

def merge_files(file_parts, output_file):
    """
    Merge multiple file parts into a single file.
    :param file_parts: List of file parts to merge (e.g., ['file.aa', 'file.ab']).
    :param output_file: Path to the output file (e.g., 'file.tar.gz').
    """
    # 检查输出文件是否已存在，如果存在则删除
    if os.path.exists(output_file):
        print(f"File {output_file} already exists. Deleting it...")
        os.remove(output_file)

    # 合并文件
    with open(output_file, 'wb') as merged_file:
        for part in file_parts:
            print(f"Merging {part} into {output_file}...")
            with open(part, 'rb') as part_file:
                merged_file.write(part_file.read())
    print(f"Merge complete: {output_file}")

def extract_tar_gz(tar_gz_path, extract_to):
    """
    Extract a .tar.gz file to the specified directory.
    :param tar_gz_path: Path to the .tar.gz file.
    :param extract_to: Directory to extract the contents to.
    """
    if not os.path.exists(extract_to):
        os.makedirs(extract_to)

    print(f"Extracting {tar_gz_path} to {extract_to}...")
    with tarfile.open(tar_gz_path, 'r:gz') as tar:
        tar.extractall(path=extract_to)
    print(f"Extraction complete: {extract_to}")

# Example usage
if __name__ == "__main__":
    # 选择两个分割文件
    file_parts = [
        r"C:\\Yang\\Files\\NISSAN\\Image\\RELEASE_IMAGES.tar.gz.aa",
        r"C:\\Yang\\Files\\NISSAN\\Image\\RELEASE_IMAGES.tar.gz.ab"
    ]
    # 合并后的输出文件路径
    output_file = r"C:\\Yang\\Files\\NISSAN\\Image\\RELEASE_IMAGES.tar.gz"
    # 调用合并函数
    merge_files(file_parts, output_file)

    # Step 2: Extract the merged .tar.gz file
    extract_to = r"C:\\Yang\\Files\\NISSAN\\Image\\Extracted"
    extract_tar_gz(output_file, extract_to)