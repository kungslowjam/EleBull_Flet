import sys
import flet as ft
import os
import cv2  # สำหรับการดึงกล้องบน Linux

# ตรวจสอบระบบปฏิบัติการและนำเข้า pythoncom และ pygrabber เฉพาะบน Windows
if sys.platform == "win32":
    import pythoncom
    from pygrabber.dshow_graph import FilterGraph

# ฟังก์ชันสำหรับดึงข้อมูลอุปกรณ์กล้อง
def get_camera_devices():
    if sys.platform == "win32":  # ใช้ pythoncom และ pygrabber สำหรับ Windows
        pythoncom.CoInitialize()
        graph = FilterGraph()
        devices = graph.get_input_devices()
        return {device: index for index, device in enumerate(devices)}
    elif sys.platform == "linux":
        # ใช้ OpenCV สำหรับ Linux
        devices = {}
        index = 0
        while True:
            cap = cv2.VideoCapture(index)
            if not cap.read()[0]:  # ตรวจสอบว่ากล้องที่ index นี้ใช้ได้หรือไม่
                break
            devices[f"Camera {index}"] = index
            cap.release()
            index += 1
        return devices
    else:
        print("Camera device retrieval is only supported on Windows and Linux.")
        return {}  # ส่งคืนค่าว่างในกรณีที่ไม่ใช่ Windows หรือ Linux

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

        # สร้างรายการเก็บค่า threshold สำหรับแต่ละ section
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
        self.threshold_texts[section_index].value = f"{selected_threshold:.2f}"  # อัปเดตค่า slider
        self.threshold_texts[section_index].update()  # รีเฟรชการแสดงผล
        print(f"Confidence threshold for section {section_index + 1} set to: {selected_threshold}")

    def build(self):
        # สร้าง dropdown, model selector, และ threshold slider สำหรับแต่ละ section
        camera_model_sections = [
            ft.Container(
                width=280,  # กำหนดความกว้างของแต่ละ section
                content=ft.Column([
                    ft.Text(f"Settings for Section {i + 1}", size=18, weight="bold", color=ft.colors.WHITE),
                    
                    # ตัวเลือกกล้อง
                    ft.Dropdown(
                        options=[ft.dropdown.Option(name, text=name) for name in self.camera_devices.keys()] or [ft.dropdown.Option("No cameras available")],
                        label="Select Camera",
                        value=self.default_cameras[i],  # ค่าเริ่มต้นที่โหลดจากค่า default
                        on_change=lambda e, idx=i: self.on_camera_change(idx, e),
                        width=220  # ปรับความกว้างให้เหมาะสม
                    ),
                    
                    # ตัวเลือกโมเดล
                    ft.Dropdown(
                        options=[ft.dropdown.Option(file, text=file) for file in self.model_files] or [ft.dropdown.Option("No models available")],
                        label="Select Model",
                        value=self.default_models[i],  # ค่าเริ่มต้นที่โหลดจากค่า default model
                        on_change=lambda e, idx=i: self.on_model_change(idx, e),
                        width=220  # ปรับความกว้างให้เหมาะสม
                    ),
                    
                    # Slider สำหรับ confidence threshold
                    ft.Row(
                        controls=[
                            ft.Slider(
                                label="Confidence Threshold",
                                min=0.0,
                                max=1.0,
                                divisions=100,  # กำหนด slider ให้มี 100 ระดับระหว่าง 0.0 และ 1.0
                                value=self.default_thresholds[i],  # ค่าเริ่มต้น
                                on_change=lambda e, idx=i: self.on_threshold_change(idx, e),
                                width=140  # ปรับความกว้างให้เหมาะสม
                            ),
                            self.threshold_texts[i]  # แสดงค่าปัจจุบันของ threshold
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
            margin=ft.margin.only(bottom=20)  # เพิ่มพื้นที่ด้านล่างของหัวเรื่อง
        ) 
 
        # Return the layout with title and settings sections aligned separately 
        return ft.Column([ 
            title_section,  # หัวเรื่องด้านบน
            ft.Column(camera_model_sections, spacing=20)  # ส่วนการตั้งค่ากล้องด้านล่าง
        ], alignment=ft.MainAxisAlignment.START)  # จัดเรียง layout ไปทางซ้าย
