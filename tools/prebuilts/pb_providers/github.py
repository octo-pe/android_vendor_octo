from .base import DirectDownloadProvider
import re
import requests
class GithubReleaseProvider(DirectDownloadProvider):
    @staticmethod
    def download(package_data, destination):
        release_data = requests.get(f"https://api.github.com/repos/{package_data['repo']}/releases/latest").json()
        for asset in release_data["assets"]:
            if re.match(package_data["regex"], asset["name"]):
                package_data["url"] = asset["browser_download_url"]
                DirectDownloadProvider.download(package_data, destination)
                return
        raise ValueError(f"Can't find asset with name that matches {package_data['regex']}!")
