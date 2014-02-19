import unittest
import coverage

from __init__ import suite

cov = coverage.coverage()
cov.start()

try:
    unittest.TextTestRunner().run(suite())
finally:
    cov.stop()
    cov.save()

    cov.html_report(omit=[
        "*.google_appengine*",
        "*dms_venv*",
        "*slpp*",
        "*tests*",
        "*appengine_config*"
    ])
