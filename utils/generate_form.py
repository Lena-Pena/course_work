def generate_form():
    return [
        {
            "label": "Первое поле",
            "type": "text",
            "name": "first"
        },
        {
            "label": "Второе поле",
            "type": "date",
            "name": "second"
        },
        {
            "label": "Третье поле",
            "type": "checkbox",
            "name": "third"
        }
    ]