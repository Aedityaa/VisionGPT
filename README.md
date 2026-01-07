# VisionGPT 👁️🧠

**VisionGPT** is a real-time, multiprocessing AI vision system that combines fast object detection (YOLOv8) with a powerful Vision-Language Model (Qwen-VL).

Unlike standard detection scripts, VisionGPT maintains a **Spatial & Temporal Memory**. It doesn't just see "a cup"; it understands "the person *picked up* the cup 3 seconds ago" by analyzing object relationships over a rolling time window.

---

## 🚀 Key Features

* **⚡ True Parallel Processing:** Uses Python `multiprocessing` to run Camera, Detection, Context, and VLM logic on separate CPU cores/threads.
* **🧠 Spatial Context Awareness:** Automatically detects relationships like `is_holding`, `is_on`, `is_near`, and `left_of`/`right_of`.
* **⏳ 10-Second Short-Term Memory:** A rolling window buffer allows the AI to answer questions about recent actions, not just the current static frame.
* **💬 Natural Language Interface:** Talk to your video feed using State-of-the-Art VLMs (Qwen-VL).
* **📉 Smart Frame Sampling:** Decouples capture rate (30 FPS) from processing rate (3 FPS) to ensure real-time responsiveness without lag.

---

## 🏗️ System Architecture

Data flows through a unidirectional pipeline of independent workers:

1. **Camera Process (`camera.py`)**: Captures raw frames from Webcam/IP Camera.
2. **Detector Process (`detector.py`)**: Runs YOLOv8n to identify objects and bounding boxes.
3. **Context Builder (`context_builder.py`)**:
* Calculates spatial relationships (e.g., *Is the cup on the table?*).
* Updates the **Rolling Window** (Deque) to track history.
* Generates a text-based "Scene Description" prompt.


4. **VLM Handler (`vlm_handler.py`)**: Waits for user queries. When asked, it combines the *current image* + *historical text context* to generate an answer.

---

## 🛠️ Installation

### 1. Prerequisites

* Python 3.8+
* CUDA-enabled GPU (Recommended for VLM speed)

### 2. Install Dependencies

```bash
pip install opencv-python ultralytics torch transformers qwen-vl-utils numpy pillow

```

### 3. Model Setup

The system uses **YOLOv8 Nano** (auto-downloads) and **Qwen2-VL** (requires downloading).

* YOLO: Will download `yolov8n.pt` automatically on first run.
* VLM: Ensure you have access to `Qwen/Qwen2-VL-2B-Instruct` via Hugging Face, or change the `VLM_MODEL_PATH` in `config.py`.

---

## ⚙️ Configuration (`config.py`)

You can tune the performance in `config.py`. Key settings include:

| Setting | Default | Description |
| --- | --- | --- |
| `CAMERA_INDEX` | `0` | Set to `0` for webcam, or an HTTP URL for IP cameras (e.g., Phone). |
| `PROCESS_FPS` | `3` | How many times per second the AI "thinks". Lower = Less CPU usage. |
| `CONTEXT_WINDOW_SECONDS` | `10` | How far back the AI "remembers" (in seconds). |
| `YOLO_MODEL` | `"yolov8n.pt"` | Switch to `yolov8m.pt` for higher accuracy (but slower speed). |
| `INTERFACE_TYPE` | `"cli"` | Switch between CLI mode or GUI (if implemented). |

---

## 🏃 Usage

1. **Start the System:**
```bash
python main.py

```


2. **Wait for Initialization:**
* You will see logs as the Camera, Detector, and VLM models load.
* Once you see `✓ System ready!`, the terminal will open for input.


3. **Interact:**
* Type your question in the terminal (e.g., *"What is the person holding?"*).
* The VLM will analyze the last 10 seconds of context and the current frame to answer.


4. **Stop:**
* Press `Ctrl+C` to gracefully shut down all background processes.



---

## 📂 Project Structure

```text
VisionGPT/
├── main.py                # Entry point & Process Orchestrator
├── config.py              # Global settings
├── modules/
│   ├── camera.py          # Webcam capture & frame sampling
│   ├── detector.py        # YOLOv8 Object Detection
│   ├── context_builder.py # Spatial logic & Rolling Window memory
│   ├── vlm_handler.py     # Qwen-VL inference engine
│   └── utils.py           # Logging & file helpers
├── interface/
│   └── cli.py             # Command Line Interface logic
├── data/
│   ├── frames/            # Saved snapshots (optional)
│   └── detections/        # JSON logs of detections (optional)

```

---

## 🧩 Extending the Project

* **Add a Web UI:** Create a `web_main.py` using FastAPI/Flask to stream the `context_queue` to a React frontend.
* **Custom Object Detection:** Train a custom YOLO model on specific datasets (e.g., electronics, safety gear) and update `YOLO_MODEL` in config.
* **Voice Mode:** Integrate `pyttsx3` in `main.py` to make the AI speak its responses.

---

## 📜 License

MIT License. Feel free to use and modify!