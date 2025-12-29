"""
Utility functions for VisionGPT
Helper functions for common operations
"""

import os
import json
from datetime import datetime


def create_directories():
    """Create necessary directories if they don't exist"""
    dirs = ['data', 'data/detections', 'data/frames', 'modules', 'interface']
    for d in dirs:
        os.makedirs(d, exist_ok=True)


def save_frame(frame, frame_id, directory='data/frames'):
    """Save a frame as image file"""
    import cv2
    os.makedirs(directory, exist_ok=True)
    filename = f"frame_{frame_id:06d}.jpg"
    filepath = os.path.join(directory, filename)
    cv2.imwrite(filepath, frame)
    return filepath


def format_timestamp(timestamp):
    """Convert Unix timestamp to readable format"""
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]


def print_detection_summary(detection_data):
    """Print a summary of detections for debugging"""
    detections = detection_data['detections']
    timestamp = format_timestamp(detection_data['timestamp'])
    
    print(f"\n[Frame {detection_data['frame_id']}] {timestamp}")
    print(f"Objects detected: {len(detections)}")
    
    for det in detections:
        print(f"  - {det['class_name']}: {det['confidence']:.2f}")


def print_context_summary(context_data):
    """Print context summary for debugging"""
    print(f"\n[Context] Frame {context_data['frame_id']}")
    print(f"Objects: {', '.join(context_data['objects'])}")
    print(f"Relationships: {len(context_data['relationships'])}")
    print(f"Window size: {context_data['window_size']} frames")


class PerformanceMonitor:
    """Monitor FPS and processing times"""
    def __init__(self, name, window_size=30):
        self.name = name
        self.window_size = window_size
        self.times = []
        self.last_time = None
    
    def tick(self):
        """Record a tick"""
        import time
        current = time.time()
        
        if self.last_time is not None:
            interval = current - self.last_time
            self.times.append(interval)
            
            if len(self.times) > self.window_size:
                self.times.pop(0)
        
        self.last_time = current
    
    def get_fps(self):
        """Get average FPS"""
        if not self.times:
            return 0.0
        avg_interval = sum(self.times) / len(self.times)
        return 1.0 / avg_interval if avg_interval > 0 else 0.0
    
    def get_stats(self):
        """Get statistics"""
        if not self.times:
            return {'fps': 0.0, 'avg_ms': 0.0, 'min_ms': 0.0, 'max_ms': 0.0}
        
        times_ms = [t * 1000 for t in self.times]
        return {
            'fps': self.get_fps(),
            'avg_ms': sum(times_ms) / len(times_ms),
            'min_ms': min(times_ms),
            'max_ms': max(times_ms)
        }
    
    def print_stats(self):
        """Print statistics"""
        stats = self.get_stats()
        print(f"[{self.name}] FPS: {stats['fps']:.1f} | "
              f"Avg: {stats['avg_ms']:.1f}ms | "
              f"Min: {stats['min_ms']:.1f}ms | "
              f"Max: {stats['max_ms']:.1f}ms")