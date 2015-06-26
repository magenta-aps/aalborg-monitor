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
    result = subprocess.call(['AutoIT3.exe', sys.argv[1]], env=env)

    # Clean up if run was successful
    if 0 == result:
        run.finish()
