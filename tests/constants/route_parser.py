from lxml.html import builder as E

HEADER = E.HTML(E.TD(
    E.TABLE(
        E.TD(E.SPAN('DURATION')),
        E.TD(E.SPAN('LINKS'))
    ),
    E.TABLE('MISC')
))
