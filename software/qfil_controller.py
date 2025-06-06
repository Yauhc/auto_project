import subprocess
import os
import serial.tools.list_ports
import time

def run_qfil_controller(images_path):
    # Correct the path to avoid nested duplicates
    images_path = os.path.abspath(images_path)
    print(f"[INFO] Using images_path: {images_path}")

    # Find QSaharaServer.exe and fh_loader.exe
    base_dir = os.path.dirname(os.path.abspath(__file__))
    qsahara_path = os.path.join(base_dir, '..', 'utils', 'QPST', 'bin', 'QSaharaServer.exe')
    fh_loader_path = os.path.join(base_dir, '..', 'utils', 'QPST', 'bin', 'fh_loader.exe')

    if not os.path.exists(qsahara_path) or not os.path.exists(fh_loader_path):
        print("[ERROR] QSaharaServer.exe or fh_loader.exe not found.")
        return False

    # Find firehose
    firehose_path = find_file(images_path, 'prog_firehose_ddr.elf')
    if not firehose_path:
        print("[ERROR] prog_firehose_ddr.elf not found in images_path.")
        return False

    # Find sail_nor folder
    sail_nor = find_directory(images_path, 'sail_nor')
    if not sail_nor:
        print("[ERROR] sail_nor directory not found in images_path.")
        return False

    # Find rawprogram0.xml
    rawprogram_path = find_file(sail_nor, 'rawprogram0.xml')
    if not rawprogram_path:
        print("[ERROR] rawprogram0.xml not found in sail_nor directory.")
        return False

    # Find Qualcomm 9008 port
    qsahara_port = None
    for port in serial.tools.list_ports.comports():
        if "9008" in port.description:
            qsahara_port = port.device
            break

    if not qsahara_port:
        print("[ERROR] Qualcomm 9008 port not detected.")
        return False

    com_port = rf'\\.\{qsahara_port}'

    # Build QSaharaServer command
    qsahara_cmd = [
        qsahara_path,
        '-p', com_port,
        '-s', f'13:{firehose_path}'
    ]

    # Build fh_loader command
    fh_loader_cmd = [
        fh_loader_path,
        f'--port={com_port}',
        f'--sendxml={rawprogram_path}',
        f'--search_path={sail_nor}',
        '--noprompt',
        '--showpercentagecomplete',
        '--memoryname=spinor',
        '--zlpawarehost=1'
    ]

    # Attempt flashing loop
    while True:
        print("\n[INFO] Running QSaharaServer...")
        ret, out = _run_subprocess(qsahara_cmd)
        if ret != 0:
            if not _prompt_retry("QSaharaServer execution failed"):
                return False
            continue

        print("\n[INFO] Running fh_loader...")
        ret, out = _run_subprocess(fh_loader_cmd)
        print(f"\nfh_loader return code: {ret}")
        print("fh_loader output (last 300 characters):")
        print(out[-300:])

        success_keywords = ["All Finished Successfully", "Success", "Finished"]
        if ret != 0 and not any(k in out for k in success_keywords):
            if not _prompt_retry("fh_loader execution failed"):
                return False
            continue

        print("[INFO] Flashing completed.")
        return True

def find_file(start_dir, target_filename):
    for root, _, files in os.walk(start_dir):
        if target_filename in files:
            return os.path.join(root, target_filename)
    return None

def find_directory(start_dir, target_dirname):
    for root, dirs, _ in os.walk(start_dir):
        if target_dirname in dirs:
            return os.path.join(root, target_dirname)
    return None

def _run_subprocess(cmd):
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    output = []
    while True:
        line = process.stdout.readline()
        if not line and process.poll() is not None:
            break
        if line:
            print(line, end='')
            output.append(line)
    retcode = process.wait()
    return retcode, ''.join(output)

def _prompt_retry(message):
    print(f"\n[ERROR] {message}")
    print("Retrying in 5 seconds automatically, or press Ctrl+C to abort...")
    try:
        time.sleep(5)
        return True
    except KeyboardInterrupt:
        print("\n[INFO] User aborted.")
        return False

if __name__ == "__main__":
    # Example path, can be passed externally
    base_dir = os.path.dirname(os.path.abspath(__file__))
    images_path = os.path.join(base_dir, '..', 'utils', 'extracted')
    success = run_qfil_controller(images_path)
    if not success:
        print("QFIL flashing aborted.")
        exit(1)
