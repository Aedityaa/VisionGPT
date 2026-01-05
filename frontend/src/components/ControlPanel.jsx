import { Video, VideoOff } from 'lucide-react';

export default function ControlPanel({ isStreaming, onToggle, detectionCount }) {
  return (
    <div className="bg-slate-800/50 rounded-xl border border-white/10 p-4">
      <div className="flex items-center justify-between">
        {/* Camera Controls */}
        <div className="flex items-center gap-4">
          <button
            onClick={onToggle}
            className={`flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-all transform active:scale-95 ${
              isStreaming
                ? 'bg-red-600 hover:bg-red-700 text-white'
                : 'bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white'
            }`}
          >
            {isStreaming ? (
              <>
                <VideoOff size={20} />
                Stop Camera
              </>
            ) : (
              <>
                <Video size={20} />
                Start Camera
              </>
            )}
          </button>

          {/* Status Badge */}
          <div className={`flex items-center gap-2 px-4 py-2 rounded-lg ${
            isStreaming 
              ? 'bg-green-500/20 border border-green-500/30' 
              : 'bg-slate-700/50 border border-white/10'
          }`}>
            <div className={`w-2 h-2 rounded-full ${
              isStreaming ? 'bg-green-400 animate-pulse' : 'bg-slate-500'
            }`} />
            <span className={`text-sm font-medium ${
              isStreaming ? 'text-green-400' : 'text-slate-400'
            }`}>
              {isStreaming ? 'Live' : 'Offline'}
            </span>
          </div>
        </div>

        {/* Detection Stats */}
        <div className="flex items-center gap-6">
          <div className="text-right">
            <p className="text-xs text-slate-400">Objects Detected</p>
            <p className="text-2xl font-bold text-cyan-400">{detectionCount}</p>
          </div>
        </div>
      </div>

      {/* Additional Info */}
      {isStreaming && (
        <div className="mt-4 pt-4 border-t border-white/10">
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-2 text-slate-400">
              <div className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse" />
              Processing video feed
            </div>
            <div className="text-slate-400">
              Resolution: 640x480
            </div>
          </div>
        </div>
      )}
    </div>
  );
}