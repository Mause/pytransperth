import coverage

import run_tests

cov = coverage.coverage()
cov.start()

try:
    run_tests.main()
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
