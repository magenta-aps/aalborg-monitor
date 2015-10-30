import subprocess
import os
import platform

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ARCH_POSTFIX = "win32"
if platform.architecture()[0] == "64bit":
    ARCH_POSTFIX = "win_amd64"

# Install nympy if it is missing
try:
    import numpy
except ImportError:
    whl = 'numpy-1.10.1+mkl-cp27-none-%s.whl' % ARCH_POSTFIX
    subprocess.call([
        'pip.exe',
        'install',
        os.path.join(BASE_DIR, "lib", whl)
    ]);
