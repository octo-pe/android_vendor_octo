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
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("prebuilts")
MAKE_TEMPLATE = """
LOCAL_PATH := $(call my-dir)

include $(CLEAR_VARS)
LOCAL_MODULE := {name}
LOCAL_SRC_FILES := $(LOCAL_MODULE).apk
LOCAL_CERTIFICATE := PRESIGNED
LOCAL_MODULE_TAGS := optional
LOCAL_MODULE_CLASS := APPS
LOCAL_DEX_PREOPT := false
LOCAL_MODULE_SUFFIX := $(COMMON_ANDROID_PACKAGE_SUFFIX)
LOCAL_OVERRIDES_PACKAGES := {overrides}
LOCAL_USES_LIBRARIES := {required}
LOCAL_OPTIONAL_USES_LIBRARIES := {optional}
{extras}
include $(BUILD_PREBUILT)
"""
LIB_TEMPALTE = """
include $(CLEAR_VARS)
LOCAL_MODULE := {libname}
LOCAL_MODULE_CLASS := SHARED_LIBRARIES
LOCAL_MODULE_PATH := $(TARGET_OUT)/app/{name}/lib/arm64/
LOCAL_SRC_FILES := libs/{libname}
OVERRIDE_BUILT_MODULE_PATH := $(TARGET_OUT_INTERMEDIATE_LIBRARIES)
LOCAL_CHECK_ELF_FILES := false
include $(BUILD_PREBUILT)
"""
PROHIBIT_TOUCHING_APK = "\nLOCAL_REPLACE_PREBUILT_APK_INSTALLED := $(LOCAL_PATH)/$(LOCAL_MODULE).apk"
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


def extract_libs(destination):
    libs = []
    libspath = Path("/".join(destination.split("/")
                             [:-1])) / "libs"
    os.makedirs(libspath, exist_ok=True)
    with zipfile.ZipFile(destination, "r") as zf:
        files = zf.namelist()
        for file in files:
            if file.startswith("lib/arm64"):
                (libspath / Path(file.split("/")
                 [-1])).write_bytes(zf.read(file))
                libs.append(file)
    return libs


base_app = {
    "dont_touch_apk": False,
    "copy_libraries": False,
    "source": None,
    "priveleged": False
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
        if app["copy_libraries"] or app["dont_touch_apk"]:
            extras += PROHIBIT_TOUCHING_APK
        if app["priveleged"]:
            extras += PRIVELEGED
        if app["copy_libraries"]:
            extracted_libs = extract_libs(destination)
            libnames = []
            for lib in extracted_libs:
                libname = lib.split("/")[-1]
                result += LIB_TEMPALTE.format(
                    name=app["name"], libname=libname)
                applist.append(libname)
                libnames.append(libname.replace(".so", ""))
            extras += "\nLOCAL_SHARED_LIBRARIES := " + \
                " ".join(libnames)
        result = MAKE_TEMPLATE.format(name=app["name"], extras=extras, overrides=app.get("overrides", ""), required=" ".join(
            requirements["required"]), optional=" ".join(requirements["optional"])) + result
        if result != current_mk:
            with open(mkpath, 'w', newline="") as f:
                logger.info("Writing new makefile for %s", app["name"])
                f.write(result)
        else:
            logger.info("Makefile for %s is already up to date", app["name"])
    sys.stdout.write(' '.join(applist))


if __name__ == "__main__":
    main(sys.argv[-1])
