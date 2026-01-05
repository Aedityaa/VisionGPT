"""
Context Builder with Rolling Window
Builds spatial relationships and maintains temporal context
"""

import numpy as np
import time
from collections import deque
from config import (ON_THRESHOLD, NEAR_THRESHOLD, HORIZONTAL_ALIGNMENT_THRESHOLD,
                   CONTEXT_WINDOW_SECONDS, MAX_FRAMES_IN_WINDOW)


class ContextBuilder:
    """
    Builds spatial relationship context from YOLO detections with rolling window.
    """

    def __init__(self):
        self.on_threshold = ON_THRESHOLD
        self.near_threshold = NEAR_THRESHOLD
        self.horizontal_alignment_threshold = HORIZONTAL_ALIGNMENT_THRESHOLD
        
        # Rolling window: stores recent detection frames
        self.detection_window = deque(maxlen=MAX_FRAMES_IN_WINDOW)

        self.surface_objects = {'table', 'desk', 'bed', 'couch', 'chair',
                               'dining table', 'counter', 'shelf'}

        self.holdable_objects = {'cell phone', 'bottle', 'cup', 'book',
                                'remote', 'fork', 'knife', 'spoon', 'umbrella'}

    def get_bbox_center(self, bbox):
        return [(bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2]

    def calculate_distance(self, center1, center2):
        return np.sqrt((center1[0] - center2[0])**2 + (center1[1] - center2[1])**2)

    def is_on(self, obj1, obj2):
        if obj2['class_name'] not in self.surface_objects:
            return False

        obj1_bottom = obj1['bbox'][3]
        obj2_top = obj2['bbox'][1]

        vertical_aligned = abs(obj1_bottom - obj2_top) < 50

        obj1_center_x = (obj1['bbox'][0] + obj1['bbox'][2]) / 2
        obj2_left = obj2['bbox'][0]
        obj2_right = obj2['bbox'][2]
        horizontal_overlap = obj2_left <= obj1_center_x <= obj2_right

        return vertical_aligned and horizontal_overlap

    def get_horizontal_relationship(self, obj1, obj2):
        center1 = self.get_bbox_center(obj1['bbox'])
        center2 = self.get_bbox_center(obj2['bbox'])

        vertical_diff = abs(center1[1] - center2[1])
        if vertical_diff > self.horizontal_alignment_threshold:
            return None

        if center1[0] < center2[0]:
            return "left_of"
        else:
            return "right_of"

    def is_holding(self, person, obj):
        if person['class_name'] != 'person':
            return False

        if obj['class_name'] not in self.holdable_objects:
            return False

        person_box = person['bbox']
        obj_center = self.get_bbox_center(obj['bbox'])

        in_horizontal = person_box[0] <= obj_center[0] <= person_box[2]

        person_height = person_box[3] - person_box[1]
        upper_region = person_box[1] + (person_height * 0.7)
        in_upper = obj_center[1] <= upper_region

        return in_horizontal and in_upper

    def build_relationships(self, detections):
        relationships = []

        sorted_detections = sorted(detections,
                                   key=lambda x: (x['bbox'][2] - x['bbox'][0]) *
                                               (x['bbox'][3] - x['bbox'][1]),
                                   reverse=True)

        for i, obj1 in enumerate(sorted_detections):
            for j, obj2 in enumerate(sorted_detections):
                if i == j:
                    continue

                obj1_name = obj1['class_name']
                obj2_name = obj2['class_name']

                if self.is_on(obj1, obj2):
                    relationships.append((obj1_name, "on", obj2_name))
                    continue

                if self.is_holding(obj1, obj2):
                    relationships.append((obj1_name, "holding", obj2_name))
                    continue

                horiz_rel = self.get_horizontal_relationship(obj1, obj2)
                if horiz_rel:
                    relationships.append((obj1_name, horiz_rel, obj2_name))

                center1 = self.get_bbox_center(obj1['bbox'])
                center2 = self.get_bbox_center(obj2['bbox'])
                distance = self.calculate_distance(center1, center2)

                if distance < self.near_threshold:
                    relationships.append((obj1_name, "near", obj2_name))

        relationships = list(set(relationships))
        return relationships
    
    def add_to_window(self, detection_data):
        """Add new detection frame to rolling window"""
        self.detection_window.append(detection_data)
        
        # Clean old frames outside time window
        current_time = time.time()
        while (self.detection_window and 
               current_time - self.detection_window[0]['timestamp'] > CONTEXT_WINDOW_SECONDS):
            self.detection_window.popleft()
    
    def get_temporal_summary(self):
        """Get summary of objects seen in the rolling window"""
        if not self.detection_window:
            return {}
        
        object_counts = {}
        for frame in self.detection_window:
            for det in frame['detections']:
                obj_name = det['class_name']
                object_counts[obj_name] = object_counts.get(obj_name, 0) + 1
        
        return object_counts

    def process_frame(self, detection_data, question=None):
        """
        Process detection data and build context
        
        Args:
            detection_data: Dict with detections from YOLO
            question: Optional user question
        
        Returns:
            Context dict with VLM prompt and frame
        """
        # Add to rolling window
        self.add_to_window(detection_data)
        
        detections = detection_data['detections']
        relationships = self.build_relationships(detections)

        # Format current frame objects
        objects_list = [f"{d['class_name']} (confidence: {d['confidence']:.2f})"
                       for d in detections]
        
        # Get temporal context
        temporal_summary = self.get_temporal_summary()
        temporal_text = ", ".join([f"{obj} ({count} frames)" 
                                  for obj, count in temporal_summary.items()])

        # Format relationships
        relations_text = []
        for obj1, rel, obj2 in relationships:
            rel_formatted = rel.replace("_", " ")
            relations_text.append(f"- {obj1} is {rel_formatted} {obj2}")

        vlm_prompt = f"""**Scene Analysis (Last {CONTEXT_WINDOW_SECONDS}s):**

**Currently Visible:** {', '.join(objects_list) if objects_list else 'No objects detected'}

**Objects Seen Recently:** {temporal_text if temporal_text else 'None'}

**Spatial Relationships:**
{chr(10).join(relations_text) if relations_text else "- No clear spatial relationships detected"}
"""

        if question:
            vlm_prompt += f"""
**Question:** {question}

Based on the visual scene and the analysis above, please answer the question accurately and concisely."""

        return {
            'frame_id': detection_data['frame_id'],
            'timestamp': detection_data['timestamp'],
            'frame': detection_data['frame'],  # Pass frame to VLM
            'num_objects': len(detections),
            'objects': [d['class_name'] for d in detections],
            'relationships': relationships,
            'vlm_prompt': vlm_prompt,
            'window_size': len(self.detection_window)
        }


def context_process(detection_queue, context_queue, stop_event):
    """
    Process function to run context builder in separate process
    
    Args:
        detection_queue: Queue to receive detections
        context_queue: Queue to send context data
        stop_event: Event to signal when to stop
    """
    builder = ContextBuilder()
    print(f"Context builder started (window: {CONTEXT_WINDOW_SECONDS}s)")
    
    try:
        while not stop_event.is_set():
            try:
                detection_data = detection_queue.get(timeout=0.1)
            except:
                continue
            
            # Build context
            context_data = builder.process_frame(detection_data)
            
            # Send to VLM handler
            if not context_queue.full():
                context_queue.put(context_data)
            
    except KeyboardInterrupt:
        pass
    finally:
        print("Context builder stopped")