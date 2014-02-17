import ipy_table

fares = {
    'adult': {'1 Zone Cash Fare': 1.1, '1 Zone SmartRider': 0.83},
    'concession': {'1 Zone Cash Fare': 1.1, '1 Zone SmartRider': 0.83}
}


keys, values = zip(*fares.items())

table_rows = [[''] + list(keys)]

for key in values[0].keys():
    table_rows.append([key])

    for ticket_type in values:
        table_rows[-1].append(ticket_type[key])


table = ipy_table.make_table(table_rows)
table.apply_theme('basic')
