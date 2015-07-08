import os
import django
from django.contrib.auth.models import User

if __name__ == '__main__':
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE", "aalborgmonitor.settings"
    )
    try:
        django.setup()
        users = User.objects.filter(is_superuser=True)
        if len(users) > 0:
            print "Superusers already exists: %s" % (
                ", ".join([str(u) for u in users])
            )
            exit(0)
        else:
            raise Exception("No superusers found")
    except Exception as e:
        print e
        exit(1)

