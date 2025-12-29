"""
VLM Handler for Qwen-VL model
Manages model loading and inference with both image and text context
"""

import torch
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
from qwen_vl_utils import process_vision_info
import cv2
from PIL import Image
import numpy as np
from config import VLM_MODEL_PATH, VLM_MAX_TOKENS, VLM_TEMPERATURE


class VLMHandler:
    def __init__(self):
        self.model = None
        self.processor = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.latest_context = None
        
    def initialize(self):
        """Load Qwen-VL model"""
        print(f"Loading VLM model: {VLM_MODEL_PATH}...")
        print(f"Using device: {self.device}")
        
        self.model = Qwen2VLForConditionalGeneration.from_pretrained(
            VLM_MODEL_PATH,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            device_map="auto" if self.device == "cuda" else None
        )
        
        self.processor = AutoProcessor.from_pretrained(VLM_MODEL_PATH)
        
        print("✓ VLM model loaded")
    
    def update_context(self, context_data):
        """Store latest context from context builder"""
        self.latest_context = context_data
    
    def frame_to_pil(self, frame):
        """Convert OpenCV frame to PIL Image"""
        # OpenCV uses BGR, PIL uses RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return Image.fromarray(frame_rgb)
    
    def query(self, question):
        """
        Answer a question using latest frame and context
        
        Args:
            question: User's question string
        
        Returns:
            Model's response text
        """
        if self.latest_context is None:
            return "No visual context available yet. Please wait for camera to initialize."
        
        # Get frame and convert to PIL
        frame = self.latest_context['frame']
        pil_image = self.frame_to_pil(frame)
        
        # Get text context from context builder
        text_context = self.latest_context['vlm_prompt']
        
        # Construct message for Qwen-VL
        # Qwen-VL expects messages in format with image and text
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "image": pil_image
                    },
                    {
                        "type": "text",
                        "text": f"{text_context}\n\n{question}"
                    }
                ]
            }
        ]
        
        # Process with Qwen-VL processor
        text = self.processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        
        image_inputs, video_inputs = process_vision_info(messages)
        
        inputs = self.processor(
            text=[text],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt"
        )
        
        inputs = inputs.to(self.device)
        
        # Generate response
        with torch.no_grad():
            generated_ids = self.model.generate(
                **inputs,
                max_new_tokens=VLM_MAX_TOKENS,
                temperature=VLM_TEMPERATURE,
                do_sample=True
            )
        
        # Decode response
        generated_ids_trimmed = [
            out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]
        
        response = self.processor.batch_decode(
            generated_ids_trimmed,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False
        )[0]
        
        return response


class VLMManager:
    """Manager to handle VLM in separate process"""
    def __init__(self, context_queue, query_queue, response_queue):
        self.context_queue = context_queue
        self.query_queue = query_queue
        self.response_queue = response_queue
        self.vlm = VLMHandler()
    
    def run(self, stop_event):
        """Main loop for VLM process"""
        self.vlm.initialize()
        print("✓ VLM ready for queries")
        
        try:
            while not stop_event.is_set():
                # Update context continuously from context builder
                try:
                    context_data = self.context_queue.get(timeout=0.1)
                    self.vlm.update_context(context_data)
                except:
                    pass
                
                # Check for user queries
                try:
                    query = self.query_queue.get_nowait()
                    print(f"\n🤔 Processing: {query}")
                    
                    # Generate response
                    response = self.vlm.query(query)
                    
                    # Send back to user interface
                    self.response_queue.put({
                        'query': query,
                        'response': response,
                        'frame_id': self.vlm.latest_context['frame_id'] if self.vlm.latest_context else None
                    })
                    
                except:
                    pass
                    
        except KeyboardInterrupt:
            pass
        finally:
            print("✓ VLM stopped")


def vlm_process(context_queue, query_queue, response_queue, stop_event):
    """
    Process function to run VLM in separate process
    
    Args:
        context_queue: Queue receiving context from context builder
        query_queue: Queue receiving questions from user interface
        response_queue: Queue to send answers back to user interface
        stop_event: Event to signal when to stop
    """
    manager = VLMManager(context_queue, query_queue, response_queue)
    manager.run(stop_event)