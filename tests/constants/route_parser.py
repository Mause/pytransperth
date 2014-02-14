from lxml.html import builder as E
from lxml.etree import HTML, tounicode


HEADER = E.HTML(E.TD(
    E.TABLE(
        E.TD(E.SPAN('DURATION')),
        E.TD(E.SPAN('LINKS'))
    ),
    E.TABLE('MISC')
))

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

MISC = HTML(
    '''
    <tr bgcolor="#e4f6e9">
        <td class="TP_M_Text" width="3%">&nbsp;</td>
        <td class="TP_M_Text" width="25%"><b>Depart Time:</b> 10:30 AM<br><b>Arrival Time:</b> 11:00 AM
        </td>
        <td class="TP_M_Text" width="25%"><b>Number of Legs:</b> &nbsp;1<br><b>Total Walking Distance:</b> 0 m</td>
        <td class="TP_M_Text" width="47%">
        <table cellpadding="1"><tbody><tr><td><img src="/DesktopModules/JourneyPlannerResults/images/Bus.gif" alt="70" title="70"></td></tr></tbody></table></td>
    </tr>
    '''
).xpath('//html/body/tr')[0]


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
