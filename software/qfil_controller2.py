import subprocess
import time
import pyautogui
import os
import cv2
import numpy as np
import sys
import pygetwindow as gw
import pyperclip
import threadingz

def open_qfil(qfil_path):
    try:
        print(f"Opening QFIL software at: {qfil_path}")
        subprocess.Popen(qfil_path, shell=True)
    except FileNotFoundError:
        print(f"Error: QFIL executable not found at {qfil_path}")
    except Exception as e:
        print(f"An error occurred while trying to open QFIL: {str(e)}")

def locate_with_opencv(template_path, confidence=0.8):
    screenshot = pyautogui.screenshot()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)

    template = cv2.imread(template_path, cv2.IMREAD_UNCHANGED)
    if template is None:
        print(f"Error: Could not load template image from {template_path}")
        return None

    if len(template.shape) == 3:
        template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    if max_val >= confidence:
        template_height, template_width = template.shape[:2]
        center_x = max_loc[0] + template_width // 2
        center_y = max_loc[1] + template_height // 2
        return center_x, center_y
    return None

def click_buttons_and_configure():
    try:
        time.sleep(3)

        # 使用绝对坐标点击
        positions = [(450, 300), (1450, 360), (1450, 600)]

        pyautogui.click(positions[0])
        print("Clicked on button 1 at (450, 300)")

        pyautogui.click(positions[1])
        print("Clicked on button 2 at (1450, 360)")

        time.sleep(1)
        if hasattr(sys, '_MEIPASS'):
            base_dir = sys._MEIPASS
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, "..", "download", "downloads", "RELEASE_IMAGES", "RELEASE_IMAGES", "2025-04-28_21_25", "prog_firehose_ddr.elf")
        pyperclip.copy(file_path)
        pyautogui.hotkey('ctrl', 'v')
        print(f"Pasted file path: {file_path}")
        pyautogui.press('enter')

        time.sleep(1)
        pyautogui.click(positions[2])
        print("Clicked on button 3 at (1450, 600)")

        time.sleep(1)
        file_path = os.path.join(base_dir, "..", "download", "downloads", "RELEASE_IMAGES", "RELEASE_IMAGES", "2025-04-28_21_25", "sail_nor", "rawprogram0.xml")
        pyperclip.copy(file_path)
        pyautogui.hotkey('ctrl', 'v')
        print(f"Pasted file path: {file_path}")
        pyautogui.press('enter')

        time.sleep(1)
        file_path = os.path.join(base_dir, "..", "download", "downloads", "RELEASE_IMAGES", "RELEASE_IMAGES", "2025-04-28_21_25", "sail_nor", "patch0.xml")
        pyperclip.copy(file_path)
        pyautogui.hotkey('ctrl', 'v')
        print(f"Pasted file path: {file_path}")
        pyautogui.press('enter')

        time.sleep(1)
        print("QFIL configuration completed.")

    except Exception as e:
        print(f"An error occurred in click_buttons_and_configure: {e}")

def wait_for_qfil_window(window_title_keywords=("Qualcomm", "Flash Image Loader"), timeout=20):
    min_width, min_height = 500, 300
    existing_ids = set(w._hWnd for w in gw.getAllWindows())
    for _ in range(timeout * 2):
        for w in gw.getAllWindows():
            if w._hWnd not in existing_ids:
                print(f"新窗口: {w.title}, 大小=({w.width},{w.height})")
                if (any(keyword.lower() in w.title.lower() for keyword in window_title_keywords)
                    and w.width > min_width and w.height > min_height):
                    return w
        time.sleep(0.5)
    return None

def monitor_new_windows(position=(380, 128), size=(1200, 898), poll_interval=0.5):
    print("后台窗口监控已启动...")
    known_windows = set(w._hWnd for w in gw.getAllWindows())
    while True:
        current_windows = gw.getAllWindows()
        for win in current_windows:
            if win._hWnd not in known_windows:
                try:
                    print(f"[监控] 新窗口: {win.title}")
                    win.moveTo(*position)
                    win.resizeTo(*size)
                    print(f"[监控] 已调整窗口位置到 {position}，大小为 {size}")
                except Exception as e:
                    print(f"[监控] 调整窗口失败: {e}")
                known_windows.add(win._hWnd)
        time.sleep(poll_interval)

if __name__ == "__main__":
    if hasattr(sys, '_MEIPASS'):
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    # 启动后台线程，监控新窗口
    threading.Thread(target=monitor_new_windows, daemon=True).start()

    qfil_path = os.path.join(
        base_dir,
        "qfil",
        "Qualcomm_Flash_Image_Loader_v2.0.3.5",
        "Qualcomm_Flash_Image_Loader_v2.0.3.5",
        "QFIL.exe"
    )
    print(f"QFIL Path: {qfil_path}")

    if os.path.exists(qfil_path):
        os.startfile(qfil_path)
    else:
        print(f"Error: QFIL.exe not found at {qfil_path}")

    qfil_window = wait_for_qfil_window(("QFIL",))
    if qfil_window:
        print(f"找到QFIL窗口: {qfil_window.title}, 位置=({qfil_window.left},{qfil_window.top}), 大小=({qfil_window.width},{qfil_window.height})")
    else:
        print("未找到QFIL窗口")

    click_buttons_and_configure()
