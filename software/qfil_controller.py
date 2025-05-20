import subprocess
import time
import pyautogui
import os
import cv2
import numpy as np
import sys
import pygetwindow as gw


def open_qfil(qfil_path):
    """
    Open the QFIL software using the provided path.
    :param qfil_path: The full path to the QFIL executable.
    """
    try:
        print(f"Opening QFIL software at: {qfil_path}")
        subprocess.Popen(qfil_path, shell=True)
    except FileNotFoundError:
        print(f"Error: QFIL executable not found at {qfil_path}")
    except Exception as e:
        print(f"An error occurred while trying to open QFIL: {str(e)}")


def locate_with_opencv(template_path, confidence=0.8):
    """
    Locate an image on the screen using OpenCV template matching.
    :param template_path: Path to the template image.
    :param confidence: Confidence threshold for matching (default is 0.8).
    :return: The center coordinates (x, y) of the matched region, or None if not found.
    """
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
    """
    Simulate mouse clicks on 'Configuration' and 'FireHose Configuration' buttons in QFIL,
    then ensure 'spinor' is selected in the dropdown and 'Reset After Download' is checked.
    """
    try:
        time.sleep(4)

        if hasattr(sys, '_MEIPASS'):
            base_dir = sys._MEIPASS
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))

        utils_dir = os.path.abspath(os.path.join(base_dir, "..", "utils"))

        config_button_path = os.path.join(utils_dir, "images", "configuration_button.png")
        firehose_button_path = os.path.join(utils_dir, "images", "firehose_button.png")
        dropdown_button_path = os.path.join(utils_dir, "images", "dropdown_button.png")
        reset_checkbox_checked_path = os.path.join(utils_dir, "images", "reset_checkbox_checked.png")
        reset_unchecked_path = os.path.join(utils_dir, "images", "reset_unchecked.png")
        reset_checkbox_hover_path = os.path.join(utils_dir, "images", "reset_checkbox_hover.png")
        ok_button_path = os.path.join(utils_dir, "images", "ok_button.png")
        flat_build_button_path = os.path.join(utils_dir, "images", "flat_build_button.png")
        browse_file_button_path = os.path.join(utils_dir, "images", "browse_file_button.png")
        load_xml_file_path = os.path.join(utils_dir, "images", "load_xml_file.png")

        config_button = locate_with_opencv(config_button_path, confidence=0.8)
        if config_button:
            pyautogui.click(config_button)
            print("Clicked on 'Configuration' button.")
        else:
            print("Could not find 'Configuration' button on the screen.")
            return

        firehose_button = locate_with_opencv(firehose_button_path, confidence=0.8)
        if firehose_button:
            pyautogui.click(firehose_button)
            print("Clicked on 'FireHose Configuration' button.")
        else:
            print("Could not find 'FireHose Configuration' button on the screen.")
            return

        time.sleep(1)

        dropdown_button = locate_with_opencv(dropdown_button_path, confidence=0.8)
        if dropdown_button:
            pyautogui.click(dropdown_button)
            print("Clicked on the dropdown button.")

            dropdown_x, dropdown_y = dropdown_button
            print(f"Dropdown button coordinates: ({dropdown_x}, {dropdown_y})")

            spinor_offset_x = 0
            spinor_offset_y = 100

            spinor_x = dropdown_x + spinor_offset_x
            spinor_y = dropdown_y + spinor_offset_y

            print(f"Calculated 'spinor' coordinates: ({spinor_x}, {spinor_y})")

            pyautogui.click(spinor_x, spinor_y)
            print(f"Clicked on 'spinor' option at coordinates ({spinor_x}, {spinor_y}).")
        else:
            print("Could not find the dropdown button on the screen.")

        reset_checkbox_states = [reset_unchecked_path, reset_checkbox_hover_path]
        reset_checkbox_checked = locate_with_opencv(reset_checkbox_checked_path, confidence=1)
        if reset_checkbox_checked:
            print("'Reset After Download' is already checked. No action needed.")
        else:
            for state in reset_checkbox_states:
                reset_checkbox = locate_with_opencv(state, confidence=0.9)
                if reset_checkbox:
                    checkbox_x, checkbox_y = reset_checkbox
                    pyautogui.click(checkbox_x, checkbox_y)
                    print(f"Checked 'Reset After Download' (state: {state}).")
                    break
            else:
                print("Could not find the 'Reset After Download' checkbox in any state.")
    except Exception as e:
        print(f"An error occurred while trying to operate QFIL: {str(e)}")

    ok_button = locate_with_opencv(ok_button_path, confidence=0.8)
    pyautogui.click(ok_button)
    print("Clicked on 'OK' button.")

    flat_build_button = locate_with_opencv(flat_build_button_path, confidence=0.8)
    pyautogui.click(flat_build_button)
    print("Clicked on 'Flat Build' button.")

    browse_file_button = locate_with_opencv(browse_file_button_path, confidence=0.8)
    pyautogui.click(browse_file_button)
    print("Clicked on 'Browse File' button.")

    time.sleep(1)

    file_path = os.path.join(base_dir, "..", "download", "downloads", "RELEASE_IMAGES", "RELEASE_IMAGES", "2025-04-28_21_25", "prog_firehose_ddr.elf")
    pyautogui.typewrite(file_path)
    print(f"Typed the file path: {file_path}")
    pyautogui.press('enter')
    print("Pressed Enter to confirm the file selection.")

    time.sleep(1)
    load_xml_file = locate_with_opencv(load_xml_file_path, confidence=1)
    pyautogui.click(load_xml_file)
    print("Clicked on 'Load XML File' button.")

    file_path = os.path.join(base_dir, "..", "download", "downloads", "RELEASE_IMAGES", "RELEASE_IMAGES", "2025-04-28_21_25", "sail_nor", "rawprogram0.xml")
    pyautogui.typewrite(file_path)
    print(f"Typed the file path: {file_path}")
    pyautogui.press('enter')
    print("Pressed Enter to confirm the file selection.")

    file_path = os.path.join(base_dir, "..", "download", "downloads", "RELEASE_IMAGES", "RELEASE_IMAGES", "2025-04-28_21_25", "sail_nor", "patch0.xml")
    pyautogui.typewrite(file_path)
    print(f"Typed the file path: {file_path}")
    pyautogui.press('enter')
    print("Pressed Enter to confirm the file selection.")

    time.sleep(1)
    print("QFIL configuration completed.")


def wait_for_qfil_window(window_title="QFIL", timeout=20):
    """
    Wait for QFIL window to appear and return the window object, return None if timeout.
    """
    for _ in range(timeout * 2):  # check every 0.5 seconds
        for w in gw.getAllWindows():
            print(f"Window title: {w.title}")  # Debugging output
            if window_title.lower() in w.title.lower():
                return w
        time.sleep(0.5)
    return None


if __name__ == "__main__":
    if hasattr(sys, '_MEIPASS'):
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

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

    qfil_window = wait_for_qfil_window("QFIL")
    if qfil_window:
        print(f"Found QFIL window: {qfil_window.title}, position=({qfil_window.left},{qfil_window.top}), size=({qfil_window.width},{qfil_window.height})")
    else:
        print("QFIL window not found")

    click_buttons_and_configure()
