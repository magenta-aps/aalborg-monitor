# The contents of this file are subject to the Mozilla Public License
# Version 2.0 (the "License"); you may not use this file except in
# compliance with the License. You may obtain a copy of the License at
#    http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS IS" basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
# for the specific language governing rights and limitations under the
# License.
#
# Copyright 2015 Magenta Aps
#
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
