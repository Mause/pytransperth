from lxml.html import builder as E

HEADER = E.HTML(E.TD(
    E.TABLE(
        E.TD(E.SPAN('DURATION')),
        E.TD(E.SPAN('LINKS'))
    ),
    E.TABLE('MISC')
))

STEP_BUS = E.HTML(
    E.TR(
        E.TD(
            E.IMG(alt="bus")
        ),
        E.TD(
            E.SPAN('ONE'),
            E.SPAN('TWO')
        ),
        E.TD(
            E.SPAN('THREE'),
            E.SPAN('FOUR')
        )
    )
)

STEP_WALK = E.HTML(
    E.TR(
        E.TD(
            E.IMG(alt="walk")
        ),
        E.TD(
            E.SPAN('ONE'),
            E.SPAN('TWO')
        ),
        E.TD(
            E.SPAN('THREE'),
            E.SPAN('FOUR')
        )
    )
)
