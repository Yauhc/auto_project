import os
import requests
import subprocess
import configparser

class JFrogManager:
    def __init__(self, config_rel_path='../config.ini'):
        # Get current script directory
        self.script_dir = os.path.dirname(os.path.abspath(__file__))

        # Path to save jf.exe
        self.jf_exe_path = os.path.abspath(os.path.join(self.script_dir, '../utils/jf.exe'))

        # Load config.ini (located at project root)
        config_path = os.path.abspath(os.path.join(self.script_dir, config_rel_path))
        self.config = configparser.ConfigParser()
        self.config.read(config_path)

        # Read download URL from config file
        try:
            self.artifactory_jfrog_cli_download_url = self.config.get('artifactory', 'jfrog_cli_download_url')
        except (configparser.NoSectionError, configparser.NoOptionError):
            raise RuntimeError("Missing 'artifactory' section or 'jfrog_cli_download_url' option in config.ini, please check.")

        self.proxies = {}  # Set proxies here if needed

    def download_jfrog_cli(self):
        if os.path.exists(self.jf_exe_path):
            print(f"{self.jf_exe_path} already exists,succeeded.")
            return

        try:
            os.makedirs(os.path.dirname(self.jf_exe_path), exist_ok=True)
            print("Starting to download JFrog CLI...")

            with requests.get(self.artifactory_jfrog_cli_download_url, stream=True, proxies=self.proxies) as response:
                response.raise_for_status()
                with open(self.jf_exe_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

            print(f"JFrog CLI downloaded to: {self.jf_exe_path}")
        except Exception as e:
            print(f"Download failed: {e}")

    def configure_jfrog_cli(self):
        try:
            server_id = 'nissan-artifactory'
            artifactory_url = 'https://spaws.jp.nissan.biz/'
            username = self.config.get('artifactory', 'username')
            token = self.config.get('artifactory', 'token')

            command = [
                self.jf_exe_path,
                'config', 'add', server_id,
                '--url', artifactory_url,
                '--user', username,
                '--password', token,
                '--interactive=false'
            ]

            print("Authorizing access...")
            result = subprocess.run(command, capture_output=True, text=True)

            if result.returncode == 0:
                print("JFrog CLI configured successfully.")
            else:
                if "already exists" in result.stderr:
                    print("Server ID already exists,succeeded.")
                else:
                    print(f"Error configuring JFrog CLI, return code {result.returncode}")
                    print("STDERR:", result.stderr)

        except Exception as e:
            print(f"Exception during configuration: {e}")

    def ensure_jfrog_ready(self):
        self.download_jfrog_cli()
        self.configure_jfrog_cli()

if __name__ == "__main__":
    manager = JFrogManager()
    manager.ensure_jfrog_ready()
