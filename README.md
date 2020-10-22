# STM32Cube package Creator

## Description

This tool is intended for the automatic creation of a `framework-stm32cube` package, which includes all the latest versions of the sub-packages from ST Microelectronics. 

## **!!UPDATE!!** 

Uplaoding the 400MB `framework-stm32cube` cube file to this Git repo with Large-File-Storage (LFS) was a pretty bad idea because my entire quote of only 1GB bandwidth and storage was exceeded instantly. (Every download causes a bandwidth usage of 400MB). 

The file was moved to Google Drive, that does not have such restrictions: 

https://drive.google.com/file/d/1306PQZXcKkuDVKcFetv0D9rsbZuIaDDV/view?usp=sharing 


## Version overview 

Comparison regarding package versions included in PIO's current `framework-stm32cube` and this ones. PIO's versions are mostly around 2 years old and several versions behind.

|Series| PIO version | This version |
|------|:-------------:|---------------|
| F0 	 | 1.9.0       | 1.11.1        | 	
| F1 	 | 1.7.0       | 1.8.2         |	
| F2 	 | 1.7.0       | 1.9.1         |	
| F3 	 | 1.10.0      | 1.11.1        | 	
| F4 	 | 1.23.0      | 1.25.1        | 	
| F7 	 | 1.14.0      | 1.16.0        | 	
| H7 	 | 1.3.0       | 1.8.0         |	
| G0 	 | ❌ not included | 1.3.0-1 | 	
| G4 	 | ❌ not included | 1.3.0 | 	
| L0 	 | 1.11.0      | 1.11.3        | 	
| L1 	 | 1.8.1       | 1.10.1        | 	
| L4 	 | 1.13.0      | 1.16.0        | 	
| L5 	 | ❌ not included | 1.3.1 | 	
| MP1  | ❌ not included | 1.2.0-2 | 	
| WB  | ❌ not included | 1.9.0 | 	


## Inner workings

The script roughly does the following
1. `git clone` a list of 15 `STM32Cube*` respositories from STM 
2. Copy the needed folders and files into a new package folder 
3. Remove some files to decrease download size 
4. Apply some quirks (see below)
5. Generate a `package.json` with updated version info
6. use `pio package pack` to create the final tarball

If all works out, executing the script will give you a nice up-to-date `framework-stm32cube-2.0.x.tar.gz`.

## Quirks

The [stm32cube.py](https://github.com/platformio/platform-ststm32/blob/develop/builder/frameworks/stm32cube.py) build scripts currently expects some files to be in special folders, which have changed in newer revisions of the STM32Cube packages. Specifically, files which used to be in `Drivers/CMSIS/Lib/GCC` are now found in the DSP folder. Thus, we have to move the folder to the right place.

Also, the `Drivers/CMSIS/DSP_Lib` folder was renamed to just `DSP`, but PIO doesn't explicitly use this path, so it can be ignored.

The original `framework-stm32cube` package has a HAL config file, which is a copy of the template file. Usually, projects bring their own config file to only enable modules that they need. But PIO copies the template, which enables all modules. This behaviour is replicated in the script.

Although this package has all known STM32Cube packages, support for the new series (L5, G0, G4, WB, ..) still incomplete since the `platformio\ldscripts` folder is lacking the linker files (e.g. `STM32L552CE_FLASH.ld`). These must be obtained from the STM32CubeMX generator and added for each new board that would be added in the future to complete support.

## Usage of script

```
>python stm32cube_package_creater.py --help
usage: stm32cube_package_creater.py [-h] [-v] [-t] [-s] [--show-versions]

Helper program to download the latest version of STM32Cube packages and auto-
package them as a PlatformIO package.

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         increase output verbosity
  -t, --create-tarball  Automatically use 'pio package' to create the complete
                        .tar.gz package
  -s, --skip-update     Do not update repositories, just create new package.
  --show-versions       Only show versions of downloaded pacakges.
```

Execution of `python stm32cube_package_creater.py -t` should createa a `created_package` folder in the scripts directory in which the package will be created. Then, a tarball should be created.

## Usage of generated package 

As long as this package is not yet merged, the cleanest way to use it is to manually override the `framework-stm32cube` in the project. This can be done using [`platform_packages`](https://docs.platformio.org/en/latest/projectconf/section_env_platform.html#platform-packages) and a link to the created package. 

Since the package was removed from this repo (see update section), you **have to download the `tar.gz` package yourself to some path on your harddrive. The `file://` pseudo-protocol can then be used to as "download link". For example, if you downloaded it to `D:\pio-stm32cube-package-creator\framework-stm32cube-2.0.201021.tar.gz`, add 
 

```
platform_packages = 
    framework-stm32cube@file://D:\pio-stm32cube-package-creator\framework-stm32cube-2.0.201021.tar.gz
```

to the `platformio.ini` of the project.

If you use Linux or Mac, the path will simply be different, e.g. `file:///User/myuser/Downloads/framework-stm32cube-2.0.201021.tar.gz`. (tripple `/` because of `file://` plus path `/User/...`).

## Example project 

Use https://github.com/platformio/platform-ststm32/tree/develop/examples/stm32cube-hal-blink but override the `platformio.ini` with e.g. 

```
; global overrides
[env]
platform_packages = 
    framework-stm32cube@file://D:\pio-stm32cube-package-creator\framework-stm32cube-2.0.201021.tar.gz

; compile for STM32F072RB
[env:nucleo_f072rb]
platform = ststm32
framework = stm32cube
board = nucleo_f072rb
build_flags = -DF0
```

While adapting the path above.


# Open ToDos

* verify that examples are still compilable, or update them if APIs have changed
* For `platform-ststm32`: Allow projects to specify their own hal config file
    * see proposed changes in https://github.com/dingyifei/platform-ststm32
* add some examples for devices from new series (L5, G0, G4, WB, MP1, ..)
   * needs linker scripts