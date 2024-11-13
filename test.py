import flet as ft

def main(page: ft.Page):
    page.title = "Calculator"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    result = ft.Text(value="0", size=40, weight=ft.FontWeight.BOLD)

    def button_click(e):
        if e.control.text == "=":
            try:
                result.value = str(eval(result.value))
            except Exception as ex:
                result.value = "Error"
        elif e.control.text == "C":
            result.value = "0"
        else:
            if result.value == "0":
                result.value = ""
            result.value += e.control.text
        page.update()

    buttons = [
        ["7", "8", "9", "/"],
        ["4", "5", "6", "*"],
        ["1", "2", "3", "-"],
        ["C", "0", "=", "+"]
    ]

    for row in buttons:
        row_container = ft.Row()
        for button_text in row:
            button = ft.ElevatedButton(text=button_text, on_click=button_click)
            row_container.controls.append(button)
        page.add(row_container)

    page.add(result)

ft.app(target=main)
