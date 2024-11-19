# ใช้ Python เวอร์ชันที่รองรับ
FROM python:3.10-slim

# ติดตั้ง dependencies ที่จำเป็นสำหรับ UI, OpenCV, GStreamer และ MPV
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    ffmpeg \
    libgtk-3-0 \
    gstreamer1.0-plugins-base \
    gstreamer1.0-tools \
    gstreamer1.0-x \
    gstreamer1.0-libav \
    libmpv1 \
    && rm -rf /var/lib/apt/lists/*

# ตั้งค่า directory ทำงานใน container
WORKDIR /app

# คัดลอกไฟล์ requirements.txt และติดตั้ง dependencies ผ่าน pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# คัดลอกไฟล์โปรเจกต์ทั้งหมดไปยัง container (รวม main.py, setting.py, vision_app.py)
COPY . .

# เปิดพอร์ตที่ใช้
EXPOSE 8550

# คำสั่งสำหรับการเริ่มต้นแอป
CMD ["python", "main.py"]
