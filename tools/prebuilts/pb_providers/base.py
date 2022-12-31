import requests
import hashlib
import logging
import os
from tqdm import tqdm
from io import BytesIO
from pathlib import Path
import subprocess
import sys


def fancy_dl(url, desc):
    resp = requests.get(url, stream=True)
    total = int(resp.headers.get('content-length', 0))
    io = BytesIO()
    with tqdm(
            desc=desc,
            total=total,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
    ) as bar:
        for data in resp.iter_content(chunk_size=1024):
            size = io.write(data)
            bar.update(size)
    io.seek(0)
    return io


class ProviderBase():
    def download(self, package_data, destination):
        raise RuntimeError("download not overridden!")


logger = logging.getLogger("DirectDownloadProvider")


class DirectDownloadProvider(ProviderBase):
    @staticmethod
    def download(package_data, destination):
        downloaded = False
        if os.path.exists(destination):
            logger.info("%s already exists, checking if its valid...",
                        package_data["name"])
            if package_data.get("sha256", False):
                with open(destination, 'rb') as f:
                    local_hash = hashlib.sha256(f.read()).hexdigest()
                    if local_hash == package_data["sha256"]:
                        logger.info(
                            "Already have %s downloaded and hashes match - skipping...", package_data["name"])
                        downloaded = True
                    else:
                        logger.info(
                            "Local %s is invalid/outdated (sha256 doesn't match) - redownloading", package_data["name"])
            else:
                signed = subprocess.call(
                    ["apksigner", "verify", destination], stdout=sys.stderr) == 0
                if signed:
                    downloaded = True
                    logger.info(
                        "%s doesn't have sha256 set and signatures match - skipping. You might wanna set sha256.", package_data["name"])
                else:
                    logger.warning("Signature verification error: %s", signed)
        else:
            logger.info("%s is not present - downloading...",
                        package_data["name"])

        if not downloaded:
            data = fancy_dl(package_data["url"], Path(destination).stem).read()
            if package_data.get("sha256", None) is not None:
                logger.info("Verifying hash for %s", package_data["url"])
                assert hashlib.sha256(
                    data).hexdigest() == package_data["sha256"]
                logger.info("All good!")
            else:
                logger.warning(
                    "Hash for %s is not supplied, can't check :(", package_data["url"])
            with open(destination, 'wb') as f:
                f.write(data)
