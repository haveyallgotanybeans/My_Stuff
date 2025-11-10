# Auto Annotator 
 
## Overview 
A custom auto-annotation tool built in Python for efficiently labeling images using YOLO models. It allows flexible dataset management, GPU acceleration (if available), and supports merging or renaming predefined classes to create new grouped labels. 
 
## Features 
- Supports any YOLO model (.pt) for inference 
- Merge or rename existing YOLO classes into new custom categories 
- Optional GPU acceleration using PyTorch/CUDA 
- Saves labels in YOLO format (.txt) compatible with Ultralytics training 
- Handles corrupt or unreadable images gracefully 
 
## Requirements 
Python 3.8+, PyTorch, OpenCV, Ultralytics YOLOv8/YOLOv11, tqdm 
 
## Usage 
python auto_annotator.py --model yolov11.pt --input images/ --output labels/ 
 
## Author 
Raviramanan V 
