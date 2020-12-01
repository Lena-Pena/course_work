def make_dict_list_from_rows(cursor):
    rows = cursor.fetchall()
    column_names = cursor.column_names

    keyed_rows = []

    for row in rows:
        keyed_row = {}

        # enumerate делает из такого массива
        #     ['a', 'b', 'c']
        # такой
        #     [(0, 'a'), (1, 'b'), (2, 'c')]
        for (column_index, column_name) in enumerate(column_names):
            keyed_row[column_name] = row[column_index]

        keyed_rows.append(keyed_row)

    return keyed_rows
