import serial
import subprocess
import time
import os

FASTBOOT_TRIGGER_KEYWORD = "fastboot"
FASTBOOT_KEYWORDS = [
    "fastboot",
]
BAUD_RATE = 115200

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BAT_FILE = os.path.normpath(os.path.join(
    SCRIPT_DIR,
    "..",
    "utils",
    "RELEASE_IMAGES",
    "2025-04-28_21_25",
    "fastboot_nscdc_high_blank_flash.bat"
))

def find_lowest_available_com():
    for i in range(1, 256):
        port_name = f'COM{i}'
        try:
            with serial.Serial(port_name, BAUD_RATE, timeout=1) as ser:
                print(f"[INFO] Available COM port found: {port_name}")
                print("Please reset the device to continue...")
                return port_name
        except serial.SerialException as e:
            print(f"[DEBUG] Could not open {port_name}: {e}")
            continue
    print("[ERROR] No available COM port found after scanning COM1-COM255.")
    return None

def wait_for_fastboot_prompt(ser):
    ser.reset_input_buffer()
    ser.reset_output_buffer()

    total_timeout = 60
    start_time = time.time()
    buffer = ""
    last_boot_time = 0
    no_data_warning_issued = False  # 控制提示只出现一次

    print("[INFO] Waiting for device reboot...")

    BOOT_INDICATORS = [
        "QC_IMAGE_VERSION_STRING=",
        "IMAGE_VARIANT_STRING=",
        "OEM_IMAGE_VERSION_STRING=",
        "Boot Interface: UFS",
        "Successfully set the FDE"
    ]

    try:
        while (time.time() - start_time) < total_timeout:
            if ser.in_waiting:
                current_time = time.time()
                try:
                    chunk = ser.read(ser.in_waiting).decode('ascii', errors='ignore')
                except Exception as e:
                    print(f"[ERROR] Serial read decode failed: {e}")
                    chunk = ""

                if chunk:
                    print(f"[LOG] {chunk}", end='')
                    buffer += chunk
                    no_data_warning_issued = False  # 重置标志

                    if any(indicator in buffer for indicator in BOOT_INDICATORS):
                        if current_time - last_boot_time > 5:
                            trigger_indicator = next((ind for ind in BOOT_INDICATORS if ind in buffer), "")
                            print(f"\n[INFO] Trigger detected: {trigger_indicator}")
                            print("[INFO] Sending reset commands...")

                            try:
                                reset_cmd = "reset -f\r\n".encode('ascii')
                                ser.write(reset_cmd)
                                ser.flush()
                                print("[DEBUG] Reset command sent")
                            except Exception as e:
                                print(f"[ERROR] Failed to send reset command: {e}")

                            last_boot_time = current_time
                            buffer = ""

                    if "fastboot" in buffer.lower():
                        print("\n[SUCCESS] Fastboot mode detected")
                        time.sleep(2)
                        return True
            else:
                if not no_data_warning_issued and (time.time() - last_boot_time) > 15:
                    print("[WARN] Please set the device to normal mode and power cycle it.")
                    no_data_warning_issued = True

            time.sleep(0.01)
    except serial.SerialException as e:
        print(f"[ERROR] Serial communication error: {e}")

    print(f"[ERROR] Fastboot mode not detected within {total_timeout}s")
    return False

def check_fastboot_device():
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            result = subprocess.check_output(["fastboot", "devices"], stderr=subprocess.STDOUT, text=True)
        except FileNotFoundError:
            print("[ERROR] fastboot command not found. Please ensure fastboot is installed and in PATH.")
            return False
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] fastboot devices command failed: {e.output}")
            continue

        if "fastboot" not in result.lower():
            print(f"[WARN] Attempt {attempt + 1}/{max_attempts}: No fastboot device found.")
            time.sleep(5)
            continue

        try:
            result = subprocess.check_output(["fastboot", "getvar", "all"], stderr=subprocess.STDOUT, text=True, timeout=20)
            lower_result = result.lower()
            if "finished. total time" in lower_result or "all images flashed successfully" in lower_result:
                print("[SUCCESS] Flash process completed successfully.")
                return True
            else:
                print("[INFO] Fastboot device connected but flash process not confirmed finished yet.")
        except subprocess.TimeoutExpired:
            print("[ERROR] fastboot getvar command timed out.")
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] fastboot getvar failed: {e.output}")

        if attempt < max_attempts - 1:
            print("[INFO] Retrying in 10 seconds...")
            time.sleep(10)

    print("[ERROR] Flash verification failed after all attempts.")
    return False

def run_flash_script():
    if not os.path.isfile(BAT_FILE):
        print(f"[ERROR] Flash script not found: {BAT_FILE}")
        return False

    TOTAL_TIMEOUT = 30 * 60
    start_time = time.time()
    last_output_time = start_time

    try:
        process = subprocess.Popen(
            f'cmd.exe /c "{BAT_FILE}"',
            shell=True,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
            cwd=os.path.dirname(BAT_FILE)
        )
    except Exception as e:
        print(f"[ERROR] Failed to start flash script: {e}")
        return False

    try:
        while True:
            if (time.time() - start_time) > TOTAL_TIMEOUT:
                print("[ERROR] Flash script timeout, killing process...")
                process.kill()
                return False

            output_line = process.stdout.readline()
            if output_line:
                line = output_line.strip()
                last_output_time = time.time()

                if any(x in line for x in ['Sending', 'Writing', 'OKAY']):
                    print(f"\r[PROGRESS] {line:<100}", end='', flush=True)
                    if 'OKAY' in line:
                        print()
                elif "pause" in line.lower():
                    print("[INFO] Detected pause command, sending Enter key...")
                    time.sleep(1)
                    process.stdin.write('\n')
                    process.stdin.flush()
                else:
                    print(f"[BAT] {line}")

                if "failed" in line.lower() or "error" in line.lower():
                    print(f"[WARN] Flash script reported error: {line}")

            if process.poll() is not None:
                break

            if (time.time() - last_output_time) > 60:
                print("[WARN] No output from flash script for 60 seconds...")

            time.sleep(0.01)

    except Exception as e:
        print(f"\n[ERROR] Exception while running flash script: {e}")
        try:
            process.kill()
        except Exception:
            pass
        return False

    if process.returncode == 0:
        print("[SUCCESS] Flash script completed successfully")
        return True
    else:
        print(f"[ERROR] Flash script failed with return code: {process.returncode}")
        return False

def main():
    port = find_lowest_available_com()
    if not port:
        print("[RESULT] FAIL: No available COM port found.")
        return

    try:
        with serial.Serial(
            port=port,
            baudrate=BAUD_RATE,
            timeout=1,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            xonxoff=False,
            rtscts=False
        ) as ser:
            if not wait_for_fastboot_prompt(ser):
                print("[RESULT] FAIL: Fastboot log not detected.")
                return
            else:
                print("[RESULT] SUCCESS: Fastboot mode detected.")
    except serial.SerialException as e:
        print(f"[ERROR] Failed to open serial port {port}: {e}")
        print("[RESULT] FAIL: Serial port error.")
        return

    time.sleep(2)

    if not check_fastboot_device():
        print("[RESULT] FAIL: No fastboot device detected.")
        return
    else:
        print("[RESULT] SUCCESS: Fastboot device detected.")

    time.sleep(2)

    if run_flash_script():
        print("[RESULT] SUCCESS: Flash script executed successfully.")
    else:
        print("[RESULT] FAIL: Flash script execution failed.")
        retry_count = 3
        for i in range(retry_count):
            print(f"\n[INFO] Retrying flash process ({i+1}/{retry_count})...")
            if run_flash_script():
                print("[RESULT] SUCCESS: Flash script executed successfully on retry.")
                break
            time.sleep(5)
        else:
            print("[RESULT] FAIL: Flash script failed after all retries.")

if __name__ == "__main__":
    main()
