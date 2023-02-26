import glob
import os
import sqlite3


class Database:
    def __init__(self, database_filename: str) -> None:
        self.conn = sqlite3.connect(f"databases/{database_filename}")
        self.cursor = self.conn.cursor()

    def __del__(self) -> None:
        self.cursor.close()
        self.conn.close()

    @staticmethod
    def get_databases() -> list[str]:
        return [os.path.basename(path) for path in glob.glob("databases/*.db")]

    @staticmethod
    def create_database(name: str) -> None:
        conn = sqlite3.connect(f"databases/{name}.db")
        conn.close()

    @staticmethod
    def delete_database(filename: str) -> None:
        file_path = f"databases/{filename}"

        if os.path.exists(file_path):
            os.remove(file_path)

    def get_tables(self) -> list[str]:
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = list(map(lambda x: x[0], self.cursor.fetchall()))

        return tables

    def get_info_columns_of_table(self, table_name: str) -> list[tuple]:
        self.cursor.execute(f"PRAGMA table_info({table_name})")
        result = self.cursor.fetchall()

        return result

    def get_rows_from_table(self, table_name: str) -> list[tuple]:
        self.cursor.execute(f"SELECT * FROM {table_name}")
        result = self.cursor.fetchall()

        return result

    def create_table(self, table_name: str, columns: list[str]) -> None:
        sql_columns = ", ".join([f"{i} TEXT" for i in columns])
        sql = f"""
CREATE TABLE IF NOT EXISTS {table_name} (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    {sql_columns}
);
"""
        print(sql)
        self.cursor.execute(sql)
        self.conn.commit()

    def drop_table(self, table_name: str) -> None:
        self.cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        self.conn.commit()

    def add_row_to_table(self, table_name, data: dict[str, str]) -> bool:
        columns = list(data.keys())
        values = list(data.values())

        sql = f"INSERT INTO {table_name} ({', '.join(columns)})" \
              f"VALUES ({', '.join('?' * len(values))})"

        try:
            self.cursor.execute(sql, values)
            self.conn.commit()
        except sqlite3.OperationalError:
            return False

        return True

    def delete_row_from_table(self, table_name: str, id: int) -> None:
        self.cursor.execute(f"DELETE FROM {table_name} WHERE id = ?", (id, ))
        self.conn.commit()

    def get_table_rows(self, table: str) -> list[dict]:
        self.conn.row_factory = Database.dict_factory
        cursor = self.conn.cursor()
        cursor.execute(f'SELECT * FROM {table}')
        return cursor.fetchall()

    @staticmethod
    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d
