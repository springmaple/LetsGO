import os.path

from cx_Freeze import setup, Executable

PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))
VERSION = '1.0.0'

setup(
    name='redirect',
    version=VERSION,
    author='YO TIME TRADING',
    options={"build_exe": {
        'packages': [],
        'include_files': ['settings.json']
    }},
    executables=[
        Executable('index.py', targetName='LetsGo.exe'),
    ]
)
