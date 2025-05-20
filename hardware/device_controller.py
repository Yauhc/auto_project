try:
    import serial.tools.list_ports
except ImportError:
    print("Error: The 'pyserial' package is not installed.")
    print("Please install it using: pip install pyserial")
    exit(1)

def find_qualcomm_device():
    """
    Detect if a Qualcomm device is connected via USB.
    :return: A tuple (port, is_edl_mode), where port is the device port (e.g., COM3) and is_edl_mode is True if the device is in EDL mode.
    """
    try:
        # Qualcomm USB Vendor ID and common Product IDs for EDL mode
        QUALCOMM_VENDOR_ID = "05C6"  # Qualcomm's USB Vendor ID
        EDL_PRODUCT_IDS = ["9008"]  # Common Product ID for EDL mode

        # List all connected devices
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if QUALCOMM_VENDOR_ID in port.hwid:
                # Check if the device is in EDL mode
                for edl_id in EDL_PRODUCT_IDS:
                    if edl_id in port.hwid:
                        return port.device, True  # Device is in EDL mode
                return port.device, False  # Device is connected but not in EDL mode

        return None, False  # No Qualcomm device found
    except Exception as e:
        print(f"Error detecting device: {str(e)}")
        return None, False

if __name__ == "__main__":
    port, is_edl_mode = find_qualcomm_device()
    if port:
        if is_edl_mode:
            print(f"Qualcomm device detected on {port} in EDL mode.")
        else:
            print(f"Qualcomm device detected on {port}, but not in EDL mode.")
    else:
        print("No Qualcomm device detected.")

