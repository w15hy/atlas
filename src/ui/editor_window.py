import flet as ft


def main_page(page: ft.Page):

    page.title = "ATLAS"
    page.padding = 0
    page.spacing = 0

    c1 = ft.Container(
        content=ft.Text("C1 (3/4)"),
        bgcolor="blue",
        expand=3,
        width=float("inf"),
    )

    c2 = ft.Container(
        content=ft.Text("C2 (1/4)"),
        bgcolor="green",
        expand=1,  # 👈 1 parte
        width=float("inf"),
    )

    page.add(
        ft.Column(
            spacing=0,
            controls=[c1, c2],
            expand=True,
        )
    )
