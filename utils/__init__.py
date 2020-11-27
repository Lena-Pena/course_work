def make_dict_list_from_rows(cursor):
    rows = cursor.fetchall()
    column_names = cursor.column_names

    keyed_rows = []

    for row in rows:
        keyed_row = {}

        for (colIndex, name) in enumerate(column_names):
            keyed_row[name] = row[colIndex]

        keyed_rows.append(keyed_row)

    return keyed_rows
