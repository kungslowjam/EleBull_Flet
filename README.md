# EleBull_Flet

<div align="center">
<img src="https://github.com/user-attachments/assets/5f73cec5-bc54-48b2-8333-495eddc33dfe" alt="Elebull" />
</div>

---

# EleBull_VISION

**EleBull_VISION** is a Python-based video feed application that leverages [Flet](https://flet.dev/) for building the UI and [YOLO](https://github.com/ultralytics/yolov5) for real-time object detection. This project is primarily designed to detect and track animals (or people) across multiple camera feeds, each with individually configurable default settings.

## ✨ Features

- **Multiple Camera Feeds**: Set up multiple cameras, each with unique, configurable settings.
- **YOLO Object Detection**: Use YOLO for real-time animal/person detection and tracking, with unique ID assignment for each detected entity.
- **User Interface**: Intuitive, Flet-based UI for easy configuration of settings, camera selection, and theme.
- **Model Selection**: Choose from YOLO models (.pt or .engine files) to suit detection needs.

## 🚀 Installation

### Prerequisites

Ensure the following packages are installed:

- **Python 3.8 or higher**
- **Flet**: `pip install flet`
- **OpenCV**: `pip install opencv-python`
- **Ultralytics YOLO**: `pip install ultralytics`
- **pygrabber** (for Windows camera access): `pip install pygrabber`
- **torch** (PyTorch for YOLO model support): [Installation Instructions](https://pytorch.org/get-started/locally/)

### Clone the Repository

```bash
git clone https://github.com/your-username/elebull_vision.git
cd elebull_vision
