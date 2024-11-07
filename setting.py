import flet as ft

class SettingsScreen(ft.UserControl):
    def __init__(self, change_theme_callback):
        super().__init__()
        self.change_theme_callback = change_theme_callback  # ฟังก์ชัน callback ที่จะใช้ในการเปลี่ยนธีม

    def build(self):
        return ft.Column([
            ft.Text("Settings", size=24, weight="bold"),
            ft.Text("Adjust your app settings here."),
            ft.Switch(label="Enable Notifications", value=True),
            ft.Row([
                ft.Text("Theme: "),
                ft.Dropdown(
                    options=[
                        ft.dropdown.Option("Light"),
                        ft.dropdown.Option("Dark"),
                        ft.dropdown.Option("System Default")
                    ],
                    label="Select Theme",
                    width=150,
                    on_change=self.on_theme_change  # เรียกใช้ฟังก์ชันเปลี่ยนธีมเมื่อมีการเปลี่ยนแปลง
                )
            ]),
        ])
    
    def on_theme_change(self, e):
        selected_theme = e.control.value
        if selected_theme == "Light":
            self.change_theme_callback(ft.ThemeMode.LIGHT)
        elif selected_theme == "Dark":
            self.change_theme_callback(ft.ThemeMode.DARK)
        else:
            self.change_theme_callback(ft.ThemeMode.SYSTEM)
