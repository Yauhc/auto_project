# Firmware Flashing Tool
This is a Python-based automation tool for flashing Qualcomm and Renesas chipset devices (such as Meter and IVI). It supports the complete workflow including downloading the latest firmware, path configuration, device detection, and flashing operations.

# Implementation Overview
The core idea of this project is to automate the firmware flashing process through a modular design, minimizing user operations. Main features include: configuration management, flexible firmware acquisition methods, device detection, flashing workflow execution, using the QFIL tool to flash the main firmware, setting device boot mode via serial communication, flashing MCU (Meter/IVI) firmware, retry mechanism for each failed step, and log output.

# User Guide
## 1.Install Python
Make sure Python 3.10.9 is installed on your system. You can download it from the official Python website:
https://www.python.org/downloads/release/python-3109/

## 2.Install Dependencies
Open a terminal and install the required Python libraries:
```bash
pip install -r requirements.txt
```

## 3.Configure Settings
Edit the config.ini file in the root directory and fill in your Artifactory credentials:
```ini
[artifactory]

user = your_artifactory_username

access_token = your_artifactory_token

jfrog_cli_download_url = your_jfrog_cli_download_url

[images]

image_save_path = your_image_save_path

[proxies]

use_proxy = true of false

http = your_proxies

https = your_proxies
```

## 4.Prepare QPST Tool
Go to the following website:

https://qpsttool.com/qpst-tool-v2-7-496#google_vignette

Download the QPST tool from the page.After downloading, extract the archive.

Run QPST.2.7.496.1.exe to install the tool. It will be installed by default to:C:\Program Files (x86)\Qualcomm

After installation, go to the folder above and copy the QPST folder into the utils folder inside your project directory.


## 5.Prepare Renesas Flash Programmer
Go to the following website:

https://www.renesas.com/ja/software-tool/renesas-flash-programmer-programming-gui#downloads

Find the section titled:ソフトウェア／ツール－評価版ソフトウェア Renesas Flash Programmer V3.19.00 Windows

Download the installer and extract it.

Run Renesas_Flash_Programmer_Package_V31900.exe to install the tool.

After installation, locate the folder named Renesas Flash Programmer V3.19 and copy it into the utils folder inside your project directory.

## 6. Start the Script
Once everything is ready, run the main program with desired start point:
```bash
# Start from the beginning
python main.py

# Start from Fastboot step
python main.py --start-from fastboot

# Start from MCU flashing only
python main.py --start-from mcu
```

# Notes
Follow prompts to ensure the device is in the correct mode.

The MCU boards must be properly connected and powered on (important).

When using the auto-download feature:

Make sure you have edited the contents in the Artifactory section.

All extracted files will be saved to [images]image_save_path.

In some cases, image files may be downloaded as empty files due to proxy or connectivity issues. If such a case occurs, please delete the affected file manually, verify your proxy or network configuration, and re-initiate the download.

If any control script fails, the console will display [RESULT] FAIL, and a retry prompt will be shown.
