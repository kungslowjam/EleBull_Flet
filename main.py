# main.py
import flet as ft
from vision_app import Countdown

class SettingsScreen(ft.UserControl):
    def build(self): 
        return ft.Column([ 
            ft.Text("Settings", size=16, weight="bold"), 
            ft.Text("Adjust your app settings here.")  
        ])  

def main(page: ft.Page): 
    page.padding = 50
    page.theme_mode = ft.ThemeMode.DARK
    
    settings_screen = SettingsScreen()

    def show_home(e):
        page.controls.clear()
        page.controls.append(main_layout)
        page.update()

    def show_settings(e):
        page.controls.clear()
        page.controls.append(settings_screen)
        page.update()

    # ฟังก์ชันสำหรับสร้าง Card ของ Countdown
    def create_countdown_section(title):
        return ft.Container(
            width=350,  
            height=550,  
            margin=ft.margin.all(10),
            content=ft.Column([
                ft.Text(
                    title,
                    size=20, weight="bold",
                    color=ft.colors.WHITE,
                ),
                Countdown()
            ], alignment=ft.MainAxisAlignment.START),
            bgcolor=ft.colors.BLUE_GREY_900,
            padding=15,
            border_radius=ft.border_radius.all(20),
            shadow=ft.BoxShadow(
                spread_radius=2,
                blur_radius=8,
                color=ft.colors.BLACK12
            )
        )

    # เพิ่ม Countdown Section สามตัว
    section1 = create_countdown_section("EleBull_VISION - Cam 1")
    section2 = create_countdown_section("EleBull_VISION - Cam 2")
    section3 = create_countdown_section("EleBull_VISION - Cam 3")

    # จัด Row ของ Countdown สามตัวให้อยู่ตรงกลางหน้า
    main_row = ft.Row(
        controls=[section1, section2, section3],
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER
    )
    
    # Layout หลักของหน้า
    main_layout = ft.Column(
        controls=[main_row],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )
    drawer = ft.NavigationDrawer(
        [
            ft.ListTile(title=ft.Text("Home"), on_click=show_home),
            ft.ListTile(title=ft.Text("Settings"), on_click=show_settings),
            ft.ListTile(title=ft.Text("About"), on_click=lambda e: print("About selected")),
        ]
    )
    # สร้างปุ่มเมนูและ Drawer
    menu_button = ft.IconButton(
        icon=ft.icons.MENU,
        on_click=lambda e: page.open(drawer)
    )

    page.appbar = ft.AppBar(title=ft.Text("EleBull_VISION"), leading=menu_button)
   
    
    # เริ่มต้นแสดงหน้า Home
    page.add(main_layout)

if __name__ == '__main__': 
    ft.app(target=main)
