FARE_BASIC_XML = '''\
<table width="96%" border="0" cellspacing="0" cellpadding="0" align="center">
    <tr>
        <td colspan="4">
            <hr width="100%" size="1" color="#339900"/>
        </tr>
    </td>
    <tr>
        <td width="25%" align="left" class="NormalBold">Fare Type</td>
        <td width="20%" align="left" class="NormalBold">Adult</td>
        <td width="20%" align="left" class="NormalBold">Concession</td>
        <td width="35%" align="left" class="NormalBold">Comments</td>
    </tr>
    <tr>
        <td align="left" class="Normal">1 Zone Cash Fare</td>
        <td align="left" class="Normal">$2.80</td>
        <td align="left" class="Normal">$1.10</td>
        <td align="left" class="Normal">Current Cash Fare.</td>
    </tr>
    <tr>
        <td align="left" class="Normal">1 Zone SmartRider</td>
        <td align="left" class="Normal">$2.38</td>
        <td align="left" class="Normal">$0.94</td>
        <td align="left" class="Normal">15 percent add value discount.</td>
    </tr>
    <tr>
        <td align="left" class="Normal">1 Zone SmartRider</td>
        <td align="left" class="Normal">$2.10</td>
        <td align="left" class="Normal">$0.83</td>
        <td align="left" class="Normal">25 percent add value discount.</td>
    </tr>
</table>
'''

FARE_BASIC_ROUTES = [{'meta': {'links': {
    'getFares': ['fare', 'request', 'args']
}}}]

FARE_OUTPUT = {
    'adult': {'1 Zone Cash Fare': 1.1, '1 Zone SmartRider': 0.83},
    'concession': {'1 Zone Cash Fare': 1.1, '1 Zone SmartRider': 0.83}
}
