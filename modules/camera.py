"""
Camera module - Handles webcam capture with frame sampling
Runs in separate process to avoid blocking
"""

import cv2
import time
import multiprocessing as mp
from config import CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT, CAPTURE_FPS, PROCESS_FPS


class CameraCapture:
    def __init__(self, frame_queue):
        """
        Args:
            frame_queue: multiprocessing.Queue to send captured frames
        """
        self.frame_queue = frame_queue
        self.running = False
        self.cap = None
        
        # Calculate frame sampling interval
        self.sample_interval = 1.0 / PROCESS_FPS  # seconds between processed frames
        
    def start(self):
        """Initialize camera and start capture loop"""
        self.cap = cv2.VideoCapture(CAMERA_INDEX)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, CAPTURE_FPS)
        
        if not self.cap.isOpened():
            raise RuntimeError("Cannot open camera")
        
        print(f"✓ Camera initialized: {FRAME_WIDTH}x{FRAME_HEIGHT} @ {CAPTURE_FPS}fps")
        print(f"✓ Processing every {self.sample_interval:.2f}s ({PROCESS_FPS} fps)")
        
        self.running = True
        self._capture_loop()
    
    def _capture_loop(self):
        """Main capture loop with frame sampling"""
        last_process_time = 0
        frame_id = 0
        
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to grab frame")
                break
            
            current_time = time.time()
            
            # Frame sampling: only process if enough time has passed
            if current_time - last_process_time >= self.sample_interval:
                # Don't block if queue is full, just skip this frame
                if not self.frame_queue.full():
                    frame_data = {
                        'frame_id': frame_id,
                        'timestamp': current_time,
                        'frame': frame.copy()
                    }
                    self.frame_queue.put(frame_data)
                    last_process_time = current_time
                    frame_id += 1
            
            # Small sleep to prevent CPU spinning
            time.sleep(0.001)
    
    def stop(self):
        """Stop capture and release camera"""
        self.running = False
        if self.cap:
            self.cap.release()
        print("✓ Camera stopped")


def camera_process(frame_queue, stop_event):
    """
    Process function to run camera in separate process
    
    Args:
        frame_queue: Queue to send frames
        stop_event: Event to signal when to stop
    """
    camera = CameraCapture(frame_queue)
    
    try:
        camera.start()
        
        # Keep running until stop event is set
        while not stop_event.is_set():
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        pass
    finally:
        camera.stop()