from datetime import datetime
from flet import *
import pandas as pd
import sqlite3
import time
import os

db_path = os.path.join(os.path.dirname(__file__), "tm.db")

class Database:
    @staticmethod
    def connect_to_database():
        
        with sqlite3.connect(db_path) as db:
            db.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY,
                    Task VARCHAR(255) NOT NULL,
                    Date VARCHAR(255) NOT NULL
                )
            """)
            db.commit()

    @staticmethod
    def read_database():
        with sqlite3.connect(db_path) as db:
            df = pd.read_sql_query("SELECT Task, Date FROM tasks", db)
        return df.values.tolist()

    @staticmethod
    def insert_into_database(values):
        with sqlite3.connect(db_path) as db:
            df = pd.DataFrame([values], columns=["Task", "Date"])
            df.to_sql("tasks", db, if_exists="append", index=False)

    @staticmethod
    def delete_task_from_database(value):
        with sqlite3.connect(db_path) as db:
            db.execute("DELETE FROM tasks WHERE Task=?", value)
            db.commit()

    @staticmethod
    def update_task_in_database(value):
        with sqlite3.connect(db_path) as db:
            db.execute("UPDATE tasks SET Task=? WHERE Task=?", value)
            db.commit()

class FormContainer(UserControl):
    def __init__(self, func):
        self.func = func
        super().__init__()

    def build(self):
        return Container(
            width=280,
            height=80,
            opacity=0,
            gradient=LinearGradient(
                begin=alignment.bottom_left,
                end=alignment.top_right,
                colors=["bluegrey300", "bluegrey400", "bluegrey500", "bluegrey700"],
            ),
            border_radius=40,
            margin=margin.only(left=-20, right=-20),
            animate=animation.Animation(400, "decelerate"),
            animate_opacity=200,
            clip_behavior=ClipBehavior.HARD_EDGE,
            padding=padding.only(top=45, bottom=45),
            content=Column(
                horizontal_alignment=CrossAxisAlignment.CENTER,
                controls=[
                    TextField(
                        height=48,
                        width=255,
                        text_size=12,
                        color="black",
                        border_radius=8,
                        bgcolor="#f0f3f6",
                        border_color="transparent",
                        filled=True,
                        cursor_color="black",
                        cursor_width=1,
                        hint_text="Description...",
                        hint_style=TextStyle(
                            size=11,
                            color="black",
                        ),
                    ),
                    IconButton(
                        content=Text("Add Task"),
                        width=180,
                        height=44,
                        style=ButtonStyle(
                            bgcolor={"": "black"},
                            shape={"": RoundedRectangleBorder(radius=8)},
                        ),
                        on_click=self.func,
                    ),
                ],
            ),
        )

class CreateTask(UserControl):
    def __init__(self, task: str, date: str, func1, func2):
        self.task = task
        self.date = date
        self.func1 = func1
        self.func2 = func2
        super().__init__()

    def ShowIcons(self, e):
        if e.data == "true":
            (
                e.control.content.controls[1].controls[0].opacity,
                e.control.content.controls[1].controls[1].opacity,
            ) = (1, 1)

            e.control.content.update()
        else:
            (
                e.control.content.controls[1].controls[0].opacity,
                e.control.content.controls[1].controls[1].opacity,
            ) = (0, 0)

            e.control.content.update()

    def GetContainerInstnace(self, e):
        return self

    def TaskDeleteEdit(self, name, color, func):
        return IconButton(
            icon=name,
            width=30,
            icon_size=18,
            icon_color=color,
            opacity=0,
            animate_opacity=200,
            on_click=lambda e: func(self.GetContainerInstnace(e)),
        )

    def build(self):
        return Container(
            width=280,
            height=60,
            border=border.all(0.85, "white54"),
            border_radius=8,
            on_hover=lambda e: self.ShowIcons(e),
            clip_behavior=ClipBehavior.HARD_EDGE,
            padding=10,
            animate=200,
            content=Row(
                alignment=MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    Column(
                        spacing=1,
                        alignment=MainAxisAlignment.CENTER,
                        controls=[
                            Text(value=self.task, size=10, overflow="fade"),
                            Text(value=self.date, size=9, color="white54"),
                        ],
                    ),
                    Row(
                        spacing=0,
                        alignment=MainAxisAlignment.END,
                        controls=[
                            self.TaskDeleteEdit(
                                icons.DELETE_ROUNDED,
                                "red700",
                                self.func1,
                            ),
                            self.TaskDeleteEdit(
                                icons.EDIT_ROUNDED,
                                "white70",
                                self.func2,
                            ),
                        ],
                    ),
                ],
            ),
        )

def main(page: Page):
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"

    def AddTaskToScreen(e):
        dateTime = datetime.now().strftime("%b %d, %Y  %H:%M")
        Database.insert_into_database((form.content.controls[0].value, dateTime))

        if form.content.controls[0].value:
            _main_column_.controls.append(
                CreateTask(
                    form.content.controls[0].value,
                    dateTime,
                    DeleteFunction,
                    UpdateFunction,
                )
            )
            _main_column_.update()
            CreateToDoTask(e)
        else:
            pass

    def DeleteFunction(e):
        Database.delete_task_from_database(
            (e.controls[0].content.controls[0].controls[0].value,)
        )

        e.controls[0].height = 0
        e.controls[0].update()
        time.sleep(0.2)
        _main_column_.controls.remove(e)
        _main_column_.update()

    def UpdateFunction(e):
        form.height, form.opacity = 200, 1

        (
            form.content.controls[0].value,
            form.content.controls[1].content.value,
            form.content.controls[1].on_click,
        ) = (
            e.controls[0].content.controls[0].controls[0].value,
            "Update Task",
            lambda _: FinalizeUpdate(e),
        )
        form.update()

    def FinalizeUpdate(e):
        Database.update_task_in_database(
            (
                form.content.controls[0].value,
                e.controls[0].content.controls[0].controls[0].value,
            ),
        )

        e.controls[0].content.controls[0].controls[0].value = form.content.controls[
            0
        ].value
        e.controls[0].content.update()
        CreateToDoTask(e)

    def CreateToDoTask(e):
        if form.height != 200:
            form.height, form.opacity = 200, 1
            form.update()
        else:
            form.height, form.opacity = 80, 0
            form.content.controls[0].value = None
            form.content.controls[1].content.value = "Add Task"
            form.content.controls[1].on_click = lambda e: AddTaskToScreen(e)
            form.update()

    _main_column_ = Column(
        scroll="hidden",
        expand=True,
        alignment=MainAxisAlignment.START,
        controls=[
            Row(
                alignment=MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    Text(
                        "To-Do Items",
                        size=18,
                        weight="bold",
                    ),
                    IconButton(
                        icons.ADD_CIRCLE_ROUNDED,
                        icon_size=18,
                        on_click=lambda e: CreateToDoTask(e),
                    ),
                ],
            ),
            Divider(height=8, color="white24"),
        ],
    )

    page.add(
        Container(
            width=1500,
            height=900,
            margin=-10,
            gradient=LinearGradient(
                begin=alignment.bottom_left,
                end=alignment.top_right,
                colors=[
                    "#e2e8f0",
                    "#cbd5e1",
                    "#94a3b8",
                    "#64748b",
                    "#475569",
                    "#334155",
                    "#1e293b",
                    "#0f172a",
                ],
            ),
            alignment=alignment.center,
            padding=padding.only(right=110),
            content=Row(
                alignment=MainAxisAlignment.END,
                vertical_alignment=CrossAxisAlignment.CENTER,
                controls=[
                    Container(
                        width=280,
                        height=600,
                        bgcolor="#0f0f0f",
                        border=border.all(0.5, "white70"),
                        border_radius=40,
                        padding=padding.only(top=35, left=20, right=20),
                        clip_behavior=ClipBehavior.HARD_EDGE,
                        content=Column(
                            alignment=MainAxisAlignment.SPACE_BETWEEN,
                            expand=True,
                            controls=[
                                _main_column_,
                                FormContainer(lambda e: AddTaskToScreen(e)),
                            ],
                        ),
                    ),
                ],
            ),
        )
    )
    page.update()

    form = page.controls[0].content.controls[0].content.controls[1].controls[0]
    
    Database.connect_to_database()

    for task in Database.read_database()[::-1]:
        _main_column_.controls.append(
            CreateTask(
                task[0],
                task[1],
                DeleteFunction,
                UpdateFunction,
            )
        )
    _main_column_.update()

if __name__ == "__main__":
    app(target=main)