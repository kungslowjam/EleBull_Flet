import sys
import os
import flet as ft
import base64
import cv2
import threading
import time
import queue
import torch
from ultralytics import YOLO

# ตรวจสอบระบบปฏิบัติการ
if sys.platform == "win32":
    import pythoncom
    from pygrabber.dshow_graph import FilterGraph

# Constants
MODEL_DIR = "model"
FRAME_SIZE = (320, 320)
FRAME_QUEUE_SIZE = 5

# ฟังก์ชันสำหรับดึงข้อมูลกล้อง
def get_camera_devices():
    if sys.platform == "win32":  # ใช้ pythoncom และ pygrabber สำหรับ Windows
        pythoncom.CoInitialize()
        try:
            graph = FilterGraph()
            devices = graph.get_input_devices()
            return {device: index for index, device in enumerate(devices)}
        finally:
            pythoncom.CoUninitialize()
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

class Countdown(ft.UserControl): 
    def __init__(self, update_person_count_callback, reset_person_count_callback, default_camera=None, default_model=None, confidence_threshold=0.5): 
        super().__init__()
        self.running = False
        self.automatic_start = False  
        self.update_person_count_callback = update_person_count_callback
        self.reset_person_count_callback = reset_person_count_callback
        self.selected_camera_name = default_camera
        self.selected_model_path = os.path.join(MODEL_DIR, default_model) if default_model else None
        self.confidence_threshold = confidence_threshold  
        self.frame_queue = queue.Queue(maxsize=FRAME_QUEUE_SIZE)
        self.camera_devices = get_camera_devices()  # ดึงข้อมูลกล้องจากฟังก์ชันที่ปรับแล้ว
        self.model = None
        self.status_text = ft.Text(f"Selected Camera: {default_camera if default_camera else 'None'}, Selected Model: {default_model if default_model else 'None'}")
        self.detection_info = ft.Text("Detections: None", color=ft.colors.WHITE)
        self.unique_person_ids = set()

        transparent_pixel = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/wcAAgAB/Onk7AAA"
        self.img = ft.Image(border_radius=ft.border_radius.all(20), src_base64=transparent_pixel)

        self.loading_indicator = ft.ProgressRing(visible=False)

        self.load_model()

    def load_model(self):
        """Load the YOLO model based on the selected model path."""
        if self.selected_model_path and os.path.exists(self.selected_model_path):
            try:
                self.model = YOLO(self.selected_model_path, task="detect")
                print(f"Model loaded: {self.selected_model_path}")
                if self.automatic_start:
                    self.start_video_feed(None)  
            except Exception as e:
                print(f"Error loading YOLO model: {e}")
                self.model = None
        else:
            print("No model selected or model file missing.")

    def start_video_feed(self, e):
        """Start capturing video and processing frames."""
        if not self.running:
            if self.selected_camera_name in self.camera_devices:
                self.loading_indicator.visible = True
                self.update()
                
                self.cap = cv2.VideoCapture(self.camera_devices[self.selected_camera_name])
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                if not self.cap.isOpened():
                    print("Error: Cannot open camera.")
                    self.loading_indicator.visible = False
                    self.update()
                    return

                self.running = True
                threading.Thread(target=self.read_frames, daemon=True).start()
                threading.Thread(target=self.process_frames, daemon=True).start()
                
                self.loading_indicator.visible = False
                self.update()
            else:
                print("Selected camera not available.")
    
    def stop_video_feed(self, e):
        """Stop video capture and release resources."""
        self.running = False
        if self.cap:
            self.cap.release()
            self.cap = None
        self.loading_indicator.visible = False  
        self.update()

    def reset_person_count(self, e):
        """Reset person count."""
        self.reset_person_count_callback()

    def will_unmount(self):
        """Ensure proper cleanup on component unmount."""
        self.stop_video_feed(None)

    def read_frames(self):
        """Read frames from the camera and add them to the queue."""
        while self.running:
            success, frame = self.cap.read()
            if not success:
                break
            frame = cv2.resize(frame, FRAME_SIZE)
            if not self.frame_queue.full():
                self.frame_queue.put(frame)
            time.sleep(0.03)

    def process_frames(self):
        """Process frames in the queue using the YOLO model."""
        if self.model is None:
            print("YOLO model not loaded. Skipping frame processing.")
            return

        while self.running:
            if not self.frame_queue.empty():
                frame = self.frame_queue.get()
                try:
                    with torch.no_grad():
                        results = self.model.track(
                            source=frame,
                            imgsz=FRAME_SIZE[0],
                            tracker="botsort.yaml",
                            conf=self.confidence_threshold
                        )
                    if results:
                        detections = results[0].names
                        class_counts = {}
                        detection_ids = []

                        for box in results[0].boxes:
                            class_name = detections[int(box.cls)]
                            track_id_tensor = box.id
                            track_id = int(track_id_tensor.item()) if track_id_tensor is not None else None

                            if class_name == "person" and track_id is not None and track_id not in self.unique_person_ids:
                                self.unique_person_ids.add(track_id)
                                self.update_person_count_callback(track_id)
                            detection_ids.append(f"{class_name} (ID: {track_id})")
                            class_counts[class_name] = class_counts.get(class_name, 0) + 1

                        detection_summary = "Detections: " + ", ".join([f"{cls}: {count}" for cls, count in class_counts.items()])
                        detection_summary += "\nTrack IDs: " + ", ".join(detection_ids[:10])
                        self.detection_info.value = detection_summary
                        self.update()

                        annotated_frame = results[0].plot() if results else frame
                        _, buffer = cv2.imencode('.png', annotated_frame)
                        self.img.src_base64 = base64.b64encode(buffer).decode("utf-8")
                        self.update()
                except Exception as e:
                    print(f"Error processing frame: {e}")
                time.sleep(0.02)

    def on_camera_change(self, e):
        """Handle camera selection change."""
        self.selected_camera_name = e.control.value
        self.status_text.value = f"Selected Camera: {self.selected_camera_name}"
        if self.automatic_start:
            self.start_video_feed(None)
        self.update()

    def on_model_change(self, e):
        """Handle model selection change."""
        self.selected_model_path = os.path.join(MODEL_DIR, e.control.value)
        self.status_text.value = f"Selected Model: {os.path.basename(self.selected_model_path)}"
        self.load_model()
        self.update()

    def toggle_automatic_start(self, e):
        """Toggle automatic start functionality."""
        self.automatic_start = e.control.value
        print(f"Automatic Start set to: {self.automatic_start}")

    def build(self):
        """Build the UI components for the countdown system."""
        camera_selector = ft.Dropdown(
            options=[ft.dropdown.Option(name, text=name) for name in self.camera_devices.keys()] or [ft.dropdown.Option("No cameras available")],
            label="Select Camera",
            value=self.selected_camera_name,
            on_change=self.on_camera_change,
            width=200
        )

        model_files = [f for f in os.listdir(MODEL_DIR) if f.endswith((".engine", ".pt"))]
        
        model_selector = ft.Dropdown(
            options=[ft.dropdown.Option(file, text=file) for file in model_files] or [ft.dropdown.Option("No models available")],
            label="Select Model",
            value=os.path.basename(self.selected_model_path) if self.selected_model_path else None,
            on_change=self.on_model_change,
            width=200
        )
        
        button_row = ft.Row(
            controls=[
                ft.ElevatedButton(text="Start", on_click=self.start_video_feed),
                ft.ElevatedButton(text="Stop", on_click=self.stop_video_feed),
            ],
            alignment=ft.MainAxisAlignment.START
        )

        return ft.Column([
            camera_selector,
            model_selector,
            self.loading_indicator,
            self.status_text,
            self.detection_info,
            button_row, 
            self.img 
        ])
