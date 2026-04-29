from flet import (TextField,
                  InputBorder,
                  Page,
                  ControlEvent)

class TextEditor():
    def __init__(self) -> None:
        super().__init__()
        self.textfield = TextField(outline=True,
                                   autofocus=True,
                                   border=InputBorder.NONE,
                                   min_lines=40,
                                   on_change=save_text)

    def save_text(self, e:ControlEvent) -> None:
        raise NotImplementedError
