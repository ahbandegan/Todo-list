from flet import *
import flet as ft
from sqlite3 import *

class SaveData:
    def __init__(self):
        self.conn = connect("identifier.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            """
                CREATE TABLE IF NOT EXISTS tasks(
                    id INTEGER NOT NULL ,
                    task TEXT,
                    complet INTEGER
                )
            """
        )

    def save(self, tasks: list[tuple[int, str, int]]):
        number = 0
        for (id, task, complet) in tasks:
            self.cursor.execute(
                """
                INSERT INTO tasks (id, task, complet) values (?,?,?)
                """,
                (id, task, complet)
            )
        self.conn.commit()

    def create(self):
        self.cursor.execute(
            """
            SELECT * FROM tasks
            """
        )
        rows = self.cursor.fetchall()
        list1 = []
        for row in rows:
            list1.append(row)
        return list1

    def delete(self):
        self.cursor.execute(
            """
                DROP TABLE tasks
            """
        )
        self.create_database()
        self.conn.commit()

    def create_database(self):
        self.cursor.execute(
            """
                CREATE TABLE IF NOT EXISTS tasks(
                    id INTEGER NOT NULL ,
                    task TEXT,
                    complet INTEGER
                )
            """
        )
        self.conn.commit()

    def change_complet(self, id, data):
        if data:
            self.cursor.execute(
                """
                UPDATE tasks
                SET complet = 1
                WHERE id = ?
                  AND complet = 0
                """, (id, )
            )
        elif not data:
            self.cursor.execute(
                """
                UPDATE tasks
                SET complet = 0
                WHERE id = ?
                  AND complet = 1
                """, (id,)
            )
        self.conn.commit()

    def last_data(self):
        self.cursor.execute(
            """
            select * from tasks
            """
        )
        rows = self.cursor.fetchall()
        number = ""
        for i in rows:
            number += str(i[0])

        return number

    def close(self):
        self.conn.commit()
        self.conn.close()


class Tasks(ft.Row):
    def __init__(self, text, number, complet: int = 0):
        super().__init__(text, number, complet)
        self.number = number
        self.text = text
        self.complet_task = complet
        self.color = ""

        if self.complet_task == 0:
            self.complet = Checkbox(value=False, data=self.number, on_change=self.change)
            self.color = "red"
        elif self.complet_task == 1:
            self.complet = Checkbox(value=True, data=self.number, on_change=self.change)
            self.color = "green"

        self.text_view = Text(
            value=self.text
        )
        self.text_Edit = TextField(
            value=self.text,
            visible=False,
            width=230
        )
        self.edit_button = IconButton(
            icon=icons.EDIT,
            on_click=self.edit,
        )
        self.save_button = IconButton(
            icon=icons.SAVE,
            visible=False,
            on_click=self.save,
        )
        self.card =Card(
            content=ft.Row(
                [
                    Container(height=15),
                    Text(f"{self.number}:", size=20),
                    self.complet,
                    self.text_view,
                    self.text_Edit,
                    self.edit_button,
                    self.save_button,
                ]
            ),
            color=self.color,
        )

        self.controls = [
            self.card,
        ]

    def save(self, e):
        self.text_view.value = self.text_Edit.value
        self.text_view.visible = True
        self.text_Edit.visible = False
        self.edit_button.visible = True
        self.save_button.visible = False
        self.update()

    def edit(self, e):
        self.text_view.visible = False
        self.text_Edit.visible = True
        self.edit_button.visible = False
        self.save_button.visible = True
        self.update()

    def trash(self, e):
        self.clean()

    def change(self, e):
        if e.control.value:
            SaveData().change_complet(e.control.data, True)
            self.card.color = "green"
        elif not e.control.value:
            SaveData().change_complet(e.control.data, False)
            self.card.color = "red"

        self.update()


class App(Column):
    def __init__(self):
        super().__init__()

        self.tsk = TextField(
            hint_text="what needs to be done?",
            text_size=18,
            multiline=True,
            width=230
        )
        self.task = Column()
        num = SaveData().last_data()
        if num != "":
            num2 = int(num[-1])
            if num2 > 0:
                self.number = num2 + 1
        elif num == "":
            self.number = 1

        SaveData().create_database()
        for (id, task, complet) in SaveData().create():
            self.task.controls.append(Tasks(task, id, complet))

        self.controls = [
            ft.Row(
                [
                    self.tsk,
                    FloatingActionButton(icon=icons.ADD, on_click=self.add_task),
                    FloatingActionButton(icon=icons.CLEAR_ALL, on_click=self.clear_task),
                ]
            ),
            self.task
        ]

    def add_task(self, e):
        if self.tsk.value != "":
            self.task.controls.append(Tasks(self.tsk.value, self.number))
            SaveData().save([(self.number, self.tsk.value, False)])
            self.tsk.value = ""
            self.number += 1

        self.update()

    def clear_task(self, e):
        self.task.controls.clear()
        self.update()

    def load_task(self, e):
        for (id, task, complet) in SaveData().create():
            self.task.controls.append(Tasks(task, id, complet))
        self.update()


def main(page: Page):

    def clear(e):
        SaveData().delete()
        page.controls.clear()
        page.add(
            App()
        )
        dialog.open = True
        page.update()

    page.window.width = 400
    page.window.height = 600
    page.scroll = True
    dialog = SnackBar(
        content=ft.Row(
            [
                Text("Data base is cleared...!")
            ]
        )
    )
    page.overlay.append(dialog)
    page.appbar = AppBar(
        title=Text("To-Do"),
        actions=[
            CupertinoButton("clear database", on_click=clear),
            Container(height=15)
        ]
    )
    page.add(
        App()
    )


if __name__ == '__main__':
    app(main)
    SaveData().close()