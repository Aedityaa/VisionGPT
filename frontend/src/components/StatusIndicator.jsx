// import { Activity, Wifi, WifiOff, Eye } from 'lucide-react';

// export default function StatusIndicator({ isConnected, fps, detections }) {
//   return (
//     <div className="flex items-center gap-4">
//       {/* Connection Status */}
//       <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg ${
//         isConnected 
//           ? 'bg-green-500/20 border border-green-500/30' 
//           : 'bg-red-500/20 border border-red-500/30'
//       }`}>
//         {isConnected ? (
//           <Wifi size={16} className="text-green-400" />
//         ) : (
//           <WifiOff size={16} className="text-red-400" />
//         )}
//         <span className={`text-xs font-medium ${
//           isConnected ? 'text-green-400' : 'text-red-400'
//         }`}>
//           {isConnected ? 'Connected' : 'Disconnected'}
//         </span>
//       </div>

//       {/* FPS Counter */}
//       {isConnected && (
//         <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-cyan-500/20 border border-cyan-500/30">
//           <Activity size={16} className="text-cyan-400" />
//           <span className="text-xs font-medium text-cyan-400">
//             {fps} FPS
//           </span>
//         </div>
//       )}

//       {/* Detection Count */}
//       {isConnected && detections > 0 && (
//         <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-blue-500/20 border border-blue-500/30">
//           <Eye size={16} className="text-blue-400" />
//           <span className="text-xs font-medium text-blue-400">
//             {detections} detected
//           </span>
//         </div>
//       )}
//     </div>
//   );
// }

import { Activity, Wifi, WifiOff, Eye } from 'lucide-react';

export default function StatusIndicator({ isConnected, fps, detections }) {
  return (
    <div className="flex items-center gap-4">
      {/* Connection Status */}
      <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg ${
        isConnected 
          ? 'bg-green-500/20 border border-green-500/30' 
          : 'bg-red-500/20 border border-red-500/30'
      }`}>
        {isConnected ? (
          <Wifi size={16} className="text-green-400" />
        ) : (
          <WifiOff size={16} className="text-red-400" />
        )}
        <span className={`text-xs font-medium ${
          isConnected ? 'text-green-400' : 'text-red-400'
        }`}>
          {isConnected ? 'Connected' : 'Disconnected'}
        </span>
      </div>

      {/* FPS Counter */}
      {isConnected && (
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-cyan-500/20 border border-cyan-500/30">
          <Activity size={16} className="text-cyan-400" />
          <span className="text-xs font-medium text-cyan-400">
            {fps} FPS
          </span>
        </div>
      )}

      {/* Detection Count */}
      {isConnected && detections > 0 && (
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-blue-500/20 border border-blue-500/30">
          <Eye size={16} className="text-blue-400" />
          <span className="text-xs font-medium text-blue-400">
            {detections} detected
          </span>
        </div>
      )}
    </div>
  );
}