"""
Configuration file for VisionGPT
Centralizes all settings for easy modification
"""

# Camera Settings
CAMERA_INDEX = 0  # Default webcam
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
CAPTURE_FPS = 30  # Camera capture rate
PROCESS_FPS = 3   # How many frames per second to process (frame sampling)

# YOLO Settings
YOLO_MODEL = "yolov8n.pt"  # 'n' for nano (fastest), 's', 'm', 'l', 'x' for larger
YOLO_CONFIDENCE = 0.5
YOLO_IOU_THRESHOLD = 0.45

# Context Builder Settings
ON_THRESHOLD = 0.3
NEAR_THRESHOLD = 150
HORIZONTAL_ALIGNMENT_THRESHOLD = 50

# Rolling Window Settings
CONTEXT_WINDOW_SECONDS = 10  # Keep last 10 seconds of detections
MAX_FRAMES_IN_WINDOW = PROCESS_FPS * CONTEXT_WINDOW_SECONDS  # 30 frames

# VLM Settings
VLM_MODEL_PATH = "Qwen/Qwen2-VL-2B-Instruct"  # Change to your model path
VLM_MAX_TOKENS = 512
VLM_TEMPERATURE = 0.7

# Queue Settings
FRAME_QUEUE_SIZE = 10
DETECTION_QUEUE_SIZE = 30
CONTEXT_QUEUE_SIZE = 30

# Paths
SAVE_DETECTIONS = False  # Set True to save detection JSONs for debugging
DETECTIONS_DIR = "data/detections"
FRAMES_DIR = "data/frames"

# Interface
INTERFACE_TYPE = "cli"  # 'cli' or 'gui'