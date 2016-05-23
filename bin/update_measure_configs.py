# encoding: utf8

import django
from appmonitor.models import TestMeasure
from appmonitor.models import TestMeasureConfig
from appmonitor.models import TestSuite

def update():
    distinct_names = TestMeasure.objects.exclude(
        test_run__test_suite__name="DEBUG"
    ).values(
        "test_run__test_suite__pk",
        "test_run__test_suite__name",
        "name"
    ).order_by(
        "test_run__test_suite__name",
        "name"
    ).distinct()
    for x in distinct_names:
        pk = x['test_run__test_suite__pk']
        qs = TestMeasure.objects.filter(
            config__isnull=True,
            test_run__test_suite__pk=pk,
            name=x['name']
        )
        count = qs.count()
        print "%s => %s: %s" % (
            x["test_run__test_suite__name"],
            x["name"],
            count
        )
        if count > 0:
            try:
                cnf = TestMeasureConfig.objects.get(
                    test_suite=pk,
                    name=x['name']
                )
            except TestMeasureConfig.DoesNotExist:
                cnf = TestMeasureConfig(
                    test_suite=TestSuite.objects.get(pk=pk),
                    name=x['name']
                )
                cnf.save()
            qs.update(
                config=cnf
            )
        

if __name__ == '__main__':
    django.setup()
    update()