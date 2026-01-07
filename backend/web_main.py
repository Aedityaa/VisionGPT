import cv2
import base64
import asyncio
import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from main import VisionGPT  # Importing your existing class

# Initialize the app
app = FastAPI()

# Allow React to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global reference to your system
vision_system = VisionGPT()

@app.on_event("startup")
def start_vision_system():
    # Start the existing multiprocessing pipeline
    vision_system.start()

@app.on_event("shutdown")
def stop_vision_system():
    vision_system.stop()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    try:
        while True:
            # 1. READ FROM YOUR EXISTING QUEUES
            # Check for new video frames + context
            if not vision_system.context_queue.empty():
                data = vision_system.context_queue.get()
                
                # Draw boxes on the frame for the UI
                frame = data['frame']
                # (Optional: Add your drawing logic here using cv2.rectangle based on data['objects'])
                
                # Compress to JPEG for smoother streaming
                _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 60])
                jpg_as_text = base64.b64encode(buffer).decode('utf-8')
                
                # Send to React
                await websocket.send_json({
                    "type": "video_update",
                    "image": jpg_as_text,
                    "objects": data['objects'],
                    "relationships": data['relationships'] # e.g., ['cup on table']
                })
            
            # Check for VLM responses to your questions
            if not vision_system.response_queue.empty():
                resp = vision_system.response_queue.get()
                await websocket.send_json({
                    "type": "chat_response",
                    "text": resp['response']
                })
            
            # Check if User sent a message FROM the UI
            try:
                # We use a very short timeout to not block the video loop
                data = await asyncio.wait_for(websocket.receive_json(), timeout=0.01)
                if data.get("type") == "user_query":
                    print(f"User asked: {data['text']}")
                    vision_system.query_queue.put(data['text'])
            except asyncio.TimeoutError:
                pass # No message from user, keep looping
            
            await asyncio.sleep(0.01) # Small sleep to prevent CPU spike

    except Exception as e:
        print(f"Client disconnected: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)