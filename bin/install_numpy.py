import subprocess
import os
import platform
from initial_setup import download

DL_URI_TEMPLATE = "".join([
    "https://redmine.magenta-aps.dk/magenta_files/aalborg/",
    'numpy-1.10.1+mkl-cp27-none-%s.whl'
])
ARCH_POSTFIX = "win32"
if platform.architecture()[0] == "64bit":
    ARCH_POSTFIX = "win_amd64"

if __name__ == '__main__':
    # Install nympy if it is missing
    try:
        import numpy
    except ImportError:
        filename = download(DL_URI_TEMPLATE % ARCH_POSTFIX)
        subprocess.call(['pip.exe', 'install', filename ]);
