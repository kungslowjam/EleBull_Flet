# vision_app.py
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

# โหลดโมเดล YOLO
model = YOLO("yolov8n.engine", task="detect")

# ฟังก์ชันสำหรับดึงข้อมูลกล้องจาก Windows
def get_camera_devices():
    pythoncom.CoInitialize()  # Initialize COM for DirectShow on Windows
    graph = FilterGraph()
    devices = graph.get_input_devices()
    return [(device, index) for index, device in enumerate(devices)]

class Countdown(ft.UserControl):
    def __init__(self):
        super().__init__()
        self.running = False
        # ใช้ base64-encoded โปร่งใสสำหรับรูปเริ่มต้น
        transparent_pixel = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/wcAAgAB/Onk7AAA"
        self.img = ft.Image(border_radius=ft.border_radius.all(20), src_base64=transparent_pixel)  
        self.cap = None
        self.selected_camera_index = 0
        self.frame_queue = queue.Queue(maxsize=5)

    def start_video_feed(self, e):
        if not self.running:
            self.cap = cv2.VideoCapture(self.selected_camera_index)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            if not self.cap.isOpened():
                print("Error: Cannot open camera.")
                return
            self.running = True
            threading.Thread(target=self.read_frames).start()
            threading.Thread(target=self.process_frames).start()

    def stop_video_feed(self, e):
        self.running = False
        if self.cap:
            self.cap.release()
            self.cap = None

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
            frame = cv2.resize(frame, (320, 320))
            if not self.frame_queue.full():
                self.frame_queue.put(frame)
            time.sleep(0.01)

    def process_frames(self):
        while self.running:
            if not self.frame_queue.empty():
                frame = self.frame_queue.get()
                with torch.no_grad():
                    results = model.predict(frame, imgsz=320)
                    annotated_frame = results[0].plot()
                _, buffer = cv2.imencode('.png', annotated_frame)
                im_b64 = base64.b64encode(buffer).decode("utf-8")
                self.img.src_base64 = im_b64
                self.update()
            time.sleep(0.02)

    def on_camera_change(self, e):
        self.selected_camera_index = int(e.control.value)

    def build(self):
        camera_devices = get_camera_devices()
        camera_selector = ft.Dropdown(
            options=[ft.dropdown.Option(str(index), text=name) for name, index in camera_devices],
            label="Select Camera",
            on_change=self.on_camera_change,
            width=200
        )
        button_row = ft.Row(
            controls=[
                ft.ElevatedButton(text="Start", on_click=self.start_video_feed),
                ft.ElevatedButton(text="Stop", on_click=self.stop_video_feed)
            ],
            alignment=ft.MainAxisAlignment.START
        )
        return ft.Column([camera_selector, button_row, self.img])
