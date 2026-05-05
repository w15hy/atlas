import flet as ft


class App:
    def __init__(self, pg: ft.Page):
        super().__init__()

        self.pg = pg
        self.init_helper()

    def init_helper(self):
        self.pg.add(
            ft.Container(
                expand=True,
                bgcolor="blue",
                content=ft.Row(
                    spacing=0,
                    controls=[
                        ft.Container(bgcolor="brown", width=80),  # sidebar
                        ft.Container(bgcolor="green", expand=True),  # main screen
                    ],
                ),
            )
        )


def start():
    ft.app(target=App)


if __name__ == "__main__":
    start()
