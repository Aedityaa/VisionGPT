import { useRef, useEffect, useState } from 'react';
import Webcam from 'react-webcam';
import { Camera, AlertCircle } from 'lucide-react';

export default function VideoFeed({ isStreaming, onDetections, onFpsUpdate }) {
  const webcamRef = useRef(null);
  const canvasRef = useRef(null);
  const [error, setError] = useState(null);
  const [mockDetections, setMockDetections] = useState([]);

  // Simulate detections for demo (replace with actual backend calls)
  useEffect(() => {
    if (!isStreaming) {
      setMockDetections([]);
      return;
    }

    const interval = setInterval(() => {
      // Generate random bounding boxes for demo
      const detections = [
        { 
          label: 'person', 
          confidence: 0.95,
          bbox: { x: 100, y: 80, width: 200, height: 300 },
          color: '#3b82f6'
        },
        { 
          label: 'laptop', 
          confidence: 0.87,
          bbox: { x: 350, y: 250, width: 180, height: 120 },
          color: '#10b981'
        },
        { 
          label: 'cup', 
          confidence: 0.78,
          bbox: { x: 500, y: 200, width: 60, height: 80 },
          color: '#f59e0b'
        }
      ];
      
      setMockDetections(detections);
      onDetections(detections);
      onFpsUpdate(Math.floor(Math.random() * 5) + 25); // Mock FPS 25-30
    }, 1000);

    return () => clearInterval(interval);
  }, [isStreaming, onDetections, onFpsUpdate]);

  // Draw bounding boxes on canvas
  useEffect(() => {
    if (!canvasRef.current || !webcamRef.current) return;

    const canvas = canvasRef.current;
    const video = webcamRef.current.video;
    
    if (!video) return;

    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;

    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw bounding boxes
    mockDetections.forEach(detection => {
      const { bbox, label, confidence, color } = detection;
      
      ctx.strokeStyle = color;
      ctx.lineWidth = 3;
      ctx.strokeRect(bbox.x, bbox.y, bbox.width, bbox.height);
      
      // Label background
      ctx.fillStyle = color;
      ctx.fillRect(bbox.x, bbox.y - 25, 150, 25);
      
      // Label text
      ctx.fillStyle = 'white';
      ctx.font = 'bold 14px Arial';
      ctx.fillText(`${label} ${(confidence * 100).toFixed(0)}%`, bbox.x + 5, bbox.y - 7);
    });
  }, [mockDetections]);

  const handleUserMedia = () => {
    setError(null);
  };

  const handleUserMediaError = (err) => {
    console.error('Camera error:', err);
    setError('Unable to access camera. Please check permissions.');
  };

  return (
    <div className="relative w-full h-full flex items-center justify-center bg-black rounded-lg overflow-hidden">
      {!isStreaming ? (
        // Camera off state
        <div className="flex flex-col items-center justify-center gap-4 text-slate-400">
          <Camera size={64} className="opacity-30" />
          <p className="text-lg">Camera is off</p>
          <p className="text-sm">Click "Start Camera" to begin</p>
        </div>
      ) : error ? (
        // Error state
        <div className="flex flex-col items-center justify-center gap-4 text-red-400">
          <AlertCircle size={64} />
          <p className="text-lg font-semibold">Camera Error</p>
          <p className="text-sm text-center max-w-md">{error}</p>
        </div>
      ) : (
        // Active camera feed
        <>
          <Webcam
            ref={webcamRef}
            audio={false}
            screenshotFormat="image/jpeg"
            className="absolute inset-0 w-full h-full object-cover"
            onUserMedia={handleUserMedia}
            onUserMediaError={handleUserMediaError}
            mirrored={true}
          />
          
          {/* Bounding box overlay canvas */}
          <canvas
            ref={canvasRef}
            className="absolute inset-0 w-full h-full object-cover pointer-events-none"
          />

          {/* Detection count overlay */}
          {mockDetections.length > 0 && (
            <div className="absolute top-4 right-4 bg-black/70 backdrop-blur-sm px-4 py-2 rounded-lg border border-cyan-500/30">
              <p className="text-cyan-400 text-sm font-semibold">
                {mockDetections.length} objects detected
              </p>
            </div>
          )}
        </>
      )}
    </div>
  );
}