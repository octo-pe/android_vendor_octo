#!/usr/bin/env python3
import requests
import sys
import yaml
import logging
import os
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("prebuilts")
from . import pb_providers
MAKE_TEMPLATE = """
LOCAL_PATH := $(call my-dir)

include $(CLEAR_VARS)
LOCAL_MODULE := {name}
LOCAL_SRC_FILES := {name}.apk
LOCAL_CERTIFICATE := PRESIGNED
LOCAL_MODULE_TAGS := optional
LOCAL_MODULE_CLASS := APPS
LOCAL_DEX_PREOPT := false
LOCAL_MODULE_SUFFIX := $(COMMON_ANDROID_PACKAGE_SUFFIX)
LOCAL_OVERRIDES_PACKAGES := {overrides}
include $(BUILD_PREBUILT)
"""

def main(config_file):
    with open(config_file) as f:
        config = yaml.load(f, Loader=yaml.CLoader)
    target_path = "vendor/octo/prebuilt"
    applist = []
    for app in config:
        assert app["source"] in pb_providers.PROVIDERS
        os.makedirs(os.path.join(target_path, app["name"]), exist_ok=True)
        destination = os.path.join(target_path, app["name"], app["name"] + ".apk")
        logger.info("Getting %s (%s)", app["name"], destination)
        pb_providers.PROVIDERS[app["source"]].download(app, destination)
        with open(os.path.join(target_path, app["name"], "Android.mk"), 'w') as f:
            f.write(MAKE_TEMPLATE.format(name=app["name"], overrides=app.get("overrides", "")))
        applist.append(app["name"])
    sys.stdout.write(' '.join(applist))

if __name__ == "__main__":
    main(sys.argv[-1])
