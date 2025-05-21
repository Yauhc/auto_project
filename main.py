import sys
import os
import subprocess

# 添加 hardware 模块路径
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
                # 调用 qfil_controller.py
                run_qfil_script()
                break
            else:
                print(f"⚠️ 检测到 Qualcomm 设备（端口: {port}），但不是 DLOAD 模式。请检查开关，或重新插拔设备。")
        else:
            print("❌ 未检测到 Qualcomm 设备，请检查连接。")

        print("按回车重新检测，或输入 exit 退出。")

def run_qfil_script():
    # 相对路径调用 software/qfil_controller.py
    script_path = os.path.join(os.path.dirname(__file__), 'software', 'qfil_controller.py')
    python_executable = sys.executable  # 当前 Python 环境路径
    try:
        print("⚙️ 开始执行 QFIL 刷写脚本...\n")
        subprocess.run([python_executable, script_path], check=True)
        print("\n🎉 刷写完成！")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 刷写失败，错误码：{e.returncode}")
        print("请检查 qfil_controller.py 中的参数配置是否正确。")

if __name__ == "__main__":
    main()
