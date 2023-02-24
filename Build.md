## Requirements

- Python 3
- cmake for building
- libav / ffmpeg (swscale, avutil and avcodec)
- pybind11 (will be automatically downloaded from github if not found)

## Building and Installing

### Windows

The suggested way to obtain ffmpeg is through [vcpkg](https://github.com/microsoft/vcpkg). Assuming all the setup including VC integration has been done, we can install the x64 libraries with

```cmd
vcpkg.exe install ffmpeg:x64-windows
```

You can build the extension module with python poetry almost normally. However cmake is used internally and we have to let it know the search paths to our libs. Hence the additional `CMAKE_USER_ARGS` argument with the toolchain file as per vcpkg instructions.

```cmd
$Env:CMAKE_USER_ARGS="-DCMAKE_TOOLCHAIN_FILE=[path to vcpkg]/scripts/buildsystems/vcpkg.cmake"
python -m venv venv
./venv/Scripts/Activate.ps1
pip install --upgrade pip
pip install poetry==1.1.14
poetry install
poetry build
```
