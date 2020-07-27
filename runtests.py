#!/usr/bin/env python
import os
import sys

import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = 'paranoid_model.tests.test_settings'
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    test_suite = sys.argv[1] if len(sys.argv) > 1 else 'paranoid_model.tests'
    failures = test_runner.run_tests([test_suite])
    sys.exit(bool(failures))
