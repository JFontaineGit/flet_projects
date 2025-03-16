import flet as ft
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

class AuthApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.setup_page()
        self.setup_ui()
        self.add_to_page()

    def setup_page(self):
        self.page.title = "App"
        self.page.window_width = 800
        self.page.window_height = 600
        self.page.horizontal_alignment = "center"
        self.page.vertical_alignment = "center"
        self.page.bgcolor = "#6fa8dc"

    def setup_ui(self):
        # Componente de recuperación de contraseña
        self.reset_password_content = ft.Column(
            alignment="center",
            controls=[
                ft.Text("Recover your account", size=26, weight="bold", color="eeeeee"),
                ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                    spacing=5,
                    controls=[
                        ft.Text("Enter your email to find your account", color="ffffff"),
                        ft.Divider(height=10, color="transparent"),
                        ft.Text("E-mail", weight="bold", color="eeeeee"),
                        ft.TextField(
                            hint_text="Enter your e-mail",
                            prefix_icon=ft.icons.EMAIL,
                            color="#ffffff",
                            text_size=12,
                            hint_style=ft.TextStyle(size=12, color="#ffffff"),
                            width=310,
                            height=48,
                        ),
                        ft.Divider(height=10, color="transparent"),
                        ft.FilledButton(
                            text="CONFIRM",
                            style=ft.ButtonStyle(color="#2986cc", bgcolor="white"),
                            width=300,
                            on_click=self.changeRP
                        ),
                        ft.FilledButton(
                            text="BACK",
                            style=ft.ButtonStyle(
                                color="white",
                                bgcolor="transparent"
                            ),
                            width=300,
                            on_click=self.changeSIPSUP
                        ),
                    ]
                )
            ]
        )

        # Componente de inicio de sesión
        self.login_email_field = ft.TextField(
            hint_text="Enter your e-mail",
            prefix_icon=ft.icons.EMAIL,
            color="#ffffff",
            text_size=12,
            hint_style=ft.TextStyle(size=12, color="#ffffff"),
            width=310,
            height=48,
        )
        self.login_password_field = ft.TextField(
            hint_text="Enter your password",
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.icons.KEY_OUTLINED,
            color="#ffffff",
            text_size=12,
            hint_style=ft.TextStyle(size=12, color="#ffffff"),
            width=310,
            height=48,
        )
        self.login_content = ft.Column(
            horizontal_alignment="center",
            controls=[
                ft.Text("Log In", size=28, weight=ft.FontWeight.BOLD, color="#eeeeee"),
                ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                    spacing=10,
                    controls=[
                        ft.Text("E-mail", color="#ffffff", weight="bold"),
                        self.login_email_field,
                        ft.Text("Password", color="#ffffff", weight="bold"),
                        self.login_password_field,
                        ft.IconButton(
                            content=ft.Text("Forgot password?"),
                            style=ft.ButtonStyle(
                                bgcolor={"": "transparent"},
                                shape={"": ft.RoundedRectangleBorder(radius=8)},
                            ),
                            on_click=self.changeRP
                        ),
                        ft.FilledButton(
                            text="LOGIN",
                            style=ft.ButtonStyle(color="#2986cc", bgcolor="white"),
                            width=300,
                            on_click=self.login_user
                        ),
                    ]
                ),
                ft.Divider(height=50, color="transparent"),
                ft.Row(
                    alignment="center",
                    controls=[
                        ft.Text("Don't have an account?"),
                        ft.IconButton(
                            content=ft.Text("Sign Up", weight="bold"),
                            style=ft.ButtonStyle(bgcolor={"": "transparent"}),
                            on_click=self.changeSIPSUP,
                        ),
                    ],
                ),
            ]
        )

        # Componente de registro
        self.signup_email_field = ft.TextField(
            hint_text="Enter your email",
            prefix_icon=ft.icons.EMAIL,
            color="#ffffff",
            text_size=12,
            hint_style=ft.TextStyle(size=12, color="#ffffff"),
            width=310,
            height=48,
        )
        self.signup_password_field = ft.TextField(
            hint_text="Enter your password",
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.icons.KEY_OUTLINED,
            color="#ffffff",
            text_size=12,
            hint_style=ft.TextStyle(size=12, color="#ffffff"),
            width=310,
            height=48,
        )
        self.signup_confirm_password_field = ft.TextField(
            hint_text="Confirm password",
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.icons.KEY_OUTLINED,
            color="#ffffff",
            text_size=12,
            hint_style=ft.TextStyle(size=12, color="#ffffff"),
            width=310,
            height=48,
        )
        self.signup_content = ft.Column(
            horizontal_alignment="center",
            controls=[
                ft.Text("Sign Up", size=28, weight=ft.FontWeight.BOLD, color="#eeeeee"),
                ft.Divider(height=10, color="transparent"),
                ft.Column(
                    alignment="start",
                    controls=[
                        ft.Text("E-mail", color="#ffffff", weight="bold"),
                        self.signup_email_field,
                        ft.Text("Password", color="#ffffff", weight="bold"),
                        self.signup_password_field,
                        ft.Text("Confirm Password", color="#ffffff", weight="bold"),
                        self.signup_confirm_password_field,
                        ft.Divider(height=10, color="transparent"),
                        ft.FilledButton(
                            text="REGISTER",
                            style=ft.ButtonStyle(color="#2986cc", bgcolor="white"),
                            width=300,
                            on_click=self.register_user
                        ),
                    ]
                ),
                ft.Divider(height=0.5, color="transparent"),
                ft.Row(
                    alignment="center",
                    controls=[
                        ft.Text("Have an account?"),
                        ft.IconButton(
                            content=ft.Text("Log In", weight="bold"),
                            style=ft.ButtonStyle(bgcolor={"": "transparent"}),
                            on_click=self.changeSIPSUP,
                        ),
                    ],
                ),
            ]
        )

        self.user_profile_content = lambda email: ft.Column(
            horizontal_alignment="center",
            controls=[
                ft.Text("User Profile", size=28, weight=ft.FontWeight.BOLD, color="#eeeeee"),
                ft.Divider(height=20, color="transparent"),
                ft.Text(f"Email: {email}", color="#ffffff", weight="bold"),
                ft.Divider(height=20, color="transparent"),
                ft.FilledButton(
                    text="Log Out",
                    style=ft.ButtonStyle(color="#2986cc", bgcolor="white"),
                    width=300,
                    on_click=self.changeSIPSUP
                ),
                ft.FilledButton(
                    text="Delete Account",
                    style=ft.ButtonStyle(color="white", bgcolor="red"),
                    width=300,
                    on_click=lambda e: self.delete_account(email)
                ),
            ]
        )

    def add_to_page(self):
        self.main_container = ft.Container(
            width=350,
            height=500,
            opacity=1,
            bgcolor="#76a5af",
            border_radius=5,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_center,
                end=ft.alignment.bottom_center,
                colors=["#2986cc", "#6fa8dc"],
            ),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=5,
                color="#000000"
            ),
            padding=ft.padding.only(top=40, left=20, right=20),
            content=ft.Column(
                controls=[
                    self.login_content
                ]
            )
        )
        self.page.add(self.main_container)
        self.page.update()

    def changeSIPSUP(self, e):
        if isinstance(self.main_container.content.controls[0], ft.Column) and len(self.main_container.content.controls) == 1:
            if self.login_content in self.main_container.content.controls:
                self.main_container.content.controls[0] = self.signup_content
            else:
                self.main_container.content.controls[0] = self.login_content
            self.main_container.update()
        elif isinstance(self.main_container.content.controls[0], ft.Column) and len(self.main_container.content.controls) > 1:
            self.main_container.content.controls[0] = self.login_content
            self.main_container.update()

    def changeRP(self, e):
        self.main_container.content.controls[0] = self.reset_password_content
        self.main_container.update()

    def register_user(self, e):
        email = self.signup_email_field.value
        password = self.signup_password_field.value
        confirm_password = self.signup_confirm_password_field.value

        if not email or not password or not confirm_password:
            self.page.snack_bar = ft.SnackBar(ft.Text("All fields are required!"))
            self.page.snack_bar.open = True
            self.page.update()
            return
        elif not re.match(email_pattern, email):
            self.page.snack_bar = ft.SnackBar(ft.Text("Invalid email format!"))
            self.page.snack_bar.open = True
            self.page.update()
            return
        elif password != confirm_password:
            self.page.snack_bar = ft.SnackBar(ft.Text("Passwords do not match!"))
            self.page.snack_bar.open = True
            self.page.update()
            return
        elif Database.check_email_exists(email):
            self.page.snack_bar = ft.SnackBar(ft.Text("Email already exists. Please log in."))
            self.page.snack_bar.open = True
            self.page.update()
            return
        else:
            Database.insert_into_database((email, password))
            self.page.snack_bar = ft.SnackBar(ft.Text("Registration successful. Please log in."))
            self.page.snack_bar.open = True
            self.page.update()
            self.changeSIPSUP(e)

    def login_user(self, e):
        email = self.login_email_field.value
        password = self.login_password_field.value

        if not email or not password:
            self.page.snack_bar = ft.SnackBar(ft.Text("All fields are required!"))
            self.page.snack_bar.open = True
            self.page.update()
            return
        elif not re.match(email_pattern, email):
            self.page.snack_bar = ft.SnackBar(ft.Text("Invalid email format!"))
            self.page.snack_bar.open = True
            self.page.update()
            return

        user = Database.get_user_by_email(email)
        if user and user[0] == email:
            self.page.snack_bar = ft.SnackBar(ft.Text("Login successful."))
            self.page.snack_bar.open = True
            self.page.update()
            self.show_user_profile(email)
        else:
            self.page.snack_bar = ft.SnackBar(ft.Text("Invalid email or password."))
            self.page.snack_bar.open = True
            self.page.update()

    def show_user_profile(self, email):
        self.main_container.content.controls[0] = self.user_profile_content(email)
        self.main_container.update()

    def delete_account(self, email):
        Database.delete_user_by_email(email)
        self.page.snack_bar = ft.SnackBar(ft.Text("Account deleted successfully."))
        self.page.snack_bar.open = True
        self.page.update()
        self.changeSIPSUP(None)

def main(page: ft.Page):
    app = AuthApp(page)
    Database.connect_to_database()

if __name__ == "__main__":
    ft.app(target=main)