# STM32Cube package Creator

## Description

This tool is intended for the automatic creation of a `framework-stm32cube` package, which includes all the latest versions of the sub-packages from ST Microelectronics. 

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

As long as this package is not yet merged, the cleanest way to use it is to manually override the `framework-stm32cube` in the project. This can be done using [`platform_packages`](https://docs.platformio.org/en/latest/projectconf/section_env_platform.html#platform-packages) and a download link to the created package. E.g., to use the reference package uploaded in this repo, add 

```
platform_packages = 
    framework-stm32cube@https://raw.githubusercontent.com/maxgerhardt/pio-stm32cube-package-creator/master/framework-stm32cube-2.0.201021.tar.gz
```

to the `platformio.ini` of the project.