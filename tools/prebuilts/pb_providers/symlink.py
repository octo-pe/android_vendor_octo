from .base import ProviderBase
import re
import requests
import os
import logging
logger = logging.getLogger("Symlink provider")
class SymlinkProivder(ProviderBase):
    @staticmethod
    def download(package_data, destination):
        source_path = package_data["sl_path"]
        if os.path.exists(destination):
            if os.path.islink(destination) and os.readlink(destination) == source_path:
                logger.info("Symlink for %s matches, skipping", package_data["name"])
                return
            else:
                os.unlink(destination)
        os.symlink(source_path, destination)
