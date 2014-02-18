import os

from lxml.html import builder as E
from lxml.etree import HTML

PATH = os.path.dirname(__file__)
with open(os.path.join(PATH, 'header.html')) as fh:
    HEADER = HTML(fh.read()).find('body/tr')

STEPS = E.HTML(
    E.TD(
        E.DIV(
            E.TABLE('STEP1'),
            E.TABLE('STEP2'),
            E.TABLE('EXCLUDED')
        )
    )
)

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

STEP_TRAIN = E.HTML(
    E.TR(
        E.TD(
            E.IMG(alt="train")
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

STEP_INVALID = E.HTML(
    E.TR(
        E.TD(
            E.IMG(alt="invalid")
        )
    )
)

with open(os.path.join(PATH, 'misc.html')) as fh:
    MISC = HTML(fh.read()).xpath('//html/body/tr')[0]


IMG = E.IMG(
    onclick="getFares('11/11/1111', 1111)"
)

LINKS = E.HTML(
    E.DIV(
        E.IMG('ONE'),
        E.IMG('TWO')
    )
)

DURATION = E.HTML(
    E.SPAN(
        E.SPAN('IGNORED'),
        E.SPAN('11:11 hrs')
    )
)
