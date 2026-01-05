"""
Command-Line Interface for VisionGPT
Simple text-based interface for asking questions
"""

import sys
import threading


class CLI:
    def __init__(self, query_queue, response_queue):
        """
        Args:
            query_queue: Queue to send questions to VLM
            response_queue: Queue to receive answers from VLM
        """
        self.query_queue = query_queue
        self.response_queue = response_queue
        self.running = False
        self.response_thread = None
    
    def start(self):
        """Start CLI interface"""
        self.running = True
        
        # Start response listener in separate thread
        self.response_thread = threading.Thread(target=self._response_listener, daemon=True)
        self.response_thread.start()
        
        self._print_welcome()
        self._input_loop()
    
    def _print_welcome(self):
        """Print welcome message"""
        print("\n" + "="*60)
        print("VisionGPT - Real-time Vision Assistant")
        print("="*60)
        print("\nCamera is running and analyzing the scene...")
        print("Type your questions and press Enter.")
        print("Commands: 'quit', 'exit', 'help'\n")
    
    def _print_help(self):
        """Print help message"""
        print("\nHelp:")
        print("  - Ask any question about what the camera sees")
        print("  - Examples:")
        print("    • 'What objects do you see?'")
        print("    • 'How many people are there?'")
        print("    • 'What is on the table?'")
        print("    • 'Describe the scene'")
        print("  - Type 'quit' or 'exit' to stop")
        print()
    
    def _response_listener(self):
        """Listen for responses from VLM in separate thread"""
        while self.running:
            try:
                response_data = self.response_queue.get(timeout=0.5)
                self._display_response(response_data)
            except:
                continue
    
    def _display_response(self, response_data):
        """Display VLM response"""
        print("\n" + "-"*60)
        print(f"Answer (Frame {response_data['frame_id']}):")
        print(f"{response_data['response']}")
        print("-"*60)
        print("\n>>> ", end='', flush=True)
    
    def _input_loop(self):
        """Main input loop"""
        try:
            while self.running:
                # Get user input
                print(">>> ", end='', flush=True)
                user_input = input().strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\nShutting down VisionGPT...")
                    self.running = False
                    break
                
                if user_input.lower() == 'help':
                    self._print_help()
                    continue
                
                # Send query to VLM
                print("Processing your question...")
                self.query_queue.put(user_input)
                
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted by user. Shutting down...")
            self.running = False
        except EOFError:
            self.running = False
    
    def stop(self):
        """Stop CLI"""
        self.running = False
        if self.response_thread:
            self.response_thread.join(timeout=1)


def cli_interface(query_queue, response_queue, stop_event):
    """
    Run CLI interface
    
    Args:
        query_queue: Queue to send questions
        response_queue: Queue to receive answers
        stop_event: Event to signal system shutdown
    """
    cli = CLI(query_queue, response_queue)
    
    try:
        cli.start()
    finally:
        cli.stop()
        stop_event.set()  # Signal all processes to stop