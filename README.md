# STM32Cube package Creator

## Description

This tool is intended for the automatic creation of a `framework-stm32cube` package, which includes all the latest versions of the sub-packages from ST Microelectronics. 

## Inner workings

The script roughly does the following
1. `git clone` a list of 14 `STM32Cube*` respositories from STM 
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
usage: stm32cube_package_creater.py [-h] [-v] [-t] [-s]

Helper program to download the latest version of STM32Cube packages and auto-
package them as a PlatformIO package.

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         increase output verbosity
  -t, --create-tarball  Automatically use 'pio package' to create the complete
                        .tar.gz package
  -s, --skip-update     Do not update repositories, just create new package.
```

Execution of `python stm32cube_package_creater.py -t` should createa a `created_package` folder in the scripts directory in which the package will be created. Then, a tarball should be created.

## Usage of generated package 

As long as this package is not yet merged, the cleanest way to use it is to manually override the `framework-stm32cube` in the project. This can be done using [`platform_packages`](https://docs.platformio.org/en/latest/projectconf/section_env_platform.html#platform-packages) and a download link to the created package. E.g., to use the reference package uploaded in this repo, add 

```
platform_packages = 
    framework-stm32cube@https://raw.githubusercontent.com/maxgerhardt/pio-stm32cube-package-creator/master/framework-stm32cube-2.0.201021.tar.gz
```

to the `platformio.ini` of the project.