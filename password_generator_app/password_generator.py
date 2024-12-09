from flet import *
import secrets
import string
import pyperclip

random = secrets.SystemRandom()
contraseñas = []

class TitleContainer(UserControl):
    def build(self):
        return Container(
            width=275,
            height=60,
            content=Column(
                spacing=5,
                horizontal_alignment=CrossAxisAlignment.CENTER,
                controls=[
                    Text(
                        "Password Generator",
                        size=25,
                        weight=FontWeight.BOLD,
                    ),
                ],
            ),
        )

class MainContainer(UserControl):
    def __init__(self, funcion, funcion2):
        super().__init__()
        self.funcion = funcion
        self.funcion2 = funcion2
        self.text_field = TextField(
            border=InputBorder.UNDERLINE,
            width=205,
            read_only=True,
            hint_text="Your Password",
        )
        self.copy_button = IconButton(
            icon=icons.CONTENT_COPY,
            disabled=True,
            on_click=funcion2
        )

    def text_field_value(self, long):
        self.funcion(long)
        self.copy_button.disabled = False
        self.copy_button.update()
        self.text_field.value = contraseñas[0]
        self.text_field.update()

    def Buttons(self) -> Control:
        return Row(
            [
                FilledButton("12", on_click=lambda e: self.text_field_value(12), style=ButtonStyle(shape=CircleBorder(), padding=30)),
                FilledButton("16", on_click=lambda e: self.text_field_value(16), style=ButtonStyle(shape=CircleBorder(), padding=30)),
                FilledButton("20", on_click=lambda e: self.text_field_value(20), style=ButtonStyle(shape=CircleBorder(), padding=30)),
            ],
        )

    def TextField(self) -> Control:
        return Row(
            [
                self.text_field,
                self.copy_button
            ],
        )

    def build(self):
        return Container(
            width=275,
            height=200,
            clip_behavior=ClipBehavior.HARD_EDGE,
            content=Column(
                horizontal_alignment=CrossAxisAlignment.CENTER,
                controls=[
                    self.TextField(),
                    Divider(height=20, color="transparent"),
                    self.Buttons()
                ],
            ),
        )

def main(page: Page):
    def password(longitud):
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

    def copy_function(e):
        pyperclip.copy(contraseñas[0])
        page.snack_bar = SnackBar(Text("Contraseña copiada al portapapeles"))
        page.snack_bar.open = True
        page.update()

    page.title = "Password Generator"
    page.vertical_alignment = MainAxisAlignment.CENTER
    page.horizontal_alignment = MainAxisAlignment.CENTER
    page.window_resizable = False
    page.window_maximizable = False
    page.window_width = 330

    main_container = Container(
        width=300,
        height=600,
        padding=20,
        border_radius=40,
        border=border.all(1, colors.WHITE),
        content=Column(
            controls=[
                Divider(height=20, color="transparent"),
                TitleContainer(),
                Divider(height=30, color="transparent"),
                MainContainer(password, copy_function)
            ]
        )
    )

    page.add(main_container)
    page.update()

if __name__ == "__main__":
    app(target=main)
