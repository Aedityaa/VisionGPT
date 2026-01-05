// import { useState } from 'react'
// import reactLogo from './assets/react.svg'
// import viteLogo from '/vite.svg'
// import './App.css'

// function App() {
//   const [count, setCount] = useState(0)

//   return (
//     <>
//       <div>
//         <a href="https://vite.dev" target="_blank">
//           <img src={viteLogo} className="logo" alt="Vite logo" />
//         </a>
//         <a href="https://react.dev" target="_blank">
//           <img src={reactLogo} className="logo react" alt="React logo" />
//         </a>
//       </div>
//       <h1>Vite + React</h1>
//       <div className="card">
//         <button onClick={() => setCount((count) => count + 1)}>
//           count is {count}
//         </button>
//         <p>
//           Edit <code>src/App.jsx</code> and save to test HMR
//         </p>
//       </div>
//       <p className="read-the-docs">
//         Click on the Vite and React logos to learn more
//       </p>
//     </>
//   )
// }

// export default App

import { useState, useEffect } from 'react';
import { Camera, Video, VideoOff, Activity } from 'lucide-react';
import VideoFeed from './components/VideoFeed';
import ChatInterface from './components/ChatInterface';
import ControlPanel from './components/ControlPanel';
import StatusIndicator from './components/StatusIndicator';

export default function App() {
  const [isStreaming, setIsStreaming] = useState(false);
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hello! I can see your video feed. Ask me anything about what\'s in the camera view!',
      timestamp: new Date().toLocaleTimeString()
    }
  ]);
  const [detections, setDetections] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [fps, setFps] = useState(0);

  const handleToggleStream = () => {
    setIsStreaming(!isStreaming);
    setIsConnected(!isStreaming);
  };

  const handleNewMessage = (message) => {
    setMessages(prev => [...prev, {
      role: 'user',
      content: message,
      timestamp: new Date().toLocaleTimeString()
    }]);

    // Simulate AI response (replace with actual API call)
    setTimeout(() => {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `I can see ${detections.length} objects in the frame. The main items are: person, laptop, and cup.`,
        timestamp: new Date().toLocaleTimeString()
      }]);
    }, 1000);
  };

  const handleDetections = (newDetections) => {
    setDetections(newDetections);
  };

  return (
    <div className="h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white flex flex-col overflow-hidden">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-4 border-b border-white/10 bg-slate-900/50 backdrop-blur-md">
        <div className="flex items-center gap-3">
          <div className="bg-gradient-to-br from-cyan-500 to-blue-600 p-2.5 rounded-lg">
            <Camera className="text-white" size={24} />
          </div>
          <div>
            <h1 className="font-bold text-xl bg-gradient-to-r from-white to-slate-300 bg-clip-text text-transparent">
              VLM Live Feed Assistant
            </h1>
            <p className="text-xs text-slate-400">Real-time Vision Language Model</p>
          </div>
        </div>
        <StatusIndicator isConnected={isConnected} fps={fps} detections={detections.length} />
      </header>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Side: Video Feed (60%) */}
        <div className="w-3/5 flex flex-col p-4 gap-4">
          <div className="flex-1 bg-slate-800/50 rounded-xl border border-white/10 overflow-hidden shadow-2xl">
            <VideoFeed 
              isStreaming={isStreaming} 
              onDetections={handleDetections}
              onFpsUpdate={setFps}
            />
          </div>
          <ControlPanel 
            isStreaming={isStreaming} 
            onToggle={handleToggleStream}
            detectionCount={detections.length}
          />
        </div>

        {/* Right Side: Chat Interface (40%) */}
        <div className="w-2/5 flex flex-col border-l border-white/10 bg-slate-900/30">
          <ChatInterface 
            messages={messages}
            onSendMessage={handleNewMessage}
            isStreaming={isStreaming}
          />
        </div>
      </div>
    </div>
  );
}