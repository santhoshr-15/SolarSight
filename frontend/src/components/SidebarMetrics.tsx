import React from 'react';
import { DetectionResponse } from '../types';
import { Crosshair, Layers, Zap, Cpu } from 'lucide-react';

interface Props {
  result: DetectionResponse;
  latencyMs: number;
}

const colors: Record<string, string> = {
  'Bird Drop': 'bg-rose-500',
  'Defective': 'bg-orange-500',
  'Dusty': 'bg-solar-500',
  'Non Defective': 'bg-emerald-500',
  'Physical Damage': 'bg-purple-500',
  'Snow': 'bg-ai-500',
};

export const SidebarMetrics: React.FC<Props> = ({ result, latencyMs }) => {
  return (
    <div className="flex flex-col gap-6 w-full h-full">
      
      {/* Summary Card */}
      <div className="glass-panel p-6 relative overflow-hidden group">
        <div className="absolute top-0 right-0 w-32 h-32 bg-solar-500/10 rounded-full blur-2xl -mr-16 -mt-16 pointer-events-none"></div>
        <h3 className="text-[11px] font-bold text-slate-400 uppercase tracking-widest mb-6 flex items-center gap-2 relative z-10">
          <Layers className="w-4 h-4 text-solar-400" /> Detection Summary
        </h3>
        <div className="flex justify-between items-end mb-8 relative z-10">
          <div className="text-5xl font-light text-white tracking-tight">
            {result.total_detections}
          </div>
          <div className="text-sm font-medium text-slate-400 uppercase tracking-wider mb-1">Found</div>
        </div>
        
        <div className="space-y-4 relative z-10">
          {Object.entries(result.counts).map(([cls, count]) => (
            <div key={cls} className="flex items-center justify-between group/item">
              <div className="flex items-center gap-3">
                <div className={`w-3 h-3 rounded-sm ${colors[cls] || 'bg-ai-500'} shadow-lg`}></div>
                <span className="text-sm font-medium text-slate-300 group-hover/item:text-white transition-colors">{cls}</span>
              </div>
              <span className="text-sm font-bold text-white bg-slate-800/80 px-2 py-0.5 rounded-md border border-slate-700">{count}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Confidence Profile */}
      <div className="glass-panel p-6 flex-1 min-h-[300px] flex flex-col relative overflow-hidden">
        <h3 className="text-[11px] font-bold text-slate-400 uppercase tracking-widest mb-6 flex items-center gap-2 relative z-10">
          <Crosshair className="w-4 h-4 text-ai-400" /> Confidence Profile
        </h3>
        <div className="space-y-5 overflow-y-auto pr-3 flex-1 custom-scrollbar relative z-10">
          {result.detections.sort((a, b) => b.confidence - a.confidence).map((det, idx) => (
            <div key={idx} className="space-y-2">
              <div className="flex justify-between text-xs">
                <span className="text-slate-300 font-medium uppercase tracking-wider">{det.class_name}</span>
                <span className="text-white font-bold">{Math.round(det.confidence * 100)}%</span>
              </div>
              <div className="w-full bg-slate-900/80 rounded-full h-2 overflow-hidden border border-slate-800">
                <div 
                  className={`h-full rounded-full ${colors[det.class_name] || 'bg-ai-500'} relative`} 
                  style={{ width: `${det.confidence * 100}%` }}
                >
                  <div className="absolute inset-0 bg-white/20 w-full h-full"></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Technical Metrics */}
      <div className="glass-panel p-6 bg-slate-900/60 border-t border-slate-700/50 relative overflow-hidden">
        <h3 className="text-[11px] font-bold text-slate-400 uppercase tracking-widest mb-6 flex items-center gap-2">
          <Zap className="w-4 h-4 text-yellow-500" /> Trace Metrics
        </h3>
        <div className="grid grid-cols-2 gap-y-6 gap-x-4">
          <div>
            <div className="text-[10px] uppercase tracking-widest text-slate-500 mb-1">Architecture</div>
            <div className="text-sm font-bold text-slate-200 flex items-center gap-1.5"><Cpu className="w-3.5 h-3.5 text-slate-400" /> RT-DETR-L</div>
          </div>
          <div>
            <div className="text-[10px] uppercase tracking-widest text-slate-500 mb-1">Resolution</div>
            <div className="text-sm font-bold text-slate-200">640<span className="text-slate-500 mx-0.5">×</span>640</div>
          </div>
          <div>
            <div className="text-[10px] uppercase tracking-widest text-slate-500 mb-1">Total Latency</div>
            <div className="text-sm font-bold text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded inline-flex">{latencyMs} ms</div>
          </div>
          <div>
            <div className="text-[10px] uppercase tracking-widest text-slate-500 mb-1">Trace</div>
            <div className="text-xs font-mono font-bold text-slate-300 bg-slate-950 px-2 py-1 rounded border border-slate-800">POST /detect</div>
          </div>
        </div>
      </div>
    </div>
  );
};
