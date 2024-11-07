import os
import flet as ft
import base64
import cv2
import threading
import time
import queue
import torch
from ultralytics import YOLO
import pythoncom
from pygrabber.dshow_graph import FilterGraph

# Constants
MODEL_DIR = "model"
FRAME_SIZE = (320, 320)
FRAME_QUEUE_SIZE = 5

# Function to retrieve camera devices from Windows
def get_camera_devices():
    pythoncom.CoInitialize()
    graph = FilterGraph()
    devices = graph.get_input_devices()
    return {device: index for index, device in enumerate(devices)}

class Countdown(ft.UserControl):
    def __init__(self, update_person_count_callback, reset_person_count_callback, default_camera=None, default_model=None):
        super().__init__()
        self.running = False
        self.update_person_count_callback = update_person_count_callback
        self.reset_person_count_callback = reset_person_count_callback
        self.selected_camera_name = default_camera  # Set the default camera at initialization
        self.selected_model_path = os.path.join(MODEL_DIR, default_model) if default_model else None  # Set the default model at initialization
        self.frame_queue = queue.Queue(maxsize=FRAME_QUEUE_SIZE)
        self.camera_devices = get_camera_devices()
        self.model = None
        self.status_text = ft.Text(f"Selected Camera: {default_camera if default_camera else 'None'}, Selected Model: {default_model if default_model else 'None'}")
        self.detection_info = ft.Text("Detections: None", color=ft.colors.WHITE)
        self.unique_person_ids = set()  # Track unique person IDs
        
        # Placeholder transparent image in base64 format (1x1 pixel)
        transparent_pixel = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/wcAAgAB/Onk7AAA"
        self.img = ft.Image(border_radius=ft.border_radius.all(20), src_base64=transparent_pixel)  # Initialize with placeholder

        # Load model if default model is set
        self.load_model()

    def load_model(self):
        if self.selected_model_path:
            try:
                self.model = YOLO(self.selected_model_path, task="detect")
                print(f"Model loaded: {self.selected_model_path}")
            except Exception as e:
                print(f"Error loading YOLO model: {e}")
                self.model = None
        else:
            print("No model selected.")

    def start_video_feed(self, e):
        if not self.running:
            if self.selected_camera_name:
                if self.selected_camera_name in self.camera_devices:
                    self.cap = cv2.VideoCapture(self.camera_devices[self.selected_camera_name])
                    self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                    if not self.cap.isOpened():
                        print("Error: Cannot open camera.")
                        return
                    self.running = True
                    self.load_model()
                    threading.Thread(target=self.read_frames, daemon=True).start()
                    threading.Thread(target=self.process_frames, daemon=True).start()
                else:
                    print("Selected camera not available.")
            else:
                print("No camera selected.")

    def stop_video_feed(self, e):
        self.running = False
        if self.cap:
            self.cap.release()
            self.cap = None

    def reset_person_count(self, e):
        self.reset_person_count_callback()  # Call the callback to reset person count

    def will_unmount(self):
        self.running = False
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()

    def read_frames(self):
        while self.running:
            success, frame = self.cap.read()
            if not success:
                break
            frame = cv2.resize(frame, FRAME_SIZE)
            if not self.frame_queue.full():
                self.frame_queue.put(frame)
            time.sleep(0.01)

    def process_frames(self):
        if self.model is None:
            print("YOLO model not loaded. Skipping frame processing.")
            return

        while self.running:
            if not self.frame_queue.empty():
                frame = self.frame_queue.get()
                with torch.no_grad():
                    results = self.model.track(source=frame, imgsz=FRAME_SIZE[0], tracker="botsort.yaml")
                    
                    if results:
                        detections = results[0].names
                        class_counts = {}
                        detection_ids = []

                        for box in results[0].boxes:
                            class_name = detections[int(box.cls)]
                            track_id_tensor = box.id

                            if track_id_tensor is not None and isinstance(track_id_tensor, torch.Tensor):
                                track_id = int(track_id_tensor.item())
                            else:
                                track_id = track_id_tensor

                            if class_name == "person" and track_id is not None:
                                if track_id not in self.unique_person_ids:
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
                    im_b64 = base64.b64encode(buffer).decode("utf-8")
                    self.img.src_base64 = im_b64
                    self.update()
                time.sleep(0.02)

    def on_camera_change(self, e):
        self.selected_camera_name = e.control.value
        self.status_text.value = f"Selected Camera: {self.selected_camera_name}"
        self.update()

    def on_model_change(self, e):
        self.selected_model_path = os.path.join(MODEL_DIR, e.control.value)
        self.status_text.value = f"Selected Model: {os.path.basename(self.selected_model_path)}"
        self.load_model()  # Load the newly selected model
        self.update()

    def build(self):
        camera_selector = ft.Dropdown(
            options=[ft.dropdown.Option(name, text=name) for name in self.camera_devices.keys()] or [ft.dropdown.Option("No cameras available")],
            label="Select Camera",
            value=self.selected_camera_name,  # Set initial value to the default camera
            on_change=self.on_camera_change,
            width=200
        )

        model_files = [f for f in os.listdir(MODEL_DIR) if f.endswith((".engine", ".pt"))]
        
        model_selector = ft.Dropdown(
            options=[ft.dropdown.Option(file, text=file) for file in model_files] or [ft.dropdown.Option("No models available")],
            label="Select Model",
            value=os.path.basename(self.selected_model_path) if self.selected_model_path else None,  # Set initial value to the default model
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
            self.status_text,
            self.detection_info,
            button_row,
            self.img
        ])
