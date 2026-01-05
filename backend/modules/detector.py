"""
Object detection module using YOLOv8
Runs in separate process, receives frames and outputs detections
"""

import time
import json
import os
from ultralytics import YOLO
from config import (YOLO_MODEL, YOLO_CONFIDENCE, YOLO_IOU_THRESHOLD,
                   SAVE_DETECTIONS, DETECTIONS_DIR)


class ObjectDetector:
    def __init__(self, detection_queue):
        """
        Args:
            detection_queue: Queue to send detection results
        """
        self.detection_queue = detection_queue
        self.model = None
        
    def initialize(self):
        """Load YOLO model"""
        print(f"Loading YOLO model: {YOLO_MODEL}...")
        self.model = YOLO(YOLO_MODEL)
        print("✓ YOLO model loaded")
        
        if SAVE_DETECTIONS:
            os.makedirs(DETECTIONS_DIR, exist_ok=True)
    
    def detect(self, frame_data):
        """
        Run detection on a frame
        
        Args:
            frame_data: Dict with 'frame_id', 'timestamp', 'frame'
        
        Returns:
            Detection results in standardized format
        """
        frame = frame_data['frame']
        
        # Run YOLO inference
        results = self.model(frame, 
                           conf=YOLO_CONFIDENCE,
                           iou=YOLO_IOU_THRESHOLD,
                           verbose=False)[0]
        
        # Convert to standard format
        detections = []
        for box in results.boxes:
            detection = {
                'class_id': int(box.cls[0]),
                'class_name': results.names[int(box.cls[0])],
                'confidence': float(box.conf[0]),
                'bbox': box.xyxy[0].tolist()  # [x1, y1, x2, y2]
            }
            detections.append(detection)
        
        detection_data = {
            'frame_id': frame_data['frame_id'],
            'timestamp': frame_data['timestamp'],
            'frame': frame,  # Keep frame for VLM
            'detections': detections
        }
        
        # Optionally save to JSON for debugging
        if SAVE_DETECTIONS:
            json_path = os.path.join(DETECTIONS_DIR, 
                                    f"frame_{frame_data['frame_id']:06d}.json")
            with open(json_path, 'w') as f:
                # Don't save frame in JSON, just detections
                save_data = {
                    'frame_id': frame_data['frame_id'],
                    'timestamp': frame_data['timestamp'],
                    'detections': detections
                }
                json.dump(save_data, f, indent=2)
        
        return detection_data


def detector_process(frame_queue, detection_queue, stop_event):
    """
    Process function to run detector in separate process
    
    Args:
        frame_queue: Queue to receive frames from camera
        detection_queue: Queue to send detection results
        stop_event: Event to signal when to stop
    """
    detector = ObjectDetector(detection_queue)
    detector.initialize()
    
    print("✓ Detector process started")
    
    try:
        while not stop_event.is_set():
            # Get frame from queue (with timeout to check stop_event)
            try:
                frame_data = frame_queue.get(timeout=0.1)
            except:
                continue
            
            # Run detection
            detection_data = detector.detect(frame_data)
            
            # Send to next stage
            if not detection_queue.full():
                detection_queue.put(detection_data)
            
    except KeyboardInterrupt:
        pass
    finally:
        print("✓ Detector process stopped")