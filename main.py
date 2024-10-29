import flet as ft
import base64
import cv2
import threading
import time
import io
from ultralytics import YOLO
from PIL import Image
import numpy as np
import torch

# Load YOLOv8 model
model = YOLO("yolov8n.pt")  # Replace with your YOLOv8 model path

# Capture video from the specified path or webcam
cap = cv2.VideoCapture(0)  # Use "0" for webcam, or replace with video path

class Countdown(ft.UserControl):
    def __init__(self):
        super().__init__()
        self.running = False  # Control flag for the thread, initially set to False
        self.img = ft.Image(border_radius=ft.border_radius.all(20))

    def start_video_feed(self, e):
        # Start video feed thread
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.update_timer)
            self.thread.start()

    def will_unmount(self):
        # Stop the thread and release the video capture when unmounting
        self.running = False
        if hasattr(self, "thread"):
            self.thread.join()
        cap.release()

    def update_timer(self):
        while self.running:
            success, frame = cap.read()
            if not success:
                break
            
            # Reduce frame resolution for faster processing
            frame = cv2.resize(frame, (320, 240))  # Resize to smaller resolution

            # Run YOLOv8 detection on the frame
            with torch.no_grad():  # Disable gradients for faster inference
                results = model.predict(frame, imgsz=320)  # Lower imgsz for faster processing
                annotated_frame = results[0].plot()  # Get annotated frame as numpy array

            # Convert annotated frame to RGB for Flet compatibility
            annotated_frame_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(annotated_frame_rgb)

            # Encode the PIL image as a PNG for Flet
            img_byte_arr = io.BytesIO()
            pil_image.save(img_byte_arr, format='PNG')
            im_b64 = base64.b64encode(img_byte_arr.getvalue()).decode("utf-8")

            # Update the image in the Flet app
            self.img.src_base64 = im_b64
            self.update()

            # Small delay for frame rate control
            time.sleep(0.05)  # Adjust this value to control the frame rate

    def build(self):
        # Define start button here
        start_button = ft.ElevatedButton(text="Start", on_click=self.start_video_feed)
        
        # Return a Column layout containing the button and image
        return ft.Column([start_button, self.img])

def main(page: ft.Page):
    page.padding = 50
    page.window_left = page.window_left + 100
    page.theme_mode = ft.ThemeMode.DARK

    # Layout with only the video feed and title text
    section = ft.Container(
        margin=ft.margin.only(bottom=40),
        content=ft.Column([
            ft.Text(
                "OPENCV WITH FLET AND YOLOv8",
                size=20, weight="bold",
                color=ft.colors.WHITE,
            ),
            Countdown()
        ], alignment=ft.MainAxisAlignment.CENTER),
        bgcolor=ft.colors.WHITE24,
        padding=10,
        border_radius=ft.border_radius.all(20),
    )

    # Add the section to the page
    page.add(section)

if __name__ == '__main__':
    ft.app(target=main)
    cv2.destroyAllWindows()
