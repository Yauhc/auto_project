import serial
import subprocess
import time
import os
import sys

BAUD_RATE = 115200
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def find_lowest_available_com():
    """Find the lowest available COM port, return port name or None"""
    for i in range(1, 256):
        port_name = f'COM{i}'
        try:
            with serial.Serial(port_name, BAUD_RATE, timeout=1):
                print(f"[INFO] Available COM port found: {port_name}")
                print("Please set the debug version to normal mode and restart the power...")
                return port_name
        except serial.SerialException:
            continue
    print("[ERROR] No available COM port found.")
    return None


def wait_for_fastboot_prompt(ser):
    """Listen to fastboot prompt via serial, send reset command, check if fastboot mode is entered"""
    ser.reset_input_buffer()
    ser.reset_output_buffer()

    total_timeout = 60
    start_time = time.time()
    buffer = ""
    last_reset_time = 0
    RESET_INTERVAL = 10  # Send reset command every 10 seconds

    BOOT_INDICATORS = [
        "QC_IMAGE_VERSION_STRING=",
        "IMAGE_VARIANT_STRING=",
        "OEM_IMAGE_VERSION_STRING=",
        "Boot Interface: UFS",
        "Successfully set the FDE",
        "launch io-sock for NS CDC platform."
    ]

    try:
        while (time.time() - start_time) < total_timeout:
            current_time = time.time()
            
            # Periodically send reset command
            if current_time - last_reset_time >= RESET_INTERVAL:
                try:
                    ser.write(b"reset -f\r\n")
                    ser.flush()
                    print(f"\n[CMD] Sent reset command at {time.strftime('%H:%M:%S')}")
                    last_reset_time = current_time
                    buffer = ""
                except Exception as e:
                    print(f"[ERROR] Failed to send reset command: {e}")

            if ser.in_waiting:
                chunk = ser.read(ser.in_waiting).decode('ascii', errors='ignore')
                if chunk:
                    print(f"[LOG] {chunk}", end='')
                    buffer += chunk

                    # After detecting boot indicators, possibly send reset command again
                    if any(indicator in buffer for indicator in BOOT_INDICATORS):
                        if current_time - last_reset_time > 5:
                            try:
                                ser.write(b"reset -f\r\n")
                                ser.flush()
                                print(f"\n[CMD] Sent reset command (boot indicator detected) at {time.strftime('%H:%M:%S')}")
                                last_reset_time = current_time
                                buffer = ""
                            except Exception as e:
                                print(f"[ERROR] Failed to send reset command: {e}")

                    # Detect fastboot keyword, return success
                    if "fastboot" in buffer.lower():
                        print("\n[SUCCESS] Fastboot mode detected")
                        time.sleep(2)
                        return True

            time.sleep(0.01)

    except serial.SerialException as e:
        print(f"[ERROR] Serial communication error: {e}")

    print("[ERROR] Fastboot mode not detected within timeout.")
    return False


def trigger_fastboot():
    """Find COM port and try to enter fastboot mode"""
    port = find_lowest_available_com()
    if not port:
        return False

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
            return wait_for_fastboot_prompt(ser)
    except serial.SerialException as e:
        print(f"[ERROR] Failed to open serial port: {e}")
        return False


def check_fastboot_device():
    """Call fastboot command to check if device is online"""
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            result = subprocess.check_output(["fastboot", "devices"], stderr=subprocess.STDOUT, text=True)
            if "fastboot" not in result.lower():
                time.sleep(5)
                continue

            result = subprocess.check_output(["fastboot", "getvar", "all"], stderr=subprocess.STDOUT, text=True, timeout=20)
            if "finished. total time" in result.lower() or "all images flashed successfully" in result.lower():
                return True
        except Exception:
            time.sleep(5)
    return False


def get_bat_file_path(abs_images_path):
    """Search for the absolute path of a valid fastboot flash script"""
    target_files = [
        "fastboot_nscdc_high_blank_flash.bat",
        "fastboot_nscdc_std_blank_flash.bat"
    ]

    if not os.path.exists(abs_images_path):
        print(f"[ERROR] Given path does not exist: {abs_images_path}")
        return None

    for root, _, files in os.walk(abs_images_path):
        for target_file in target_files:
            if target_file in files:
                bat_file = os.path.join(root, target_file)
                print(f"[INFO] Found flash script: {bat_file}")
                return bat_file

    print("[ERROR] Flash script not found.")
    return None

def run_flash_script(abs_images_path):
    """Execute the flash bat script and print progress in real-time"""
    bat_file = get_bat_file_path(abs_images_path)
    if not bat_file:
        return False

    try:
        process = subprocess.Popen(
            f'cmd.exe /c "{bat_file}"',
            shell=True,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            cwd=os.path.dirname(bat_file)
        )
    except Exception as e:
        print(f"[ERROR] Failed to start flash script: {e}")
        return False

    try:
        while True:
            output_line = process.stdout.readline()
            if output_line:
                line = output_line.strip()
                if any(x in line for x in ['Sending', 'Writing', 'OKAY']):
                    print(f"[PROGRESS] {line:<100}", end='', flush=True)
                    if 'OKAY' in line:
                        print()
                elif "pause" in line.lower():
                    time.sleep(1)
                    process.stdin.write('\n')
                    process.stdin.flush()
                else:
                    print(f"[BAT] {line}")

                if "failed" in line.lower() or "error" in line.lower():
                    print(f"[WARN] Flash script reported error: {line}")
            if process.poll() is not None:
                break
            time.sleep(0.01)
    except Exception as e:
        print(f"[ERROR] Error during flash script execution: {e}")
        try:
            process.kill()
        except Exception:
            pass
        return False

    return process.returncode == 0


def run_fastboot_flash(abs_images_path):
    """
    Integration process:
    1. Trigger entering fastboot mode
    2. Verify fastboot device
    3. Run flash script
    """
    if trigger_fastboot():
        print("[INFO] Fastboot mode triggered.")
        time.sleep(5)
        if check_fastboot_device():
            print("[INFO] Fastboot device verified.")
            if run_flash_script(abs_images_path):
                print("[SUCCESS] Flash script completed.")
                return True
            else:
                print("[FAILURE] Flash script execution failed.")
                return False
        else:
            print("[FAILURE] No fastboot device detected.")
            return False
    else:
        print("[FAILURE] Failed to enter fastboot mode.")
        return False


if __name__ == "__main__":
    abs_images_path = os.path.join(SCRIPT_DIR, "..", "utils")
    success = run_fastboot_flash(abs_images_path)
    sys.exit(0 if success else 1)
