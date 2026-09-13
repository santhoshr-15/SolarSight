import React from 'react';
import { DetectionResponse } from '../types';
import { Crosshair, Layers, Zap } from 'lucide-react';

interface Props {
  result: DetectionResponse;
  latencyMs: number;
}

const colors: Record<string, string> = {
  'Bird Drop': 'bg-red-500',
  'Defective': 'bg-orange-500',
  'Dusty': 'bg-yellow-500',
  'Non Defective': 'bg-green-500',
  'Physical Damage': 'bg-purple-500',
  'Snow': 'bg-blue-500',
};

export const SidebarMetrics: React.FC<Props> = ({ result, latencyMs }) => {
  return (
    <div className="flex flex-col gap-4 w-full h-full">
      <div className="glass-panel p-5">
        <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4 flex items-center gap-2">
          <Layers className="w-4 h-4" /> Detection Summary
        </h3>
        <div className="flex justify-between items-end mb-6">
          <div className="text-4xl font-bold text-white">{result.total_detections}</div>
          <div className="text-sm text-slate-400">Total Objects</div>
        </div>
        
        <div className="space-y-3">
          {Object.entries(result.counts).map(([cls, count]) => (
            <div key={cls} className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className={`w-2.5 h-2.5 rounded-full ${colors[cls] || 'bg-cyan-500'}`}></div>
                <span className="text-sm text-slate-200">{cls}</span>
              </div>
              <span className="text-sm font-medium text-white">{count}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="glass-panel p-5 flex-1 min-h-0 flex flex-col">
        <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4 flex items-center gap-2">
          <Crosshair className="w-4 h-4" /> Confidence Profile
        </h3>
        <div className="space-y-4 overflow-y-auto pr-2 flex-1 custom-scrollbar">
          {result.detections.sort((a, b) => b.confidence - a.confidence).map((det, idx) => (
            <div key={idx} className="space-y-1">
              <div className="flex justify-between text-xs">
                <span className="text-slate-300">{det.class_name}</span>
                <span className="text-white font-medium">{Math.round(det.confidence * 100)}%</span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                <div 
                  className={`h-full rounded-full ${colors[det.class_name] || 'bg-cyan-500'}`} 
                  style={{ width: `${det.confidence * 100}%` }}
                ></div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="glass-panel p-5 bg-slate-900/40 border-t-0">
        <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4 flex items-center gap-2">
          <Zap className="w-4 h-4 text-yellow-500" /> Technical Metrics
        </h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <div className="text-xs text-slate-500">Model</div>
            <div className="text-sm font-medium text-slate-200">RT-DETR-L</div>
          </div>
          <div>
            <div className="text-xs text-slate-500">Input Size</div>
            <div className="text-sm font-medium text-slate-200">640x640</div>
          </div>
          <div>
            <div className="text-xs text-slate-500">Client Latency</div>
            <div className="text-sm font-medium text-emerald-400">{latencyMs} ms</div>
          </div>
          <div>
            <div className="text-xs text-slate-500">Endpoint</div>
            <div className="text-sm font-medium text-slate-200 font-mono">POST /detect</div>
          </div>
        </div>
      </div>
    </div>
  );
};
