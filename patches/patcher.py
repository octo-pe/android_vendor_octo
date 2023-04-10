#!vendor/octo/.venv/bin/python3
from glob import glob
import sys
import os
import subprocess
from pathlib import Path


def execute_command(command, cwd=None):
    if not "whatif" in sys.argv:
        if cwd is None:
            cwd = os.getcwd()
        cwd = os.path.abspath(cwd)
        print("chdir", cwd)
        ret_code = subprocess.call(command.split(' '), cwd=cwd)
        assert ret_code == 0
    else:
        print("WhatIf: Executing", command)


def apply():
    patch_listing = {}

    for patch in glob("vendor/octo/patches/**/*.patch", recursive=True):
        patch_folder = "/".join(patch.replace("vendor/octo/patches",
                                "").split("/")[:-1])[1:]
        if patch_folder not in patch_listing:
            patch_listing[patch_folder] = []
        patch_listing[patch_folder].append(os.path.abspath(patch))
        print("Queuing up patch", patch, "for", patch_folder)
    for patch_folder in patch_listing:
        patch_listing[patch_folder] = sorted(
            patch_listing[patch_folder])
    for patch_folder, patches in patch_listing.items():
        if "unpatch" in sys.argv:
            patches = reversed(patches)
        execute_command("git reset --hard", patch_folder)
        execute_command("git clean -f -x", patch_folder)
        for patch in patches:
            if "unpatch" in sys.argv:
                command = f"git apply -R {patch}"
            else:
                command = f"git apply --whitespace=fix --3way -- {patch}"
            print("(Un)Applying patch", patch, "to", patch_folder)
            try:
                execute_command(command, patch_folder)
            except AssertionError as e:
                if "unpatch" not in sys.argv:
                    raise e


def create():
    root_dir = str(Path(__file__).parents[3])
    target_repo = subprocess.check_output(
        "git rev-parse --show-toplevel", shell=True).decode("utf-8").replace(root_dir, "").strip().replace("\n", "")
    patches_dir = str(Path(__file__).parents[0]) + target_repo
    print("Creating patch for", target_repo, patches_dir)
    os.makedirs(patches_dir, exist_ok=True)
    patch_id = "{:04d}".format(len(glob(f"{patches_dir}/*.patch")) + 1)
    print("Patch ID is", patch_id)
    patch_name = input("Enter name for patch:")
    with open(f"{patches_dir}/{patch_id}-{patch_name}.patch", 'wb') as f:
        f.write(subprocess.check_output("git diff --patch", shell=True))
    print("Patch created!")


if __name__ == "__main__":
    if "create" in sys.argv:
        create()
    else:
        apply()
