def make_dict_list_from_rows(cursor):
    rows = cursor.fetchall()
    column_names = cursor.column_names

    return [
        {column_names[i]: rows[i]}
        for i in range(len(rows))
    ]
