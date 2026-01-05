"""
VisionGPT - Main entry point
Orchestrates all components using multiprocessing
"""

import multiprocessing as mp
import signal
import sys
from config import (FRAME_QUEUE_SIZE, DETECTION_QUEUE_SIZE, 
                   CONTEXT_QUEUE_SIZE, INTERFACE_TYPE)

# Import process functions
from modules.camera import camera_process
from modules.detector import detector_process
from modules.context_builder import context_process
from modules.vlm_handler import vlm_process
from interface.cli import cli_interface
from modules.utils import create_directories


class VisionGPT:
    """Main orchestrator for VisionGPT system"""
    
    def __init__(self):
        # Multiprocessing queues for data flow
        self.frame_queue = mp.Queue(maxsize=FRAME_QUEUE_SIZE)
        self.detection_queue = mp.Queue(maxsize=DETECTION_QUEUE_SIZE)
        self.context_queue = mp.Queue(maxsize=CONTEXT_QUEUE_SIZE)
        self.query_queue = mp.Queue()
        self.response_queue = mp.Queue()
        
        # Event to signal shutdown
        self.stop_event = mp.Event()
        
        # Process list
        self.processes = []
    
    def start(self):
        """Start all processes"""
        print("\n🚀 Starting VisionGPT...\n")
        
        # Create necessary directories
        create_directories()
        
        # Start processes in order
        # 1. Camera capture
        camera_proc = mp.Process(
            target=camera_process,
            args=(self.frame_queue, self.stop_event),
            name="Camera"
        )
        camera_proc.start()
        self.processes.append(camera_proc)
        
        # 2. Object detector
        detector_proc = mp.Process(
            target=detector_process,
            args=(self.frame_queue, self.detection_queue, self.stop_event),
            name="Detector"
        )
        detector_proc.start()
        self.processes.append(detector_proc)
        
        # 3. Context builder
        context_proc = mp.Process(
            target=context_process,
            args=(self.detection_queue, self.context_queue, self.stop_event),
            name="Context"
        )
        context_proc.start()
        self.processes.append(context_proc)
        
        # 4. VLM handler
        vlm_proc = mp.Process(
            target=vlm_process,
            args=(self.context_queue, self.query_queue, 
                  self.response_queue, self.stop_event),
            name="VLM"
        )
        vlm_proc.start()
        self.processes.append(vlm_proc)
        
        print("\n✓ All background processes started")
        print("✓ System ready!\n")
        
        # 5. User interface (runs in main process)
        if INTERFACE_TYPE == "cli":
            cli_interface(self.query_queue, self.response_queue, self.stop_event)
        else:
            print("GUI interface not yet implemented. Using CLI.")
            cli_interface(self.query_queue, self.response_queue, self.stop_event)
    
    def stop(self):
        """Stop all processes gracefully"""
        print("\nStopping all processes...")
        
        # Signal all processes to stop
        self.stop_event.set()
        
        # Wait for processes to finish
        for proc in self.processes:
            proc.join(timeout=3)
            if proc.is_alive():
                print(f"⚠️  Force terminating {proc.name}")
                proc.terminate()
                proc.join()
        
        print("All processes stopped")
        print("\nVisionGPT shut down successfully\n")


def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully"""
    print("\n\nInterrupt signal received...")
    sys.exit(0)


def main():
    """Main entry point"""
    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Create and start VisionGPT
    vision_gpt = VisionGPT()
    
    try:
        vision_gpt.start()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        vision_gpt.stop()


if __name__ == "__main__":
    # Required for Windows multiprocessing
    mp.set_start_method('spawn', force=True)
    main() 