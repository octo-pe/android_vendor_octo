#!/usr/bin/env python3
from . import pb_providers
from glob import glob
import sys
import yaml
import logging
import subprocess
import os
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("prebuilts")
MAKE_TEMPLATE = """
LOCAL_PATH := $(call my-dir)

include $(CLEAR_VARS)
LOCAL_MODULE := {name}
LOCAL_SRC_FILES := $(LOCAL_MODULE).apk
LOCAL_REPLACE_PREBUILT_APK_INSTALLED := $(LOCAL_PATH)/$(LOCAL_MODULE).apk
LOCAL_CERTIFICATE := PRESIGNED
LOCAL_MODULE_TAGS := optional
LOCAL_MODULE_CLASS := APPS
LOCAL_DEX_PREOPT := false
LOCAL_MODULE_SUFFIX := $(COMMON_ANDROID_PACKAGE_SUFFIX)
LOCAL_OVERRIDES_PACKAGES := {overrides}
LOCAL_USES_LIBRARIES := {required}
LOCAL_OPTIONAL_USES_LIBRARIES := {optional}
include $(BUILD_PREBUILT)
"""


def get_requirements(destination):
    requirements_txt = subprocess.check_output(
        ["aapt", "dump", "badging", destination]).decode()
    requirements_optional = []
    requirements = []
    for line in requirements_txt.split("\n"):
        if line.startswith("uses-library-not-required:"):
            requirements_optional.append(line.split(":")[1].strip("'"))
        elif line.startswith("uses-library:"):
            requirements.append(line.split(":")[1].strip("'"))
    return {"required": requirements, "optional": requirements_optional}


def main(config_file):
    if config_file == "local_apks":
        config = []
        for apk in glob("vendor/octo/local_apks/*.apk"):
            config.append({"name": apk.split(
                "/")[-1].split(".")[0], "source": "symlink", "sl_path": os.path.abspath(apk)})
    else:
        with open(config_file) as f:
            config = yaml.load(f, Loader=yaml.CLoader)
    target_path = "vendor/octo/prebuilt"
    applist = []
    for app in config:
        assert app["source"] in pb_providers.PROVIDERS
        os.makedirs(os.path.join(target_path, app["name"]), exist_ok=True)
        destination = os.path.join(
            target_path, app["name"], app["name"] + ".apk")
        logger.info("Getting %s (%s)", app["name"], destination)
        pb_providers.PROVIDERS[app["source"]].download(
            app, destination)
        requirements = get_requirements(destination)
        with open(os.path.join(target_path, app["name"], "Android.mk"), 'w') as f:
            f.write(MAKE_TEMPLATE.format(name=app["name"], overrides=app.get("overrides", ""), required=" ".join(
                requirements["required"]), optional=" ".join(requirements["optional"])))
        applist.append(app["name"])
    sys.stdout.write(' '.join(applist))


if __name__ == "__main__":
    main(sys.argv[-1])
