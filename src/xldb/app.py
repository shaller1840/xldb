"""
An application to manage a simple database
"""
import os
import sqlite3
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

class TableBox(toga.Box):

    def __init__(self, app, on_exit):
        super().__init__(style=Pack(direction=COLUMN))
        self.app = app
        db_path = str(app.paths.data) + '/my.db'
        if not os.path.exists(db_path):
            open(db_path, 'w').close()
        self.db_conn = sqlite3.connect(db_path)
        db_cursor = self.db_conn.cursor()
        db_cursor.execute("CREATE TABLE IF NOT EXISTS my_table (key TEXT PRIMARY KEY, value TEXT)")
        self.db_conn.commit()

        self.on_exit = on_exit
        self.table = toga.Table(
            headings=['name', 'phone_number'],
            data=self.load_table(),
            style=Pack(flex=1),
            multiple_select=True
        )
        self.key_input = toga.TextInput(style=Pack(flex=1))
        self.value_input = toga.TextInput(style=Pack(flex=1))

        self.scroll_container = toga.ScrollContainer(style=Pack(flex=1), horizontal=True)
        self.scroll_container.content = self.table

        key_box = toga.Box(style=Pack(direction=ROW, padding=5))
        key_box.add(toga.Label(
            "Name: ",
            style=Pack(padding=(0, 5))
        ))
        key_box.add(self.key_input)

        value_box = toga.Box(style=Pack(direction=ROW, padding=5))
        value_box.add(toga.Label(
            "PhoneNumber: ",
            style=Pack(padding=(0, 5))
        ))
        value_box.add(self.value_input)

        self.add(toga.Button(
            'exit',
            on_press=self.exit,
            style=Pack(padding=5)
        ))
        self.add(key_box)
        self.add(value_box)

        button_box = toga.Box(style=Pack(direction=ROW, padding=5))
        button_box.add(toga.Button(
            "insert",
            on_press=self.insert_line,
            style=Pack(padding=5)
        ))
        button_box.add(toga.Button(
            'delete',
            on_press=self.delete_lines,
            style=Pack(padding=5)
        ))
        button_box.add(toga.Button(
            'clear',
            on_press=self.clear_table,
            style=Pack(padding=5)
        ))
        self.add(button_box)
        self.add(self.scroll_container)

    def __del__(self):
        self.db_conn.close()

    def exit(self, widget):
        self.on_exit()

    def refresh_table(self):
        self.table.data = self.load_table()
        self.scroll_container.refresh_sublayouts()
    
    def delete_lines(self, widget):
        def _delete_lines(dialog, return_value):
            if not return_value:
                return
            db_cursor = self.db_conn.cursor()
            for row in self.table.selection:
                db_cursor.execute(f"DELETE FROM my_table WHERE key = '{row.name}'")
            self.db_conn.commit()
            self.refresh_table()
            if self.table.selection is not None:
                self.table.selection.clear()

        if self.table.selection:
            self.app.main_window.confirm_dialog(
                'Confirm Deletion', 'Delete the seleted rows for the table?',
                _delete_lines)
            
    def load_table(self):
        db_cursor = self.db_conn.cursor()
        db_cursor.execute("SELECT * FROM my_table")
        return db_cursor.fetchall()
    
    def insert_line(self, widget):
        if self.key_input.value and self.value_input.value:
            try:
                db_cursor = self.db_conn.cursor()
                db_cursor.execute(f"SELECT * FROM my_table WHERE key = '{self.key_input.value}'")
                data = db_cursor.fetchone()
                if data:
                    db_cursor.execute(f"UPDATE my_table SET value = '{self.value_input.value}' WHERE key = '{self.key_input.value}'")
                else:
                    db_cursor.execute(f"INSERT INTO my_table (key, value) VALUES ('{self.key_input.value}', '{self.value_input.value}')")
                self.db_conn.commit()
            except Exception as e:
                print(str(e))
            self.refresh_table()
    
    def clear_table(self, widget):
        def _clear_table(dialog, return_value):
            if not return_value:
                return
            db_cursor = self.db_conn.cursor()
            db_cursor.execute("DELETE FROM my_table")
            self.db_conn.commit()
            self.refresh_table()

        self.app.main_window.confirm_dialog(
            'Confirm Clear', 'clear the table?',
            _clear_table)

class xldb(toga.App):

    def startup(self):
        self.main_box = TableBox(self, self.return_to_main_window)
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = self.main_box
        self.main_window.show()
    
    def return_to_main_window(self):
        self.main_window.content = self.main_box

def main():
    return xldb()
