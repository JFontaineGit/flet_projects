from music21 import converter
from pathlib import Path
import flet as ft
import tempfile
import zipfile
import os

class MusicConverterApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.uploaded_files = []
        self.converted_files = {}
        
        self.setup_page()
        self.setup_ui()
        self.add_to_page()

    def setup_page(self):
        self.page.title = "MusicXML/MXL to MIDI Converter"
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.bgcolor = ft.colors.BLACK54
        self.page.padding = 20

    def setup_ui(self):
        self.file_picker = ft.FilePicker(on_result=self.handle_file_pick)
        
        self.upload_button = ft.ElevatedButton(
            "Select MusicXML/MXL Files",
            icon=ft.icons.FOLDER_OPEN,
            on_click=self.pick_files,
            bgcolor=ft.colors.BLUE_600,
            color=ft.colors.WHITE
        )
        
        self.file_list = ft.ListView(
            expand=True,
            spacing=10,
            padding=10,
            auto_scroll=True
        )
        
        self.convert_button = ft.ElevatedButton(
            "Convert to MIDI",
            icon=ft.icons.AUDIOTRACK,
            on_click=self.convert_files,
            bgcolor=ft.colors.GREEN_600,
            color=ft.colors.WHITE,
            disabled=True
        )
        
        self.result_text = ft.Text(value="", size=16, color=ft.colors.BLACK)
        self.download_container = ft.Column(
            controls=[],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )

    def add_to_page(self):
        self.page.overlay.append(self.file_picker)
        self.page.add(
            ft.Column(
                controls=[
                    ft.Text("MusicXML/MXL to MIDI Converter", size=24, weight=ft.FontWeight.BOLD),
                    self.upload_button,
                    ft.Container(
                        content=self.file_list,
                        height=150,
                        width=400,
                        border=ft.border.all(1, ft.colors.GREY_400),
                        border_radius=5,
                        bgcolor=ft.colors.WHITE
                    ),
                    self.convert_button,
                    self.result_text,
                    self.download_container
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20
            )
        )

    def pick_files(self, e):
        self.file_picker.pick_files(
            allow_multiple=True,
            allowed_extensions=["musicxml", "xml", "mxl"]
        )

    def handle_file_pick(self, e: ft.FilePickerResultEvent):
        if e.files:
            self.uploaded_files = [f.path for f in e.files]
            self.update_file_list()
            self.convert_button.disabled = len(self.uploaded_files) == 0
            self.result_text.value = f"{len(self.uploaded_files)} file(s) selected"
            self.download_container.controls.clear()
            self.page.update()

    def update_file_list(self):
        self.file_list.controls.clear()
        for file_path in self.uploaded_files:
            file_name = os.path.basename(file_path)
            self.file_list.controls.append(ft.Text(file_name, color=ft.colors.BLACK))
        self.page.update()

    def extract_mxl(self, mxl_path: str) -> str:
        try:
            with zipfile.ZipFile(mxl_path, 'r') as zip_ref:
                xml_files = [f for f in zip_ref.namelist() if f.endswith('.xml') and 'META-INF' not in f]
                if not xml_files:
                    raise ValueError("No XML file found in .mxl archive")
                
                temp_dir = tempfile.mkdtemp()
                xml_file = xml_files[0]
                extracted_path = os.path.join(temp_dir, xml_file)
                zip_ref.extract(xml_file, temp_dir)
                return extracted_path
        except Exception as e:
            raise RuntimeError(f"Error extracting {os.path.basename(mxl_path)}: {str(e)}")

    def convert_files(self, e):
        self.converted_files.clear()
        self.download_container.controls.clear()
        self.page.update()

        for file_path in self.uploaded_files:
            try:
                if file_path.lower().endswith('.mxl'):
                    xml_path = self.extract_mxl(file_path)
                else:
                    xml_path = file_path

                score = converter.parse(xml_path)
                output_name = f"{Path(file_path).stem}.mid"
                output_path = os.path.join(os.path.dirname(file_path), output_name)
                score.write("midi", output_path)
                self.converted_files[output_name] = output_path

                if file_path.lower().endswith('.mxl'):
                    temp_dir = os.path.dirname(xml_path)
                    for root, dirs, files in os.walk(temp_dir, topdown=False):
                        for name in files:
                            os.remove(os.path.join(root, name))
                        for name in dirs:
                            os.rmdir(os.path.join(root, name))
                    os.rmdir(temp_dir)

            except Exception as ex:
                self.result_text.value = f"Error converting {os.path.basename(file_path)}: {str(ex)}"
                self.page.update()
                return

        self.add_go_to_buttons()
        self.page.update()

    def add_go_to_buttons(self):
        for file_name, file_path in self.converted_files.items():
            # Botón para ir a la ruta del archivo convertido
            go_button = ft.ElevatedButton(
                f"Go to file",
                icon=ft.icons.FOLDER_OPEN,
                on_click=lambda e, path=file_path: self.download_file(path),
                bgcolor=ft.colors.BLUE_400,
                color=ft.colors.WHITE
            )
            self.download_container.controls.append(go_button)
            self.download_container.controls.append(ft.Text(f"Saved at: {file_path}", size=12, color=ft.colors.GREY_600)) # Ruta del archivo

    def download_file(self, file_path):
        os.startfile(os.path.dirname(file_path))
        self.result_text.value = f"File saved at: {file_path}. Folder opened if supported."
        self.page.update()

def main(page: ft.Page):
    MusicConverterApp(page)

if __name__ == "__main__":
    ft.app(target=main)