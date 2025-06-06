import subprocess
import os
import sys

def find_ivi_image(folder):
    """Search for a .s19 file that contains 'NCDCIVI' and does NOT contain 'VHSM'"""
    for root, _, files in os.walk(folder):
        for file in files:
            if file.endswith('.s19') and 'NCDCIVI' in file and 'VHSM' not in file:
                return os.path.join(root, file)
    return None

def find_rfp_exe(search_root):
    """Search recursively under search_root for rfp-cli.exe"""
    for root, _, files in os.walk(search_root):
        for file in files:
            if file.lower() == 'rfp-cli.exe':
                return os.path.join(root, file)
    return None

def main(images_path=None):
    base_dir = os.path.dirname(os.path.abspath(__file__))

    if images_path is None:
        # Default to ../utils/extracted directory
        images_path = os.path.abspath(os.path.join(base_dir, '..', 'utils', 'extracted'))
        print(f"[INFO] No images_path passed, using default: {images_path}")
    else:
        images_path = os.path.abspath(images_path)

    if not os.path.isdir(images_path):
        print(f"[ERROR] Provided images_path is not a directory: {images_path}")
        exit(1)

    utils_dir = os.path.abspath(os.path.join(base_dir, '..', 'utils'))

    image_abs_path = find_ivi_image(images_path)
    if not image_abs_path:
        print(f"[ERROR] No valid .s19 image found in {images_path}")
        exit(1)

    rfp_path = find_rfp_exe(utils_dir)
    if not rfp_path:
        print(f"[ERROR] rfp-cli.exe not found under {utils_dir}")
        exit(1)

    print(f"[INFO] RFP tool path: {rfp_path}")
    print(f"[INFO] Image file path: {image_abs_path}")

    command = (
        f'"{rfp_path}" '
        '-d RH850 -tool E2 -if uart -osc 8.0 '
        '-fo opbt FA27FFCF,FFFFFDFF,FFFFFFFF,FFFFFFFF,FFFFFFFF,FFFFFFFF,FFFFFFFF,FFFFFFFF '
        '-e -p -v '
        f'-file "{image_abs_path}" '
        '-reset'
    )

    print(f"[INFO] Executing command: {command}")
    print("-" * 80)

    try:
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=True) as proc:
            for line in proc.stdout:
                print(line, end='')
            return_code = proc.wait()

        print("-" * 80)
        if return_code == 0:
            print("[INFO] MCU IVI programming completed successfully")
        else:
            print(f"[ERROR] MCU IVI programming failed, return code: {return_code}")
            exit(return_code)

    except Exception as e:
        print(f"[ERROR] Exception occurred during MCU IVI programming: {e}")
        exit(1)

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        main(images_path=sys.argv[1])
    else:
        main()
