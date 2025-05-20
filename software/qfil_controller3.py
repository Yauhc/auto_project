import subprocess
import time
import pyautogui
import os
import sys
import pygetwindow as gw
import pyperclip
import threading
import argparse
import yaml


# === Configuration ===
QFIL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../utils/QFIL/Qualcomm_Flash_Image_Loader_v2.0.3.5/Qualcomm_Flash_Image_Loader_v2.0.3.5/QFIL.exe"))
WINDOW_TITLE_KEYWORDS = ("QFIL",)
NEW_WINDOW_POSITION = (423, 125)
NEW_WINDOW_SIZE = (1000, 750)
PROGRESS_PIXEL = (1402, 619)
CLICK_POSITIONS = {
    "select_port": (495, 280),
    "firehose_btn": (1306, 356),
    "rawprogram_btn": (1320, 550),
    "patch_btn": (1315, 590),
}
FILE_PATHS = {
    "firehose": r"C:\Users\CHP00015\Desktop\Image new one\RELEASE_IMAGES\2025-04-28_21_25\prog_firehose_ddr.elf",
    "rawprogram": r"C:\Users\CHP00015\Desktop\Image new one\RELEASE_IMAGES\2025-04-28_21_25\sail_nor\rawprogram0.xml",
    "patch": r"C:\Users\CHP00015\Desktop\Image new one\RELEASE_IMAGES\2025-04-28_21_25\sail_nor\patch0.xml",
}

# === Utility Functions ===

def paste_file_path(filepath):
    pyperclip.copy(filepath)
    pyautogui.hotkey('ctrl', 'v')
    pyautogui.press('enter')
    print(f"Pasted: {filepath}")

def launch_qfil():
    if os.path.exists(QFIL_PATH):
        print(f"Launching QFIL: {QFIL_PATH}")
        os.startfile(QFIL_PATH)
    else:
        print(f"Error: QFIL not found at {QFIL_PATH}")
        sys.exit(1)

def wait_for_qfil_window(keywords=WINDOW_TITLE_KEYWORDS, timeout=20):
    print("Waiting for QFIL window...")
    existing_ids = set(w._hWnd for w in gw.getAllWindows())
    for _ in range(timeout * 2):
        for w in gw.getAllWindows():
            if w._hWnd not in existing_ids:
                if any(kw.lower() in w.title.lower() for kw in keywords) and w.width > 500 and w.height > 300:
                    print(f"Found QFIL window: {w.title}")
                    return w
        time.sleep(0.5)
    print("Error: QFIL window not found.")
    return None

def monitor_new_windows(position=NEW_WINDOW_POSITION, size=NEW_WINDOW_SIZE):
    print("Window monitor started.")
    known_windows = set(w._hWnd for w in gw.getAllWindows())
    while True:
        for win in gw.getAllWindows():
            if win._hWnd not in known_windows:
                print(f"[Monitor] New window: {win.title}")
                try:
                    win.moveTo(*position)
                    win.resizeTo(*size)
                    print(f"[Monitor] Resized to {size} at {position}")
                except Exception as e:
                    print(f"[Monitor] Resize failed: {e}")
                known_windows.add(win._hWnd)
        time.sleep(0.5)

def configure_qfil():
    try:
        print("Starting QFIL configuration...")
        time.sleep(3)

        pyautogui.click(CLICK_POSITIONS["select_port"])
        print("Clicked: Select Port")

        pyautogui.click(CLICK_POSITIONS["firehose_btn"])
        print("Clicked: Firehose Button")
        time.sleep(1)
        paste_file_path(FILE_PATHS["firehose"])

        time.sleep(1)
        pyautogui.click(CLICK_POSITIONS["rawprogram_btn"])
        print("Clicked: Rawprogram Button")
        time.sleep(1)
        paste_file_path(FILE_PATHS["rawprogram"])

        time.sleep(1)
        paste_file_path(FILE_PATHS["patch"])

        time.sleep(1)
        pyautogui.click(CLICK_POSITIONS["patch_btn"])
        print("Clicked: Final Confirm Button")

        print("QFIL configuration complete.")

    except Exception as e:
        print(f"Error during QFIL configuration: {e}")

def monitor_progress_bar(pixel=PROGRESS_PIXEL):
    try:
        print("Monitoring progress bar...")
        x, y = pixel
        initial_color = None
        while True:
            screenshot = pyautogui.screenshot(region=(x, y, 1, 1))
            color = screenshot.getpixel((0, 0))
            if initial_color is None:
                initial_color = color
                print(f"Initial pixel color: RGB{color}")
                continue
            if color != initial_color:
                print(f"Progress bar color changed: {initial_color} -> {color}")
                print("Flashing likely complete.")
                break
            time.sleep(0.5)
    except Exception as e:
        print(f"Error monitoring progress bar: {e}")

def load_config(config_file='config.yaml', profile='default'):
    """加载配置文件"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 合并基础配置和文件配置
        result = {
            'qfil': config['qfil'],
            'files': config['files'][profile]
        }
        return result
    except Exception as e:
        print(f"Error loading config: {e}")
        sys.exit(1)

def parse_arguments():
    parser = argparse.ArgumentParser(description='QFIL Flashing Tool Controller')
    parser.add_argument('--config', 
                       default='config.yaml',
                       help='Path to config file')
    parser.add_argument('--profile',
                       default='default',
                       help='Configuration profile to use')
    parser.add_argument('--list-profiles',
                       action='store_true',
                       help='List available profiles in config file')
    return parser.parse_args()

def list_available_profiles(config_file):
    """列出配置文件中的所有配置集"""
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    print("\nAvailable profiles:")
    for profile in config['files'].keys():
        print(f"- {profile}")

# === Main Program ===

def main():
    args = parse_arguments()
    
    if args.list_profiles:
        list_available_profiles(args.config)
        return

    # 加载配置
    config = load_config(args.config, args.profile)
    
    # 验证文件是否存在
    for key, path in config['files'].items():
        if not os.path.exists(path):
            print(f"Error: {key} file not found: {path}")
            sys.exit(1)
    
    # 更新全局常量
    global QFIL_PATH, WINDOW_TITLE_KEYWORDS, NEW_WINDOW_POSITION, NEW_WINDOW_SIZE, PROGRESS_PIXEL, CLICK_POSITIONS, FILE_PATHS
    
    QFIL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), config['qfil']['path']))
    WINDOW_TITLE_KEYWORDS = tuple(config['qfil']['window']['title_keywords'])
    NEW_WINDOW_POSITION = tuple(config['qfil']['window']['position'])
    NEW_WINDOW_SIZE = tuple(config['qfil']['window']['size'])
    PROGRESS_PIXEL = tuple(config['qfil']['progress_pixel'])
    CLICK_POSITIONS = config['qfil']['click_positions']
    FILE_PATHS = config['files']

    # 启动主程序
    threading.Thread(target=monitor_new_windows, daemon=True).start()
    launch_qfil()
    qfil_win = wait_for_qfil_window()
    if qfil_win:
        print(f"QFIL window ready: {qfil_win.title}")
    configure_qfil()
    monitor_progress_bar()

if __name__ == "__main__":
    main()
