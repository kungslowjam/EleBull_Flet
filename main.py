import flet as ft
from vision_app import Countdown
from setting import SettingsScreen  # นำเข้า SettingsScreen
import time

# Paths to icon files
icon_bull = r".\icon\bull.png"
icon_auto = r".\icon\automation.png"

# Function to convert image to base64
def get_base64_icon(path):
    import base64
    with open(path, "rb") as image_file:
        base64_str = base64.b64encode(image_file.read()).decode("utf-8")
    return f"data:image/png;base64,{base64_str}"

# Convert icons to Base64
icon_bull_base64 = get_base64_icon(icon_bull)
icon_auto_base64 = get_base64_icon(icon_auto)

# Global variables for tracking unique persons
total_person_count = 0
unique_person_ids = set()
recently_detected_ids = {}
ID_EXPIRATION_TIME = 5

def update_total_person_count(track_id):
    global total_person_count, unique_person_ids, recently_detected_ids

    current_time = time.time()
    print(f"Received track_id: {track_id}")

    if track_id is not None:
        if track_id not in unique_person_ids:
            unique_person_ids.add(track_id)
            total_person_count += 1
            print(f"New person detected with ID {track_id}. Updated count: {total_person_count}")
            total_person_count_label.value = f"Total Unique Person Count: {total_person_count}"
            total_person_count_label.update()

        recently_detected_ids[track_id] = current_time

    expired_ids = [tid for tid, last_seen in recently_detected_ids.items() if current_time - last_seen > ID_EXPIRATION_TIME]
    for tid in expired_ids:
        recently_detected_ids.pop(tid, None)
        unique_person_ids.discard(tid)

def reset_total_person_count(e):
    global total_person_count, unique_person_ids
    total_person_count = 0
    unique_person_ids.clear()
    total_person_count_label.value = "Total Unique Person Count: 0"
    total_person_count_label.update()

def create_countdown_section(title):
    try:
        countdown_component = Countdown(
            update_person_count_callback=update_total_person_count,
            reset_person_count_callback=reset_total_person_count
        )

        return ft.Container(
            width=350,
            height=650,
            margin=ft.margin.all(10),
            content=ft.Column([
                ft.Row([
                    ft.Image(src=icon_bull_base64, width=36, height=36, fit=ft.ImageFit.CONTAIN),
                    ft.Text(title, size=20, weight="bold", color=ft.colors.WHITE),
                ], alignment=ft.MainAxisAlignment.START),
                countdown_component,
                countdown_component.detection_info
            ], alignment=ft.MainAxisAlignment.START),
            bgcolor=ft.colors.BLUE_GREY_900,
            padding=15,
            border_radius=ft.border_radius.all(20),
            shadow=ft.BoxShadow(spread_radius=2, blur_radius=8, color=ft.colors.BLACK12)
        )
    except Exception as e:
        print(f"Error creating countdown section for {title}: {e}")
        return ft.Text("Error loading countdown")

def main(page: ft.Page):
    page.padding = 50
    page.theme_mode = ft.ThemeMode.DARK

    global total_person_count_label
    total_person_count_label = ft.Text("Total Unique Person Count: 0", size=20, weight="bold", color=ft.colors.WHITE)

    def change_theme(theme_mode):
        page.theme_mode = theme_mode
        page.update()  # อัปเดตหน้าจอเพื่อให้การเปลี่ยนธีมมีผลทันที

    settings_screen = SettingsScreen(change_theme_callback=change_theme)

    def show_home(e):
        page.controls.clear()
        page.controls.append(main_layout)
        page.update()

    def show_settings(e):
        page.controls.clear()
        page.controls.append(settings_screen)
        page.update()

    # Create Countdown sections for each camera
    section1 = create_countdown_section("EleBull_VISION - Cam 1")
    section2 = create_countdown_section("EleBull_VISION - Cam 2")
    section3 = create_countdown_section("EleBull_VISION - Cam 3")

    main_row = ft.Row(
        controls=[section1, section2, section3],
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER
    )

    automatic_start_checkbox = ft.Row(
        controls=[
            ft.Image(src=icon_auto_base64, width=48, height=48, fit=ft.ImageFit.CONTAIN),
            ft.Checkbox(
                label="Automatic Start",
                value=False,
                on_change=lambda e: print(f"Automatic Start is {'enabled' if e.control.value else 'disabled'}")
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER
    )

    reset_button = ft.ElevatedButton(
        text="Reset Count",
        icon="history",
        on_click=reset_total_person_count
    )

    main_layout = ft.Column(
        controls=[total_person_count_label, automatic_start_checkbox, reset_button, main_row],
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

    menu_button = ft.IconButton(
        icon=ft.icons.MENU,
        on_click=lambda e: page.open(drawer)
    )

    page.appbar = ft.AppBar(title=ft.Text("EleBull_VISION"), leading=menu_button)

    page.add(main_layout)

if __name__ == '__main__':
    ft.app(target=main)
