import subprocess

# Define command and parameters
command = [
    r".\utils\Renesas Flash Programmer V3.16\rfp-cli.exe",
    "-d", "RH850",
    "-tool", "E2",
    "-p",
    "-v",
    "-e",
    "-osc", "8.0",
    "-file", r".\utils\MCU\NCDCMETER_RELEASE_IMAGES\lge\mcu\NCDC_METER\Appl\RELEASE_IMAGES\NCDCMETER_PI26_01_01_20250428_192246\NCDCMETER_PI26_01_01.s19",
    "-reset"
]

# Use Popen to output in real time
with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True) as proc:
    for line in proc.stdout:
        print(line, end='')  # Print each line of output in real time
