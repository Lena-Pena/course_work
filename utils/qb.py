class QB:
    def __init__(self):
        self._str = ''

    def select(self, what):
        self._str += ' SELECT {}'.format(what)

        return self

    def from_table(self, table):
        self._str += ' FROM {}'.format(table)

        return self

    def where(self, clause):
        self._str += ' WHERE {}'.format(clause)

        return self

    def build(self):
        return self._str