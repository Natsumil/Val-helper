from cx_Freeze import setup, Executable
import sys
import os

build_exe_options = {
    "packages": ["os", "sys", "flet", "time", "requests", "base64", "psutil", "threading"],
    "excludes": [],
    "include_files": []
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="VAL-Helper-Flet",
    version=1.0,
    description='VAL-Helper with Flet UI',
    executables=[Executable("main.py", base=base,icon="./assets/icon.ico", target_name="VAL-Helper-Flet.exe")],
    options={"build_exe": build_exe_options}
)