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
import os
import urllib2
import zipfile
import tempfile
import time
import platform
import subprocess
import ssl

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIN_DIR = os.path.join(BASE_DIR, "bin")

AUTO_IT_DIR = os.path.join(BASE_DIR, "AutoIT")
AUTO_IT_ZIP_URL=(
    "https://www.autoitscript.com/autoit3/files/archive/autoit/" +
    "autoit-v3.3.12.0.zip"
)

SELENIUM_ZIP_URL = (
    "http://selenium-release.storage.googleapis.com/2.46/" +
    "IEDriverServer_Win32_2.46.0.zip"
)
SELENIUM_EXE_FILE = "IEDriverServer.exe"
SELENIUM_EXE_PATH = os.path.join(BIN_DIR, SELENIUM_EXE_FILE)

ARCH_POSTFIX = ""
if platform.architecture()[0] == "64bit":
    ARCH_POSTFIX = "_x64"

SQLITE_DLL_FILE = "sqlite3%s.dll" % (ARCH_POSTFIX)
SQLITE_DLL_PATH = os.path.join(AUTO_IT_DIR, SQLITE_DLL_FILE)
SQLITE_DLL_URL = (
    "https://www.autoitscript.com/autoit3/pkgmgr/sqlite/" +
    SQLITE_DLL_FILE
)

def download(url):
    file_name = url.split('/')[-1]
    file_name = os.path.join(BASE_DIR, file_name);

    if os.path.exists(file_name):
        print "Using existing version of %s for %s" % (file_name, url)
        print "Delete it if you wish to re-download"
        return file_name

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    u = urllib2.urlopen(url, context=ctx)
    f = open(file_name, 'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    print "Downloading: %s Bytes: %s" % (file_name, file_size)

    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            print ""
            break

        file_size_dl += len(buffer)
        f.write(buffer)
        status = r"%10d  [%3.2f%%]" % (
            file_size_dl,
            file_size_dl * 100. / file_size
        )
        status = status + chr(8)*(len(status)+1)
        print status,

    f.close()
    return file_name


if __name__ == '__main__':
    if not os.path.exists(AUTO_IT_DIR):
        print "Downloading and installing AutoIT"

        zip_file_name = download(AUTO_IT_ZIP_URL)
        tmp_dir = tempfile.mkdtemp('','tmp-autoit', BASE_DIR)
        zfile = zipfile.ZipFile(zip_file_name)
        zfile.extractall(tmp_dir)
        zfile.close()
        tries = 0

        # It might take some time before we're allowed to move the file
        # maybe because of antivirus software
        while True:
            try:
                os.rename(
                    os.path.join(tmp_dir, "install"),
                    AUTO_IT_DIR
                )
                break
            except Exception as e:
                tries = tries + 1
                if tries >= 5:
                    raise e
                print "Moving files failed, retrying..."
                time.sleep(1)

        os.rmdir(tmp_dir)
        os.remove(zip_file_name)
        print "Done"


    if not os.path.exists(SELENIUM_EXE_PATH):
        print "Downloading and extracting Selenium IE Driver"
        zip_file_name = download(SELENIUM_ZIP_URL)
        tmp_dir = tempfile.mkdtemp('','tmp-selenium', BASE_DIR)
        zfile = zipfile.ZipFile(zip_file_name)
        zfile.extractall(tmp_dir)
        zfile.close()
        while True:
            try:
                os.rename(
                    os.path.join(tmp_dir, SELENIUM_EXE_FILE),
                    SELENIUM_EXE_PATH
                )
                break
            except Exception as e:
                tries = tries + 1
                if tries >= 5:
                    raise e
                print "Moving files failed, retrying..."
                time.sleep(1)
        os.rmdir(tmp_dir)
        os.remove(zip_file_name)
        print "Done"

    if not os.path.exists(SQLITE_DLL_PATH):
        print "Downloading and extracting SQLite DLL"
        download_file_name = download(SQLITE_DLL_URL)
        while True:
            try:
                os.rename(download_file_name, SQLITE_DLL_PATH)
                break
            except Exception as e:
                tries = tries + 1
                if tries >= 5:
                    raise e
                print "Moving files failed, retrying..."
                time.sleep(1)
        print "Done"

    print "Setup complete"