import mysql.connector

from mysql.connector.errors import InterfaceError, ProgrammingError, DatabaseError


class DBConnectionError(Exception):
    pass


class DBCredentialError(Exception):
    pass


class DBBaseError(Exception):
    pass


class DBSQLError(Exception):
    pass


class UseDatabase:
    def __init__(self, config: dict):
        self._config = config
        self._conn = None
        self._cursor = None

    def __enter__(self):
        try:
            self._conn = mysql.connector.connect(**self._config)
            self._cursor = self._conn.cursor()
            return self._cursor
        except InterfaceError as e:
            raise DBConnectionError(e)
        except ProgrammingError as e:
            raise DBCredentialError(e)
        except DatabaseError as e:
            raise DBBaseError(e)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is ProgrammingError:
            raise DBSQLError(exc_val)

        self._conn.commit()
        self._cursor.close()
        self._conn.close()
