import flet as ft
from pygrabber.dshow_graph import FilterGraph
import pythoncom
import os

# Function to retrieve camera devices from Windows
def get_camera_devices():
    pythoncom.CoInitialize()
    graph = FilterGraph()  
    devices = graph.get_input_devices()  
    return {device: index for index, device in enumerate(devices)}  

class SettingsScreen(ft.UserControl):
    def __init__(self, set_section_camera_callbacks, set_section_model_callbacks, set_section_threshold_callbacks, default_cameras, default_models, default_thresholds):
        super().__init__()
        self.set_section_camera_callbacks = set_section_camera_callbacks
        self.set_section_model_callbacks = set_section_model_callbacks
        self.set_section_threshold_callbacks = set_section_threshold_callbacks
        self.camera_devices = get_camera_devices()
        self.default_cameras = default_cameras
        self.default_models = default_models
        self.default_thresholds = default_thresholds
        self.model_files = [f for f in os.listdir("model") if f.endswith((".engine", ".pt"))]  # List available models

        # Create list to store threshold text elements for each section
        self.threshold_texts = [ft.Text(f"{default_thresholds[i]:.2f}") for i in range(len(default_thresholds))]

    def on_camera_change(self, section_index, e):
        selected_camera = e.control.value
        self.set_section_camera_callbacks[section_index](selected_camera)
        print(f"Default camera for section {section_index + 1} set to: {selected_camera}")

    def on_model_change(self, section_index, e):
        selected_model = e.control.value
        self.set_section_model_callbacks[section_index](selected_model)
        print(f"Default model for section {section_index + 1} set to: {selected_model}")

    def on_threshold_change(self, section_index, e):
        selected_threshold = e.control.value
        self.set_section_threshold_callbacks[section_index](selected_threshold)
        self.threshold_texts[section_index].value = f"{selected_threshold:.2f}"  # Update the text to show the slider value
        self.threshold_texts[section_index].update()  # Refresh the display
        print(f"Confidence threshold for section {section_index + 1} set to: {selected_threshold}")

    def build(self):
        # Create a dropdown, model selector, and threshold slider for each section
        camera_model_sections = [
            ft.Container(
                width=280,  # Set width of each section to reduce its size
                content=ft.Column([
                    ft.Text(f"Settings for Section {i + 1}", size=18, weight="bold", color=ft.colors.WHITE),
                    
                    # Camera dropdown
                    ft.Dropdown(
                        options=[ft.dropdown.Option(name, text=name) for name in self.camera_devices.keys()] or [ft.dropdown.Option("No cameras available")],
                        label="Select Camera",
                        value=self.default_cameras[i],  # Set initial value to the loaded default camera
                        on_change=lambda e, idx=i: self.on_camera_change(idx, e),
                        width=220  # Adjust width of dropdown to fit within reduced container width
                    ),
                    
                    # Model dropdown
                    ft.Dropdown(
                        options=[ft.dropdown.Option(file, text=file) for file in self.model_files] or [ft.dropdown.Option("No models available")],
                        label="Select Model",
                        value=self.default_models[i],  # Set initial value to the loaded default model
                        on_change=lambda e, idx=i: self.on_model_change(idx, e),
                        width=220  # Adjust width of dropdown to fit within reduced container width
                    ),
                    
                    # Confidence threshold slider with live value display
                    ft.Row(
                        controls=[
                            ft.Slider(
                                label="Confidence Threshold",
                                min=0.0,
                                max=1.0,
                                divisions=100,  # Adjust slider to have 100 steps between 0.0 and 1.0
                                value=self.default_thresholds[i],  # Set initial threshold
                                on_change=lambda e, idx=i: self.on_threshold_change(idx, e),
                                width=140  # Adjust width to fit within reduced container width
                            ),
                            self.threshold_texts[i]  # Display current threshold value
                        ],
                        alignment=ft.MainAxisAlignment.START
                    ),
                ], spacing=5, alignment=ft.MainAxisAlignment.START),
                
                bgcolor=ft.colors.BLUE_GREY_900,
                padding=10,
                border_radius=ft.border_radius.all(12),
                border=ft.border.all(1, ft.colors.BLUE_GREY_800),
                margin=ft.margin.only(bottom=20)
            )
            for i in range(len(self.set_section_camera_callbacks))
        ]

        # Title with bottom margin
        title_section = ft.Container(
            content=ft.Text("Camera & Model", size=24, weight="bold", color=ft.colors.WHITE),
            margin=ft.margin.only(bottom=20)  # Adds space below the title
        ) 
 
        # Return the layout with title and settings sections aligned separately 
        return ft.Column([ 
            title_section,  # Title at the top 
            ft.Column(camera_model_sections, spacing=20)  # Camera settings sections below 
        ], alignment=ft.MainAxisAlignment.START)  # Align the entire layout to the left
