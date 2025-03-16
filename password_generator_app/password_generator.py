import flet as ft
import secrets
import string
import pyperclip

random = secrets.SystemRandom()
contraseñas = []

class PasswordGeneratorApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.setup_page()
        self.setup_ui()
        self.add_to_page()

    def setup_page(self):
        self.page.title = "Password Generator"
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.horizontal_alignment = ft.MainAxisAlignment.CENTER
        self.page.window_resizable = False
        self.page.window_maximizable = False
        self.page.window_width = 330

    def setup_ui(self):
        self.title_container = ft.Container(
            width=275,
            height=60,
            content=ft.Column(
                spacing=5,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text(
                        "Password Generator",
                        size=25,
                        weight=ft.FontWeight.BOLD,
                    ),
                ],
            ),
        )

        self.text_field = ft.TextField(
            border=ft.InputBorder.UNDERLINE,
            width=205,
            read_only=True,
            hint_text="Your Password",
        )
        self.copy_button = ft.IconButton(
            icon=ft.icons.CONTENT_COPY,
            disabled=True,
            on_click=self.copy_function
        )

        self.buttons_row = ft.Row(
            [
                ft.FilledButton("12", on_click=lambda e: self.text_field_value(12), style=ft.ButtonStyle(shape=ft.CircleBorder(), padding=30)),
                ft.FilledButton("16", on_click=lambda e: self.text_field_value(16), style=ft.ButtonStyle(shape=ft.CircleBorder(), padding=30)),
                ft.FilledButton("20", on_click=lambda e: self.text_field_value(20), style=ft.ButtonStyle(shape=ft.CircleBorder(), padding=30)),
            ],
        )

        self.main_container = ft.Container(
            width=275,
            height=200,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        [
                            self.text_field,
                            self.copy_button
                        ],
                    ),
                    ft.Divider(height=20, color="transparent"),
                    self.buttons_row
                ],
            ),
        )

    def add_to_page(self):
        self.page.add(
            ft.Container(
                width=300,
                height=600,
                padding=20,
                border_radius=40,
                border=ft.border.all(1, ft.colors.WHITE),
                content=ft.Column(
                    controls=[
                        ft.Divider(height=20, color="transparent"),
                        self.title_container,
                        ft.Divider(height=30, color="transparent"),
                        self.main_container
                    ]
                )
            )
        )
        self.page.update()

    def text_field_value(self, longitud):
        self.password(longitud)
        self.copy_button.disabled = False
        self.copy_button.update()
        self.text_field.value = contraseñas[0]
        self.text_field.update()

    def password(self, longitud):
        caract_esp = "#$%&'()*+-/:;<=>?@[\]^_`{|}~"
        contra_seg = string.ascii_letters + string.digits + caract_esp
        while True:
            it_seg = ''.join(random.choice(contra_seg) for _ in range(longitud))
            if (any(i.islower() for i in it_seg) and
                any(i.isupper() for i in it_seg) and
                sum(i.isdigit() for i in it_seg) >= 2 and
                any(i in caract_esp for i in it_seg)):
                if contraseñas:
                    contraseñas.pop()
                contraseñas.append(it_seg)
                break

    def copy_function(self, e):
        pyperclip.copy(contraseñas[0])
        self.page.snack_bar = ft.SnackBar(ft.Text("Contraseña copiada al portapapeles"))
        self.page.snack_bar.open = True
        self.page.update()

def main(page: ft.Page):
    PasswordGeneratorApp(page)

if __name__ == "__main__":
    ft.app(target=main)