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
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Task TEXT NOT NULL,
                    Date TEXT NOT NULL
                )
            """)
            db.commit()

    @staticmethod
    def read_database():
        with sqlite3.connect(db_path) as db:
            return pd.read_sql_query("SELECT Task, Date FROM tasks", db).values.tolist()

    @staticmethod
    def insert_into_database(values):
        with sqlite3.connect(db_path) as db:
            db.execute("INSERT INTO tasks (Task, Date) VALUES (?, ?)", values)
            db.commit()

    @staticmethod
    def delete_task_from_database(task):
        with sqlite3.connect(db_path) as db:
            db.execute("DELETE FROM tasks WHERE Task = ?", (task,))
            db.commit()

    @staticmethod
    def update_task_in_database(old_task, new_task):
        with sqlite3.connect(db_path) as db:
            db.execute("UPDATE tasks SET Task = ? WHERE Task = ?", (new_task, old_task))
            db.commit()

def create_form_container(add_task_callback):
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
                    hint_style=TextStyle(size=11, color="black"),
                ),
                IconButton(
                    content=Text("Add Task"),
                    width=180,
                    height=44,
                    style=ButtonStyle(
                        bgcolor={"": "black"},
                        shape={"": RoundedRectangleBorder(radius=8)},
                    ),
                    on_click=add_task_callback,
                ),
            ],
        ),
    )

def create_task_container(task, date, delete_callback, update_callback):
    def show_icons(e):
        icons_row = e.control.content.controls[1]
        opacity = 1 if e.data == "true" else 0
        icons_row.controls[0].opacity = opacity
        icons_row.controls[1].opacity = opacity
        icons_row.update()

    # Pasamos el task_container como dato al IconButton para facilitar el acceso
    task_container = Container(
        width=280,
        height=60,
        border=border.all(0.85, "white54"),
        border_radius=8,
        on_hover=show_icons,
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
                        Text(value=task, size=10, overflow=TextOverflow.FADE),
                        Text(value=date, size=9, color="white54"),
                    ],
                ),
                Row(
                    spacing=0,
                    alignment=MainAxisAlignment.END,
                    controls=[
                        IconButton(
                            icon=icons.DELETE_ROUNDED,
                            width=30,
                            icon_size=18,
                            icon_color="red700",
                            opacity=0,
                            animate_opacity=200,
                            on_click=lambda e: delete_callback(e, task_container),
                        ),
                        IconButton(
                            icon=icons.EDIT_ROUNDED,
                            width=30,
                            icon_size=18,
                            icon_color="white70",
                            opacity=0,
                            animate_opacity=200,
                            on_click=lambda e: update_callback(e, task_container),
                        ),
                    ],
                ),
            ],
        ),
    )
    return task_container

def main(page: Page):
    page.vertical_alignment = MainAxisAlignment.CENTER
    page.horizontal_alignment = CrossAxisAlignment.CENTER

    def add_task(e):
        date_time = datetime.now().strftime("%b %d, %Y  %H:%M")
        task_text = form.content.controls[0].value
        if task_text:
            Database.insert_into_database((task_text, date_time))
            main_column.controls.append(
                create_task_container(task_text, date_time, delete_task, update_task)
            )
            main_column.update()
            toggle_form(e)

    def delete_task(e, task_container):
        task_text = task_container.content.controls[0].controls[0].value
        Database.delete_task_from_database(task_text)
        task_container.height = 0
        task_container.update()
        time.sleep(0.2)
        main_column.controls.remove(task_container)
        main_column.update()

    def update_task(e, task_container):
        form.height, form.opacity = 200, 1
        form.content.controls[0].value = task_container.content.controls[0].controls[0].value
        form.content.controls[1].content.value = "Update Task"
        form.content.controls[1].on_click = lambda e: finalize_update(task_container)
        form.update()

    def finalize_update(task_container):
        old_task = task_container.content.controls[0].controls[0].value
        new_task = form.content.controls[0].value
        Database.update_task_in_database(old_task, new_task)
        task_container.content.controls[0].controls[0].value = new_task
        task_container.update()
        toggle_form(None)

    def toggle_form(e):
        if form.height != 200:
            form.height, form.opacity = 200, 1
        else:
            form.height, form.opacity = 80, 0
            form.content.controls[0].value = ""
            form.content.controls[1].content.value = "Add Task"
            form.content.controls[1].on_click = add_task
        form.update()

    main_column = Column(
        scroll=ScrollMode.HIDDEN,
        expand=True,
        alignment=MainAxisAlignment.START,
        controls=[
            Row(
                alignment=MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    Text("To-Do Items", size=18, weight=FontWeight.BOLD),
                    IconButton(
                        icons.ADD_CIRCLE_ROUNDED,
                        icon_size=18,
                        on_click=toggle_form,
                    ),
                ],
            ),
            Divider(height=8, color="white24"),
        ],
    )

    form = create_form_container(add_task)
    
    page.add(
        Container(
            width=2000,
            height=800,
            margin=-100,
            gradient=LinearGradient(
                begin=alignment.bottom_left,
                end=alignment.top_right,
                colors=[
                    "#e2e8f0", "#cbd5e1", "#94a3b8", "#64748b",
                    "#475569", "#334155", "#1e293b", "#0f172a",
                ],
            ),
            alignment=alignment.center,
            content=Column(
                alignment=MainAxisAlignment.CENTER,
                horizontal_alignment=CrossAxisAlignment.CENTER,
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
                            controls=[main_column, form],
                        ),
                    ),
                ],
            ),
        )
    )

    Database.connect_to_database()
    for task, date in Database.read_database()[::-1]:
        main_column.controls.append(create_task_container(task, date, delete_task, update_task))
    page.update()

if __name__ == "__main__":
    app(main)