import subprocess

qsahara_path = r'C:\Program Files (x86)\Qualcomm\QPST\bin\QSaharaServer.exe'
fh_loader_path = r'C:\Program Files (x86)\Qualcomm\QPST\bin\fh_loader.exe'

com_port = r'\\.\COM44'
firehose_path = r'C:\Users\CHP00015\Desktop\Image new one\RELEASE_IMAGES\2025-04-28_21_25\prog_firehose_ddr.elf'
search_path = r'C:\Users\CHP00015\Desktop\Image new one\RELEASE_IMAGES\2025-04-28_21_25\sail_nor'
rawprogram_path = 'rawprogram0.xml'

qsahara_cmd = [
    qsahara_path,
    '-p', com_port,
    '-s', f'13:{firehose_path}'  # **这里去掉了双引号**
]

fh_loader_cmd = [
    fh_loader_path,
    f'--port={com_port}',
    f'--sendxml={rawprogram_path}',
    f'--search_path={search_path}',
    '--noprompt',
    '--showpercentagecomplete',
    '--memoryname=spinor',
    '--zlpawarehost=1'
]

print("Running QSaharaServer...")
subprocess.run(qsahara_cmd, check=True)

print("Running fh_loader...")
subprocess.run(fh_loader_cmd, check=True)

print("Done.")
