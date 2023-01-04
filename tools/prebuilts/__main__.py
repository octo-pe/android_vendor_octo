#!/usr/bin/env python3
from . import pb_providers
from glob import glob
import sys
import yaml
import logging
import subprocess
import os
import zipfile
from pathlib import Path
import gzip
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("prebuilts")
MAKE_TEMPLATE = """
LOCAL_PATH := $(call my-dir)

include $(CLEAR_VARS)
LOCAL_MODULE := {name}
LOCAL_SRC_FILES := {name}.apk
LOCAL_CERTIFICATE := PRESIGNED
LOCAL_PRODUCT_MODULE := true
LOCAL_MODULE_TAGS := optional
LOCAL_MODULE_CLASS := APPS
LOCAL_DEX_PREOPT := false
LOCAL_MODULE_SUFFIX := $(COMMON_ANDROID_PACKAGE_SUFFIX)
LOCAL_OVERRIDES_PACKAGES := {overrides}
LOCAL_USES_LIBRARIES := {required}
LOCAL_OPTIONAL_USES_LIBRARIES := {optional}
LOCAL_REPLACE_PREBUILT_APK_INSTALLED := $(LOCAL_PATH)/{name}.apk
{extras}
include $(BUILD_PREBUILT)
"""
COMPRESSED = """
include $(CLEAR_VARS)
LOCAL_MODULE := Fenix
LOCAL_MODULE_TAGS := optional
LOCAL_SRC_FILES := $(LOCAL_MODULE).apk.gz
LOCAL_MODULE_CLASS := ETC
LOCAL_MODULE_PATH := $(TARGET_OUT_PRODUCT)/app/$(LOCAL_MODULE)/
LOCAL_MODULE_SUFFIX := .apk.gz
LOCAL_DEX_PREOPT := false
LOCAL_USES_LIBRARIES := {required}
LOCAL_OPTIONAL_USES_LIBRARIES := {optional}
include $(BUILD_PREBUILT)

"""
PRIVELEGED = "\nLOCAL_PRIVILEGED_MODULE := true"


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


base_app = {
    "source": None,
    "priveleged": False,
    "compressed": False
}


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
    for app_cf in config:
        app = dict(**base_app)
        template = MAKE_TEMPLATE
        app.update(app_cf)
        assert app["source"] in pb_providers.PROVIDERS
        os.makedirs(os.path.join(target_path, app["name"]), exist_ok=True)
        destination = os.path.join(
            target_path, app["name"], app["name"] + ".apk")
        logger.info("Getting %s (%s)", app["name"], destination)
        pb_providers.PROVIDERS[app["source"]].download(
            app, destination)
        requirements = get_requirements(destination)
        mkpath = os.path.join(target_path, app["name"], "Android.mk")
        current_mk = ""
        if os.path.exists(mkpath):
            with open(mkpath) as f:
                current_mk = f.read()

        applist.append(app["name"])
        result = ""
        extras = ""
        if app["compressed"]:
            with gzip.open(destination + ".gz", 'wb') as gzf:
                with open(destination, "rb") as f:
                    gzf.write(f.read())
            template = MAKE_TEMPLATE.replace(
                "LOCAL_MODULE := {name}", "LOCAL_MODULE := {name}-Stub") + COMPRESSED
            applist.append(f"{app['name']}-Stub")
        if app["priveleged"]:
            extras += PRIVELEGED
        result = template.format(name=app["name"], extras=extras, overrides=app.get("overrides", ""), required=" ".join(
            requirements["required"]), optional=" ".join(requirements["optional"]))
        if result != current_mk:
            with open(mkpath, 'w', newline="") as f:
                logger.info("Writing new makefile for %s", app["name"])
                f.write(result)
        else:
            logger.info("Makefile for %s is already up to date", app["name"])
    sys.stdout.write(' '.join(applist))


if __name__ == "__main__":
    main(sys.argv[-1])
