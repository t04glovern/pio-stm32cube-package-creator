#!/usr/bin/env python3 
import sys
import os
import subprocess
from os import path
from pathlib import Path    
import argparse
import shutil
import json
import datetime

# list of all repos with folder names 
repos = [
    ("f0", "https://github.com/STMicroelectronics/STM32CubeF0.git"),
    ("f1", "https://github.com/STMicroelectronics/STM32CubeF1.git"),
    ("f2", "https://github.com/STMicroelectronics/STM32CubeF2.git"),
    ("f3", "https://github.com/STMicroelectronics/STM32CubeF3.git"),
    ("f4", "https://github.com/STMicroelectronics/STM32CubeF4.git"),
    ("f7", "https://github.com/STMicroelectronics/STM32CubeF7.git"),
    ("l0", "https://github.com/STMicroelectronics/STM32CubeL0.git"),
    ("l1", "https://github.com/STMicroelectronics/STM32CubeL1.git"),
    ("l4", "https://github.com/STMicroelectronics/STM32CubeL4.git"),
    ("l5", "https://github.com/STMicroelectronics/STM32CubeL5.git"),
    ("g0", "https://github.com/STMicroelectronics/STM32CubeG0.git"),
    ("g4", "https://github.com/STMicroelectronics/STM32CubeG4.git"),
    ("h7", "https://github.com/STMicroelectronics/STM32CubeH7.git"),
    ("wb", "https://github.com/STMicroelectronics/STM32CubeWB.git"),
    ("mp1", "https://github.com/STMicroelectronics/STM32CubeMP1.git")
]

def get_script_directory(): 
    return path.dirname(os.path.realpath(__file__))

def run_command(args, cwd=None):
    if verbose and "git" in args:
        args.insert(2, "-v")
    if cwd is None: 
        cwd = get_script_directory()
    print("[+] Executing %s in path %s" % (' '.join(args), cwd))
    returncode = subprocess.call(args, shell=True, cwd=cwd)
    if returncode != 0:
        print("Command failed with exit code %d. Check output." % returncode)
        return False
    return True

def clone_git_repo(git_path, verbose=False):
    return run_command(['git', 'clone', git_path])

def get_target_folder_from_gitlink(git_link):
    # from link e.g. https://github.com/STMicroelectronics/STM32CubeF0.git
    # figure out that the folder name is STM32CubeF0
    dest_folder = git_link.rsplit('/', 0)[0]
    dest_folder = Path(dest_folder).stem
    dest_folder = Path(os.path.join(get_script_directory(), dest_folder))
    return dest_folder

def check_if_only_update(git_link):
    dest_folder = get_target_folder_from_gitlink(git_link)
    print("[+] Checking if folder %s already contains cloned data" % dest_folder)
    if dest_folder.exists(): 
        print("[+] Target download folder %s already exists. Only attempting a git pull." % dest_folder)
        if run_command(['git', 'pull'], cwd=str(dest_folder)) is False:
            print("[-] Git pull failed :(.")
            return True # continue with full clone
        else:
            print("[+] Git pull update was ok.")
            return False # do not full clone
    else: 
        return True # continue

def clone_or_update_all_repos(verb): 
    for (desc, git_link) in repos:
        print("[+] Cloning STM32%s package (%s)" % (str.upper(desc), git_link))
        if check_if_only_update(git_link):
            clone_git_repo(git_link)

def copy_sdk_directories(git_link, target_folder, target_folder_root):
    # get downloaded path
    download_root = get_target_folder_from_gitlink(git_link)
    target_root = Path(os.path.join(get_script_directory(), target_folder_root, target_folder))
    # create folder structure
    print("Download root: %s" % download_root)
    print("Target root: %s" % target_root)
    target_root.mkdir(parents=True, exist_ok=True)
    # only selectively copy folders and files to destionatio
    copy_list = [
        "Drivers",
        "Utilities",
        "Middlewares",
        "package.xml",
        "Release_Notes.html",
        "License.md"
    ]
    for elem in copy_list: 
        src_path = Path(download_root, elem)
        dest_path = Path(target_root, elem)
        if not src_path.exists():
            print("[-] Failed to find source path %s" % src_path)
            continue
        # copy src to destination
        print("[.] Copying %s to %s" % (src_path, dest_path))
        try:
            if src_path.is_dir():
                shutil.copytree(src_path, dest_path)
            else: #is file 
                shutil.copy2(src_path, dest_path)
        except Exception as exc:
            print("[-] Exception during copying.")
            print(str(exc))
    # special case: duplicate stm32YYxx_hal_conf_template.h from source download as stm32YYxx_hal_conf.h in target. 
    # this is what the current framawork-stm32cube package does, too..
    # works for all tested repos
    source_template = Path(download_root, "Drivers", "STM32" + str.upper(target_folder) + "xx_HAL_Driver", "Inc",  "stm32" + str.upper(target_folder) + "xx_hal_conf_template.h")
    dest_file = Path(target_root, "Drivers", "STM32" + str.upper(target_folder) + "xx_HAL_Driver", "Inc",  "stm32" + str.upper(target_folder) + "xx_hal_conf.h")
    print("Copying conf template from %s to %s" % (source_template, dest_file))
    try:
        shutil.copy2(source_template, dest_file)
    except Exception as exc:
        print("[-] Exception during copying.")
        print(str(exc))

    # fixup step 2: 
    # stm32cube builder scripts excepts all libs to be in Drivers/CMSIS/Lib/GCC. 
    # but with recent versions, some of these files have moved to CMSIS/DSP/Lib/GCC (like, libarm_cortexM4lf_math.a)
    # we have to move these files so that PlatformIO can find them. 
    dsp_lib_path = Path(target_root, "Drivers", "CMSIS", "DSP", "Lib", "GCC")
    if dsp_lib_path.exists(): 
        print("[.] Detected DSP libraries in %s. Attempting to move." % dsp_lib_path)
        shutil.move(dsp_lib_path, Path(target_root, "Drivers", "CMSIS", "Lib", "GCC"))


    # cleanup step: reduce download size by removing unnecessary folders
    to_delete = [
        "Drivers/CMSIS/docs",
        "Drivers/CMSIS/Lib/ARM",
        "Drivers/CMSIS/Lib/IAR",
        "Drivers/CMSIS/DSP/Lib/ARM",
        "Drivers/CMSIS/DSP/Lib/IAR",
        "Drivers/CMSIS/DSP/Projects/ARM",
        "Drivers/CMSIS/DSP/Projects/IAR",
        "Drivers/CMSIS/DSP/DSP_Lib_TestSuite",
        "Middlewares/Third_Party/LwIP/doc"
        "Utilities/Media" # huge bloat included in L4
    ]
    for elem in to_delete:
        delete_path = Path(target_root, elem)
        if not delete_path.exists() and (not "Utilities" in str(delete_path) or "DSP" in str(delete_path)):
            print("[-] Fail: To be deleted path does not exist: %s" % delete_path)
            continue
        try:
            print("Deleting unneccessary file %s" % delete_path)
            shutil.rmtree(delete_path)
        except Exception as exc:
            print("[-] Exception during deletion.")
            print(str(exc))

def copy_all_sdk_dirs(target_folder_root="created_package"):
    for (desc, git_link) in repos:
        print("[+] Copying downloaded SDK folders into new package for %s" % (str.upper(desc)))
        # desc text is also target folder name
        copy_sdk_directories(git_link, desc, target_folder_root)

def get_package_datecode(): 
    return '{0:%y%m%d}'.format(datetime.datetime.utcnow())

def create_pio_package(target_folder_root="created_package"):
    src_path = Path(os.path.join(get_script_directory(), "original_platformio_folder"))
    dest_path = Path(os.path.join(get_script_directory(), target_folder_root, "platformio"))
    print("[.] Copying %s to %s" % (src_path, dest_path))
    try:
        shutil.copytree(src_path, dest_path)
    except Exception as exc:
        print("[-] Exception during copying.")
        print(str(exc))
    # create update package.json
    package_data = {
        "description": "STM32Cube embedded software libraries",
        "name": "framework-stm32cube",
        "system": "*",
        "url": "http://www.st.com/en/embedded-software/stm32cube-embedded-software.html",
        "version": "2.0." + get_package_datecode()
    }
    package_content = json.dumps(package_data, indent='\t')
    print("[.] Writing package.json file\n%s" % package_content)
    package_dest = Path(os.path.join(get_script_directory(), target_folder_root, "package.json"))
    try:
        package_dest.write_text(package_content)
    except Exception as exc: 
        print("[-] Exception during copying tp %s" % str(package_dest))
        print(str(exc))
   
def get_version(folder): 
    output = subprocess.run(['git', 'describe', "--tags"], cwd=folder, stdout=subprocess.PIPE).stdout
    return output.decode('utf-8').strip()

def print_summary():
    print("[+] Version summary of downloaded packages:")
    for (desc, git_link) in repos:
        print("[+] Package STM32%s version: %s" % (str.upper(desc), get_version(get_target_folder_from_gitlink(git_link))))

def create_tarball(pack_folder_root="created_package"): 
    print("[.] Creating package. This will take a while.")
    if run_command(["pio", "package", "pack", pack_folder_root], cwd=get_script_directory()):
        print("[+] Package created.")
        for p in Path(get_script_directory()).glob("framework-stm32cube-*.tar.gz"):
            print("[+] %s (%.2f MB)" % (p, p.stat().st_size / 1024.0 / 1024.0))               
    else:
        print("[+] Package creation failed! Check output")

def main_func(verb, do_create_tarball, skip):
    if not skip:
        clone_or_update_all_repos(verb)
    copy_all_sdk_dirs()
    create_pio_package()
    print_summary()
    if do_create_tarball:
        create_tarball()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Helper program to download the latest version of STM32Cube packages and auto-package them as a PlatformIO package.")
    parser.add_argument("-v", "--verbose", help="increase output verbosity",
                    action="store_true")
    parser.add_argument("-t", "--create-tarball", help="Automatically use 'pio package' to create the complete .tar.gz package",
                    action="store_true")
    parser.add_argument("-s", "--skip-update", help="Do not update repositories, just create new package.",
                    action="store_true")
    parser.add_argument("--show-versions", help="Only show versions of downloaded pacakges.", action="store_true")
    args = parser.parse_args()
    verbose = args.verbose
    do_create_tarball = args.create_tarball
    skip = args.skip_update
    if args.show_versions: 
        print_summary()
        exit(0)
    main_func(verbose, do_create_tarball, skip)