import requests
import urllib.request
import json
import platform
import zipfile
import os

import subprocess
from packaging import version

class ChromeDriverDownloader:
    def get_operative_system(self):
        # Detect the current operating system
        os_name = platform.system().lower()
        machine = platform.machine()

        platform_name = None
        if "linux" in os_name:
            platform_name = "linux64"
        elif "darwin" in os_name:
            platform_name = "mac-x64" if machine == "x86_64" else "mac-arm64"
        elif "win" in os_name:
            platform_name = "win64" if machine == "AMD64" else "win32"
        else:
            print("Sistema operativo no compatible.")
            return None

        return platform_name

    def get_chrome_version(self, platform_name):
        # Get the version of Chrome installed on the system
        chrome_version = None
        if "linux" in platform_name:
            chrome_executable_path = "/usr/bin/google-chrome-stable"
            chrome_version = subprocess.check_output([chrome_executable_path, "--version"]).decode("utf-8")
        elif "darwin" in platform_name:
            chrome_version = subprocess.check_output(["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "--version"]).decode("utf-8")
        elif "win" in platform_name:
            chrome_version = subprocess.check_output(["reg", "query", "HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon", "/v", "version"]).decode("utf-8")

        return chrome_version.split(" ")[-1]

    def get_chromedriver_version_url(self, data, installed_chrome_version, platform_name):
        installed_version = version.parse(installed_chrome_version)

        # Filter available versions and find the closest one
        available_versions = list(data["milestones"].keys())
        closest_version = min(available_versions, key=lambda x: abs(int(x.split('.')[0]) - int(installed_version.base_version.split('.')[0])))
        
        if closest_version in data["milestones"]:
            downloads = data["milestones"][closest_version]["downloads"]["chromedriver"]
            for driver in downloads:
                if driver["platform"] == platform_name:
                    return driver["url"]
        
        return None

    def download_and_extract_chromedriver(self, download_url, target_folder):
        if download_url:
            # ChromeDriver file name
            file_name = os.path.basename(download_url)

            # Download the ChromeDriver file
            urllib.request.urlretrieve(download_url, file_name)

            # Unzip the file in the 'driver' folder
            with zipfile.ZipFile(file_name, "r") as zip_ref:
                zip_ref.extractall(target_folder)

            os.remove(file_name)  # Delete the ZIP file

            print(f"ChromeDriver downloaded and unzipped to the folder '{target_folder}'")
        else:
            print("A ChromeDriver for the current platform was not found.")

if __name__ == "__main__":
    downloader = ChromeDriverDownloader()

    # API URL
    api_url = "https://googlechromelabs.github.io/chrome-for-testing/latest-versions-per-milestone-with-downloads.json"

    # Make a GET request to the API
    response = requests.get(api_url)

    if response.status_code == 200:
        # Parse the JSON response
        data = json.loads(response.text)

        system_operative = downloader.get_operative_system()
        print(f"OS: {system_operative}")

        # Get the version of Chrome installed on the system
        installed_chrome_version = downloader.get_chrome_version(system_operative)
        print(f"Installed Chrome version: {installed_chrome_version}")

        download_url = downloader.get_chromedriver_version_url(data, installed_chrome_version, system_operative)
        target_folder = "driver"

        downloader.download_and_extract_chromedriver(download_url, target_folder)
    else:
        print("Could not connect to API")


