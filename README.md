# VisionGPT: Real-time Vision Assistant

VisionGPT is a multi-processed Python application that combines real-time object detection with a Vision-Language Model (VLM) to allow users to ask questions about their physical environment via a webcam.

## Features

* **Real-time Object Detection:** Uses YOLOv8 for high-speed object identification.
* **Spatial Context Awareness:** Analyzes relationships between objects (e.g., "on," "near," "holding").
* **Temporal Context:** Maintains a rolling window of recently seen objects (default: 10 seconds).
* **Conversational Vision:** Integration with Qwen-VL-2B to answer complex natural language questions about the scene.
* **High Performance:** Uses Python's `multiprocessing` to run camera capture, detection, context building, and the VLM in parallel.

---

## Architecture

The system consists of five parallel components:

1. **Camera Process:** Captures and samples frames from the webcam.
2. **Detector Process:** Runs YOLOv8 inference to find objects.
3. **Context Process:** Builds spatial relationships and maintains a history of detections.
4. **VLM Process:** Manages the Qwen-VL model for image-to-text reasoning.
5. **Interface Process:** Handles user input and displays AI responses via a CLI.

---

## Requirements

* Python 3.11
* Webcam
* NVIDIA GPU (Recommended for VLM inference)

### Dependencies

Install the required packages:

```bash
pip install -r requirements.txt

```

*Key packages include: `opencv-python`, `ultralytics` (YOLOv8), `torch`, `transformers`, and `qwen-vl-utils*`.

---

## Configuration

All settings are centralized in `backend/config.py`. You can modify:

* **`CAMERA_INDEX`**: Change the source webcam.
* **`PROCESS_FPS`**: Control how many frames per second are analyzed.
* **`YOLO_MODEL`**: Choose model size (nano, small, medium, etc.).
* **`VLM_MODEL_PATH`**: Set the specific HuggingFace model path.

---

## Getting Started

1. **Clone the repository.**
2. **Run the application:**
```bash
python backend/main.py

```


3. **Interact:** Once the system initializes, you can type questions into the terminal like:
* *"What objects do you see?"*
* *"Is there anyone holding a phone?"*
* *"Describe the scene."*



---

## Project Structure

* `main.py`: Main entry point and process orchestrator.
* `config.py`: Global configuration and thresholds.
* `modules/`:
* `camera.py`: Webcam capture logic.
* `detector.py`: YOLOv8 detection implementation.
* `context_builder.py`: Spatial and temporal logic.
* `vlm_handler.py`: Qwen-VL inference management.
* `utils.py`: Logging and performance monitoring.


* `interface/`: CLI implementation.