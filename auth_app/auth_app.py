from flet import *
import pandas as pd
import sqlite3
import os
import re

db_path = os.path.join(os.path.dirname(__file__), "auth.db")
email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

class Database:
    @staticmethod
    def connect_to_database():
        with sqlite3.connect(db_path) as db:
            db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL
                )
            """)
            db.commit()

    @staticmethod
    def read_database():
        with sqlite3.connect(db_path) as db:
            df = pd.read_sql_query("SELECT email, password FROM users", db)
        return df.values.tolist()

    @staticmethod
    def insert_into_database(values):
        with sqlite3.connect(db_path) as db:
            df = pd.DataFrame([values], columns=["email", "password"])
            df.to_sql("users", db, if_exists="append", index=False)

    @staticmethod
    def check_email_exists(email):
        with sqlite3.connect(db_path) as db:
            cursor = db.cursor()
            cursor.execute("SELECT 1 FROM users WHERE email=?", (email,))
            return cursor.fetchone() is not None

    @staticmethod
    def get_user_by_email(email):
        with sqlite3.connect(db_path) as db:
            cursor = db.cursor()
            cursor.execute("SELECT email FROM users WHERE email=?", (email,))
            return cursor.fetchone()

    @staticmethod
    def delete_user_by_email(email):
        with sqlite3.connect(db_path) as db:
            db.execute("DELETE FROM users WHERE email=?", (email,))
            db.commit()

        
class ResetPassword(UserControl):
    def __init__(self, func):
        self.func = func
        super().__init__()

    def build(self):
        return Column(
            alignment="center",
            controls=[
                Text("Recover your account", size=26, weight="bold", color="eeeeee"),
                Column(
                    horizontal_alignment=CrossAxisAlignment.START,
                    spacing=5,
                    controls=[
                        Text("Enter your email to find your account", color="ffffff"),
                        Divider(height=10, color="transparent"),
                        Text("E-mail", weight="bold", color="eeeeee"),
                        TextField(
                            hint_text="Enter your e-mail",
                            prefix_icon=icons.EMAIL,
                            color="#ffffff",
                            text_size=12,
                            hint_style=TextStyle(size=12, color="#ffffff"),
                            width=310,
                            height=48,
                        ),
                        Divider(height=10, color="transparent"),
                        FilledButton(
                            text="CONFIRM",
                            style=ButtonStyle(color="#2986cc", bgcolor="white"),
                            width=300,
                            on_click=self.func
                        ),
                        FilledButton(
                            text="BACK",
                            style=ButtonStyle(
                                color="white",
                                bgcolor="transparent",
                                side={
                                    MaterialState.DEFAULT: BorderSide(1, color="white"),
                                },
                            ),
                            width=300,
                            on_click=self.func
                        ),
                    ]
                )
            ]
        )

class LogIn(UserControl):
    def __init__(self, func, func2,func3):
        self.func = func
        self.func2 = func2
        self.func3 = func3
        super().__init__()

    def build(self):
        self.email_field = TextField(
            hint_text="Enter your e-mail",
            prefix_icon=icons.EMAIL,
            color="#ffffff",
            text_size=12,
            hint_style=TextStyle(size=12, color="#ffffff"),
            width=310,
            height=48,
        )
        self.password_field = TextField(
            hint_text="Enter your password",
            password=True,
            can_reveal_password=True,
            prefix_icon=icons.KEY_OUTLINED,
            color="#ffffff",
            text_size=12,
            hint_style=TextStyle(size=12, color="#ffffff"),
            width=310,
            height=48,
        )
        
        return Column(
            horizontal_alignment="center",
            controls=[
                Text("Log In", size=28, weight=FontWeight.BOLD, color="#eeeeee"),
                Column(
                    horizontal_alignment=CrossAxisAlignment.START,
                    spacing=10,
                    controls=[
                        Text("E-mail", color="#ffffff", weight="bold"),
                        self.email_field,
                        Text("Password", color="#ffffff", weight="bold"),
                        self.password_field,
                        IconButton(
                            content=Text("Forgot password?"),
                            style=ButtonStyle(
                                bgcolor={"": "transparent"},
                                shape={"": RoundedRectangleBorder(radius=8)},
                            ),
                            on_click=self.func3
                        ),
                        FilledButton(
                            text="LOGIN",
                            style=ButtonStyle(color="#2986cc", bgcolor="white"),
                            width=300,
                            on_click=self.func
                        ),
                    ]
                ),
                Divider(height=50, color="transparent"),
                Row(
                    alignment="center",
                    controls=[
                        Text("Don't have an account?"),
                        IconButton(
                            content=Text("Sign Up", weight="bold"),
                            style=ButtonStyle(bgcolor={"": "transparent"}),
                            on_click=self.func2,
                        ),
                    ],
                ),
            ]
        )

class SignUp(UserControl):
    def __init__(self, func, func2):
        self.func = func
        self.func2 = func2
        super().__init__()

    def build(self):
        self.email_field = TextField(
            hint_text="Enter your email",
            prefix_icon=icons.EMAIL,
            color="#ffffff",
            text_size=12,
            hint_style=TextStyle(size=12, color="#ffffff"),
            width=310,
            height=48,
        )
        self.password_field = TextField(
            hint_text="Enter your password",
            password=True,
            can_reveal_password=True,
            prefix_icon=icons.KEY_OUTLINED,
            color="#ffffff",
            text_size=12,
            hint_style=TextStyle(size=12, color="#ffffff"),
            width=310,
            height=48,
        )
        self.confirm_password_field = TextField(
            hint_text="Confirm password",
            password=True,
            can_reveal_password=True,
            prefix_icon=icons.KEY_OUTLINED,
            color="#ffffff",
            text_size=12,
            hint_style=TextStyle(size=12, color="#ffffff"),
            width=310,
            height=48,
        )

        return Column(
            horizontal_alignment="center",
            controls=[
                Text("Sign Up", size=28, weight=FontWeight.BOLD, color="#eeeeee"),
                Divider(height=10, color="transparent"),
                Column(
                    alignment="start",
                    controls=[
                        Text("E-mail", color="#ffffff", weight="bold"),
                        self.email_field,
                        Text("Password", color="#ffffff", weight="bold"),
                        self.password_field,
                        Text("Confirm Password", color="#ffffff", weight="bold"),
                        self.confirm_password_field,
                        Divider(height=10, color="transparent"),
                        FilledButton(
                            text="REGISTER",
                            style=ButtonStyle(color="#2986cc", bgcolor="white"),
                            width=300,
                            on_click=self.func
                        ),
                    ]
                ),
                Divider(height=0.5, color="transparent"),
                Row(
                    alignment="center",
                    controls=[
                        Text("Have an account?"),
                        IconButton(
                            content=Text("Log In", weight="bold"),
                            style=ButtonStyle(bgcolor={"": "transparent"}),
                            on_click=self.func2,
                        ),
                    ],
                ),
            ]
        )

class UserProfile(UserControl):
    def __init__(self, email, func, func2):
        self.email = email
        self.func = func
        self.func2 = func2
        super().__init__()

    def build(self):
        return Column(
            horizontal_alignment="center",
            controls=[
                Text("User Profile", size=28, weight=FontWeight.BOLD, color="#eeeeee"),
                Divider(height=20, color="transparent"),
                Text(f"Email: {self.email}", color="#ffffff", weight="bold"),
                Divider(height=20, color="transparent"),
                FilledButton(
                    text="Log Out",
                    style=ButtonStyle(color="#2986cc", bgcolor="white"),
                    width=300,
                    on_click=self.func
                ),
                FilledButton(
                    text="Delete Account",
                    style=ButtonStyle(color="white", bgcolor="red"),
                    width=300,
                    on_click=self.func2
                ),
            ]
        )

def main(page: Page):
    page.title = "App"
    page.window_width = "800"
    page.window_height = "600"
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"
    page.bgcolor = "#6fa8dc"

    def changeSIPSUP(e):
        if main_container.content.controls[0] == LIN:
            main_container.content.controls.append(SUP)
            main_container.content.controls.pop(0)
            main_container.update()
        else:
            main_container.content.controls.append(LIN)
            main_container.content.controls.pop(0)
            main_container.update()

    def changeRP(e):
        main_container.content.controls.append(RP)
        main_container.content.controls.pop(0)
        main_container.update()

    def register_user(e):
        email = SUP.email_field.value
        password = SUP.password_field.value
        confirm_password = SUP.confirm_password_field.value

        if not email or not password or not confirm_password:
            page.snack_bar = SnackBar(Text("All fields are required!"))
            page.snack_bar.open = True
            page.update()
            return
        elif not re.match(email_pattern, email):
            page.snack_bar = SnackBar(Text("Invalid email format!"))
            page.snack_bar.open = True
            page.update()
            return
        elif password != confirm_password:
            page.snack_bar = SnackBar(Text("Passwords do not match!"))
            page.snack_bar.open = True
            page.update()
            return
        elif Database.check_email_exists(email):
            page.snack_bar = SnackBar(Text("Email already exists. Please log in."))
            page.snack_bar.open = True
            page.update()
            return
        else:
            Database.insert_into_database((email, password))
            page.snack_bar = SnackBar(Text("Registration successful. Please log in."))
            page.snack_bar.open = True
            page.update()
            changeSIPSUP(e)

    def login_user(e):
        email = LIN.email_field.value
        password = LIN.password_field.value

        # Validación de campos vacíos
        if not email or not password:
            page.snack_bar = SnackBar(Text("All fields are required!"))
            page.snack_bar.open = True
            page.update()
            return
        elif not re.match(email_pattern, email):
            page.snack_bar = SnackBar(Text("Invalid email format!"))
            page.snack_bar.open = True
            page.update()
            return

        # Verificación de credenciales
        user = Database.get_user_by_email(email)
        if user and user[0] == email:
            page.snack_bar = SnackBar(Text("Login successful."))
            page.snack_bar.open = True
            page.update()
            show_user_profile(email)
        else:
            page.snack_bar = SnackBar(Text("Invalid email or password."))
            page.snack_bar.open = True
            page.update()

    def show_user_profile(email):
        def logout(e):
            changeSIPSUP(e)

        def delete_account(e):
            Database.delete_user_by_email(email)
            page.snack_bar = SnackBar(Text("Account deleted successfully."))
            page.snack_bar.open = True
            page.update()
            changeSIPSUP(e)

        UP = UserProfile(email, logout, delete_account)
        main_container.content.controls.append(UP)
        main_container.content.controls.pop(0)
        main_container.update()

    LIN = LogIn(login_user,changeSIPSUP, changeRP)
    SUP = SignUp(register_user,changeSIPSUP)
    RP = ResetPassword(changeSIPSUP)

    main_container = Container(
        width=350,
        height=500,
        opacity=1,
        bgcolor="#76a5af",
        border_radius=5,
        gradient=LinearGradient(
            begin=alignment.top_center,
            end=alignment.bottom_center,
            colors=["#2986cc", "#6fa8dc"],
        ),
        shadow=BoxShadow(
            spread_radius=1,
            blur_radius=5,
            color="#000000"
        ),
        padding=padding.only(top=40, left=20, right=20),
        content=Column(
            controls=[
                LIN,
            ]
        )
    )

    page.add(main_container)
    page.update()

    # Ensure the database and table are created
    Database.connect_to_database()

if __name__ == "__main__":
    app(target=main)
