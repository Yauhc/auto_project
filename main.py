import sys
import os
import subprocess

sys.path.append(os.path.join(os.path.dirname(__file__), 'hardware'))
from device_controller import find_qualcomm_device

def main():
    print("=== 设备连接提示 ===")
    print("请将设备连接至电脑，并设置为 DLOAD 模式（可通过拨动 DLOAD 开关）")
    print("按回车开始检测设备，或输入 exit 退出程序。")

    while True:
        user_input = input(">> ")
        if user_input.strip().lower() == "exit":
            print("程序已退出。")
            break

        port, is_edl_mode = find_qualcomm_device()
        if port:
            if is_edl_mode:
                print(f"✅ 检测到 Qualcomm 设备（端口: {port}），当前为 DLOAD 模式。")
                run_qfil_then_tera()
                break
            else:
                print(f"⚠️ 检测到 Qualcomm 设备（端口: {port}），但不是 DLOAD 模式。请检查开关，或重新插拔设备。")
        else:
            print("❌ 未检测到 Qualcomm 设备，请检查连接。")

        print("按回车重新检测，或输入 exit 退出。")

def run_qfil_then_tera():
    base_dir = os.path.join(os.path.dirname(__file__), 'software')
    python_executable = sys.executable

    qfil_script = os.path.join(base_dir, 'qfil_controller.py')
    tera_script = os.path.join(base_dir, 'tera_term_controller.py')

    try:
        print("⚙️ 开始执行 QFIL 刷写脚本...")
        subprocess.run([python_executable, qfil_script], check=True)
        print("QFIL 刷写完成！")

        print("⚙️ 开始执行 Tera Term 控制脚本...")
        subprocess.run([python_executable, tera_script], check=True)
        print("Tera Term 脚本执行完成！")

    except subprocess.CalledProcessError as e:
        print(f"\n❌ 脚本执行失败，错误码：{e.returncode}")
        print("请检查对应脚本及参数配置是否正确。")

if __name__ == "__main__":
    main()
