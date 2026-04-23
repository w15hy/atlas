import flet as ft


def main_page(page: ft.Page):
    page.title = "Editor + Consola"
    page.window_width = 1000
    page.window_height = 700
    page.padding = 0
    page.spacing = 0

    editor = ft.TextField(
        multiline=True,
        expand=True,
        min_lines=20,
        border=ft.InputBorder.NONE,
        hint_text="Escribe código aquí...",
        text_size=16,
    )

    consola = ft.TextField(
        multiline=True,
        expand=True,
        min_lines=8,
        border=ft.InputBorder.NONE,
        value=">>> Consola lista...\n",
        text_style=ft.TextStyle(font_family="monospace"),
    )

    layout = ft.Column(
        expand=True,
        spacing=0,
        controls=[
            ft.Container(content=editor, expand=3, padding=10),
            ft.Divider(height=1),
            ft.Container(content=consola, expand=1, padding=10),
        ],
    )

    page.add(layout)
