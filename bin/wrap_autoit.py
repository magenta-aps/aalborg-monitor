import sys
import os
import subprocess
from django.conf import settings
from django import db
from appmonitor.models import TestSuite

if __name__ == "__main__":
    if not len(sys.argv) > 1:
        raise Exception("You must specify a script to run")

    env = os.environ.copy()
    env['APPMONITOR_SQLITE_FILE'] = str(settings.DATABASES['default']['NAME'])

    # Create a suite
    suite = TestSuite.locate_by_path(sys.argv[1])
    run = suite.start_run()
    env['APPMONITOR_RUN_ID'] = str(run.pk)

    # Disconnect the django db connection to avoid locking issues
    db.connection.close()

    # Call autoit
    script_file = sys.argv[1]
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
            "AutoIT", "Aut2Exe", "Aut2Exe.exe"
        )
        sys.stderr.write("Compiling %s => %s%s" % (script_file, exe_file, os.linesep))
        subprocess.call([
            aut2exe_file,
            "/in", script_file,
            "/out", exe_file,
            "/console"
        ])

    # call the compiled exe file
    result = subprocess.call([exe_file], env=env)

    # Clean up
    run.finish(result)
