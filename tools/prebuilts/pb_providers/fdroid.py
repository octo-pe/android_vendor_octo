from .base import DirectDownloadProvider, fancy_dl
import logging
from apkverify import ApkSignature
import zipfile
import json
logger = logging.getLogger("F-Droid provider")
class FDroidProvider(DirectDownloadProvider):
    def __init__(self):
        logger.info("Downloading F-Droid repo data...")
        repo_fd = fancy_dl("https://f-droid.org/repo/index-v1.jar", "F-Droid index")
        logger.info("Verifying F-Droid repo...")
        assert ApkSignature(fd=repo_fd).verify()
        logger.info("Verified!")
        repo_fd.seek(0)
        self.package_index = json.load(zipfile.ZipFile(repo_fd).open("index-v1.json"))["packages"]
        logger.info("Downloaded info about %s apps", len(self.package_index))

    def download(self, package_data, destination):
        assert package_data["packageName"] in self.package_index
        package = self.package_index[package_data["packageName"]]
        package_data["url"] = f"http://f-droid.org/repo/{package[0]['apkName']}"
        package_data["sha256"] = package[0]['hash']
        return super().download(package_data, destination)
