    import flet as ft
    from ultralytics import YOLO
    import cv2
    import numpy as np
    import base64
    import threading

    # Initialize YOLO model
    model = YOLO('yolov8n.pt')  # Use yolov8n.pt for a lightweight version

    def main(page: ft.Page):
        page.title = "YOLOv8 Object Detection App"
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        
        # Image viewer with an initial placeholder
        img_viewer = ft.Image(src_base64="", width=640, height=480)

        # Start detection function in a new thread
        def start_detection(e):
            def video_loop():
                # Open video capture for the webcam (or replace with a video file path)
                cap = cv2.VideoCapture(0)
                
                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    # Run YOLOv8 detection
                    results = model(frame)
                    
                    # Draw bounding boxes
                    for result in results:
                        for box in result.boxes:
                            x1, y1, x2, y2 = map(int, box.xyxy[0])  # Coordinates
                            confidence = box.conf[0]
                            label = result.names[int(box.cls[0])]  # Class name
                            
                            # Draw box and label on the frame
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                            cv2.putText(frame, f'{label} {confidence:.2f}', (x1, y1 - 10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                    # Encode frame to JPEG format
                    _, img_buf = cv2.imencode('.jpg', frame)
                    
                    # Convert to base64 and decode it to UTF-8
                    img_base64 = base64.b64encode(img_buf).decode('utf-8').replace('\n', '')

                    # Update the image source with the new base64 data
                    img_viewer.src_base64 = f'data:image/jpeg;base64,{img_base64}'

                    # Refresh the Flet page to display the updated frame
                    page.update()

                # Release the video capture when done
                cap.release()

            # Start the video loop in a new thread
            threading.Thread(target=video_loop, daemon=True).start()

        # Button to start detection
        start_btn = ft.ElevatedButton("Start Detection", on_click=start_detection)

        # Add elements to the page
        page.add(
            ft.Row([img_viewer]),
            ft.Row([start_btn], alignment=ft.MainAxisAlignment.CENTER),
        )

    # Run Flet app
    ft.app(target=main)
