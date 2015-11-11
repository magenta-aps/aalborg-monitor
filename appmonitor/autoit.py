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
import sys
import os
import subprocess
from django.conf import settings
from django import db
from appmonitor.models import TestSuite
import django
import platform
import shutil

ARCH_POSTFIX = ""
if platform.architecture()[0] == "64bit":
    ARCH_POSTFIX = "_x64"


SQLITE_DLL = "sqlite3%s.dll" % ARCH_POSTFIX
AU2EXE = "Aut2Exe%s.exe" % ARCH_POSTFIX

# Compiles and runs an autoit script in the context of the specified test run
def run_autoit_script(script_path, test_run = None):
    env = os.environ.copy()
    env['APPMONITOR_SQLITE_FILE'] = str(settings.DATABASES['default']['NAME'])
    if test_run:
        env['APPMONITOR_RUN_ID'] = str(test_run.pk)

    # Disconnect the django db connection to avoid locking issues
    db.connection.close()

    # Call autoit
    script_file = script_path
    ext_idx = len(script_file) - 4
    ext = script_file[ext_idx:].lower()

    if ext != ".au3":
        raise Exception("Target script is not an .au3 file")

    exe_file = script_file[:ext_idx] + ".exe"
    exe_timestamp = 0
    if os.path.isfile(exe_file):
        exe_timestamp = os.path.getmtime(exe_file)

    # Recompile script if it has changed or has not yet been compiled
    if os.path.getmtime(script_file) > exe_timestamp:
        aut2exe_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "AutoIT", "Aut2Exe", AU2EXE
        )
        sys.stderr.write(
            "Compiling %s => %s%s" % (script_file, exe_file, os.linesep)
        )
        result = subprocess.call([
            aut2exe_file,
            "/in", script_file,
            "/out", exe_file,
            "/console"
        ])
        if result != 0:
            return result

    # Copy in SQLite DLL if needed
    sqlite_file = os.path.join(os.path.dirname(script_file), SQLITE_DLL)
    if not os.path.exists(sqlite_file):
        src_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "AutoIT", SQLITE_DLL
        )
        shutil.copyfile(src_file, sqlite_file)

    # call the compiled exe file
    return subprocess.call([exe_file], env=env)

# Creates a test run for the specified autoit script and runs it
def wrap_run_autoit(script_path):
    # Create a suite
    suite = TestSuite.locate_by_path(script_path)
    run = suite.start_run()

    result = run_autoit_script(script_path, run)

    run.finish(result)
    
    return result

# When run as a script, compone and execute the script given
# by the first argument in the context specified by the scripts'
# location.
if __name__ == "__main__":
    if not len(sys.argv) > 1:
        raise Exception("You must specify a script to run")

    django.setup()
    sys.exit(wrap_run_autoit(sys.argv[1]))