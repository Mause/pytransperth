import coverage

from __init__ import main

cov = coverage.coverage()
cov.start()

try:
    main()
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
