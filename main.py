import os
import sys
import time
import subprocess
import configparser
from hardware.qualcomm_detector import find_qualcomm_device
from software.qfil_controller import run_qfil_controller
from software.fastboot_flash import run_fastboot_flash

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.ini")

# ========== Utility Functions ==========

def get_absolute_path(path):
    return path if os.path.isabs(path) else os.path.join(os.path.dirname(__file__), path)


def run_script(path):
    if not os.path.isfile(path):
        print(f"[ERROR] Script not found: {path}")
        return False

    env = dict(os.environ, PYTHONUNBUFFERED="1")
    proc = subprocess.Popen([sys.executable, '-u', path, '--called'],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, bufsize=1, env=env)

    success = False
    try:
        for line in proc.stdout:
            print(line.strip())
            if "[RESULT] SUCCESS" in line:
                success = True
            elif "[RESULT] FAIL" in line:
                success = False
    except Exception as e:
        print(f"[ERROR] Reading output failed: {e}")
    
    return success or proc.wait() == 0

def run_mcu_script(script_path, images_path):
    """Run MCU script with images_path parameter and return success status"""
    if not os.path.isfile(script_path):
        print(f"[ERROR] Script not found: {script_path}")
        return False

    try:
        # Call the script with images_path as argument
        result = subprocess.run([sys.executable, script_path, images_path], 
                              capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"[ERROR] Error running script {script_path}: {e}")
        return False



def download_and_extract():
    """Automatically download files from website"""
    print("Downloading files from file management website...")
    
    try:
        
        print("=== Starting download phase ===")
        # Call setup script to configure JFrog CLI
        download_script_path = os.path.join(os.path.dirname(__file__), 'download', 'setup_jfrog.py')
        if not os.path.exists(download_script_path):
            print(f"Download script not found: {download_script_path}")
            return None
        # Run download script
        result = subprocess.run([sys.executable, download_script_path], 
                              capture_output=False, text=True)
        if result.returncode != 0:
            print("Error occurred during download process")
            return None

        
        # Call download script
        download_script_path = os.path.join(os.path.dirname(__file__), 'download', 'download_by_version.py')
        if not os.path.exists(download_script_path):
            print(f"Download script not found: {download_script_path}")
            return None
        # Run download script
        result = subprocess.run([sys.executable, download_script_path], 
                              capture_output=False, text=True)
        if result.returncode != 0:
            print("Error occurred during download process")
            return None
            
        print("Download completed")
        
        # Call extraction script
        print("\n=== Starting extraction phase ===")
        unzipper_script_path = os.path.join(os.path.dirname(__file__), 'extract', 'unzipper.py')
        
        if not os.path.exists(unzipper_script_path):
            print(f"Extraction script not found: {unzipper_script_path}")
            return None
            
        # Run extraction script
        result = subprocess.run([sys.executable, unzipper_script_path], 
                              capture_output=False, text=True)
        
        if result.returncode != 0:
            print("Error occurred during extraction process")
            return None
            
        print("Extraction completed")
        
        # Set relative path to extracted directory
        extracted_base_path = "utils/extracted"
        
        print(f"Files downloaded and extracted to: {extracted_base_path}")
        print("Configuration paths updated to extracted directory")
        return True
        
    except Exception as e:
        print(f"Download/extraction process failed: {e}")
        return None


def flash_mcu_component(component_name, script_path, images_path):
    """Flash a specific MCU component with auto-retry on failure"""
    print(f"\n=== {component_name.upper()} Flashing ===")
    
    if component_name.upper() == "METER":
        print("Checking for METER board connection...")
        print("Please connect and power on Renesas METER board.")
    else:
        print(f"Connect and power on Renesas {component_name.upper()} board.")
        input(f"Press Enter when {component_name.upper()} board is ready...")
    
    while True:
        success = run_mcu_script(script_path, images_path)
        
        if success:
            print(f"[SUCCESS] MCU {component_name.upper()} flashing completed successfully!")
            break
        else:
            print(f"[ERROR] MCU {component_name.upper()} flashing failed, retrying in 5 seconds...")
            time.sleep(5)
            


def show_firmware_selection():
    print("\n=== Firmware Selection ===")
    while True:
        print("1. Download files via version number")
        print("2. Use existing config.ini settings")
        print("Type 'exit' to quit")
        choice = input("Select (1/2): ").strip().lower()
        if choice == "exit":
            return None
        elif choice == "1":
            if download_and_extract():
                return os.path.join("utils", "extracted")
        elif choice == "2":
            config = configparser.ConfigParser()
            config.read(CONFIG_PATH)
            return config['Firmware']['images_path']
        else:
            print("Invalid input. Enter 1, 2, or 'exit'.")

def find_folder(root_path, target_folder_name):
    for dirpath, dirnames, _ in os.walk(root_path):
        if target_folder_name in dirnames:
            return os.path.join(dirpath, target_folder_name)
    return None

def main():
    print("=== Firmware Flashing Tool ===")
    images_path = show_firmware_selection()
    if not images_path:
        print("Exiting.")
        return

    abs_images_path = get_absolute_path(images_path)
    print(f"\nUsing images path: {images_path} -> {abs_images_path}")

    
    # === Check for sail_nor directory ===
    sail_nor_path = find_folder(abs_images_path, 'sail_nor')
    if  not sail_nor_path:
        print(f"[ERROR] Required folder 'sail_nor' not found in: {abs_images_path}")
        print("Please ensure that the images_path in the configuration file is correctly set to the path of the image files.")
        sys.exit(1)

    if not os.listdir(sail_nor_path):
        print("[INFO] 'sail_nor' folder is empty,identified as KOH image file.")
        skip_qfil = True
    else:
        print("[INFO] Identified as IRI image file.")
        skip_qfil = False



    # QFIL
    if not skip_qfil:
        print("\n" + "="*50)
        print("Starting QFIL Flashing Phase")
        print("="*50)
        print("Please connect device in EDL mode (DLOAD) to continue...")
        while True:
            port, is_edl_mode = find_qualcomm_device()
            if port and is_edl_mode:
                print(f"Device detected (Port: {port}, Mode: DLOAD)")
                try:
                    print("Starting QFIL flashing...")
                    print("Waiting for device to stabilize...")
                    time.sleep(5)
                    print("Running QFIL controller script...")
                    if not run_qfil_controller(abs_images_path):
                        print("[ERROR] QFIL flashing failed, please check connection and try again.")
                        print("Please connect device in EDL mode to continue...")
                        continue
                    print("QFIL flashing completed successfully")
                    break
                except Exception as e:
                    print(f"[ERROR] Error during execution: {e}")
                    continue
    else:
        print("\n[INFO] Skipping QFIL flashing phase because 'sail_nor' folder is empty.")



    # Fastboot and run fastboot script
    print("\n" + "="*50)
    print("Starting Fastboot Flashing Phase")
    print("="*50)
    print("Please connect device in NORMAL mode to continue...")
    while True:
        port, is_edl_mode = find_qualcomm_device()
        if port and not is_edl_mode:
            print(f"Device detected (Port: {port}, Mode: NORMAL)")
            print("Please disconnect device from EDL mode and connect in Fastboot mode.")
            try:
                print("Running fastboot flash script...")
                print("Waiting for device to stabilize...")
                time.sleep(5) 
                print("Starting fastboot flash...")
                if not run_fastboot_flash(abs_images_path):
                    print("[ERROR] Fastboot flash failed, please check connection and try again.")
                    print("Please connect device in NORMAL mode to continue...")
                    continue
                print("Fastboot flashing completed successfully")
                break
            except Exception as e:
                print(f"[ERROR] Fastboot and run fastboot script failed: {e}")
                continue


    # MCU Components Flashing
    print("\n" + "="*50)
    print("Starting MCU Components Flashing Phase")
    print("="*50)
    
    # MCU METER - with automatic connection checking and retry
    flash_mcu_component("METER", get_absolute_path('software/MCU_METER_controller.py'), abs_images_path)
    
    # Pause between METER and IVI
    print("\n" + "-"*50)
    print("METER flashing completed. Now preparing for IVI flashing...")
    print("Please disconnect METER board and connect IVI board...")

    # MCU IVI - with user confirmation and retry
    flash_mcu_component("IVI", get_absolute_path('software/MCU_IVI_controller.py'), abs_images_path)
    
    print("\n" + "="*50)
    print("All flashing operations completed!")
    print("="*50)

if __name__ == "__main__":
    main()
