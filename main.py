import flet as ft
from vision_app import Countdown
from setting import SettingsScreen
import json
import os
import time

# Paths to icon files
icon_bull = r".\icon\bull.png"
icon_auto = r".\icon\automation.png"
STATE_FILE = "settings.json"

# Function to convert image to base64
def get_base64_icon(path):
    import base64
    with open(path, "rb") as image_file:
        base64_str = base64.b64encode(image_file.read()).decode("utf-8")
    return f"data:image/png;base64,{base64_str}"

icon_bull_base64 = get_base64_icon(icon_bull)
icon_auto_base64 = get_base64_icon(icon_auto)

# Load the default camera and model settings from a file
def load_settings():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"cameras": [None, None, None], "models": [None, None, None]}  # Default if no settings are saved

# Save the default camera and model settings to a file
def save_settings(settings):
    with open(STATE_FILE, "w") as f:
        json.dump(settings, f)

# Load saved settings on startup
settings = load_settings()
section_default_cameras = settings["cameras"]
section_default_models = settings["models"]

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

# Callbacks to set default camera and model for each section and save the settings
def set_section_camera(section_index, camera_name):
    section_default_cameras[section_index] = camera_name
    save_settings({"cameras": section_default_cameras, "models": section_default_models})

def set_section_model(section_index, model_name):
    section_default_models[section_index] = model_name
    save_settings({"cameras": section_default_cameras, "models": section_default_models})

def create_countdown_section(title, default_camera=None, default_model=None):
    try:
        countdown_component = Countdown(
            update_person_count_callback=update_total_person_count,
            reset_person_count_callback=reset_total_person_count,
            default_camera=default_camera,
            default_model=default_model
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
            border_radius=ft.border_radius.all(12),
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

    # Callbacks list for each section camera and model setting
    set_section_camera_callbacks = [
        lambda camera: set_section_camera(0, camera),
        lambda camera: set_section_camera(1, camera),
        lambda camera: set_section_camera(2, camera)
    ]
    set_section_model_callbacks = [
        lambda model: set_section_model(0, model),
        lambda model: set_section_model(1, model),
        lambda model: set_section_model(2, model)
    ]

    settings_screen = SettingsScreen(
        set_section_camera_callbacks=set_section_camera_callbacks,
        set_section_model_callbacks=set_section_model_callbacks,
        default_cameras=section_default_cameras,
        default_models=section_default_models
    )

    def show_home(e):
        # Reinitialize sections with updated default cameras and models
        section1 = create_countdown_section("EleBull_VISION - Cam 1", default_camera=section_default_cameras[0], default_model=section_default_models[0])
        section2 = create_countdown_section("EleBull_VISION - Cam 2", default_camera=section_default_cameras[1], default_model=section_default_models[1])
        section3 = create_countdown_section("EleBull_VISION - Cam 3", default_camera=section_default_cameras[2], default_model=section_default_models[2])

        page.controls.clear()
        main_row.controls = [section1, section2, section3]
        page.controls.append(main_layout)
        page.update()

    def show_settings(e):
        page.controls.clear()
        page.controls.append(settings_screen)
        page.update()

    # Initial Countdown sections for each camera with individual default camera and model settings
    section1 = create_countdown_section("EleBull_VISION - Cam 1", default_camera=section_default_cameras[0], default_model=section_default_models[0])
    section2 = create_countdown_section("EleBull_VISION - Cam 2", default_camera=section_default_cameras[1], default_model=section_default_models[1])
    section3 = create_countdown_section("EleBull_VISION - Cam 3", default_camera=section_default_cameras[2], default_model=section_default_models[2])

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
            ft.ListTile(title=ft.Text("IP_CAMERA"), on_click=lambda e: print("About selected")),
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
