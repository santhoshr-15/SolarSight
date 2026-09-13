import React from 'react';
import { BarChart2 } from 'lucide-react';

export const EvaluationPanel: React.FC = () => {
  return (
    <div className="glass-panel p-6">
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 bg-cyan-500/10 rounded-lg border border-cyan-500/20">
          <BarChart2 className="w-5 h-5 text-cyan-400" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-white">Model Quality</h2>
          <p className="text-sm text-slate-400">Offline evaluation metrics on the Solar Panel Fault Dataset v2.</p>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-4">
          <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider bg-slate-900 py-1.5 px-3 rounded inline-block border border-slate-800">Validation Set</h3>
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-800">
              <div className="text-xs text-slate-500 mb-1">Precision</div>
              <div className="text-2xl font-semibold text-white">52.9%</div>
            </div>
            <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-800">
              <div className="text-xs text-slate-500 mb-1">Recall</div>
              <div className="text-2xl font-semibold text-white">56.0%</div>
            </div>
            <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-800">
              <div className="text-xs text-slate-500 mb-1">mAP50</div>
              <div className="text-2xl font-semibold text-white">51.1%</div>
            </div>
            <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-800">
              <div className="text-xs text-slate-500 mb-1">mAP50-95</div>
              <div className="text-2xl font-semibold text-white">34.8%</div>
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider bg-slate-900 py-1.5 px-3 rounded inline-block border border-slate-800">Held-Out Test Set</h3>
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-800">
              <div className="text-xs text-slate-500 mb-1">Precision</div>
              <div className="text-2xl font-semibold text-white">44.2%</div>
            </div>
            <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-800">
              <div className="text-xs text-slate-500 mb-1">Recall</div>
              <div className="text-2xl font-semibold text-white">51.4%</div>
            </div>
            <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-800">
              <div className="text-xs text-slate-500 mb-1">mAP50</div>
              <div className="text-2xl font-semibold text-white">42.4%</div>
            </div>
            <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-800">
              <div className="text-xs text-slate-500 mb-1">mAP50-95</div>
              <div className="text-2xl font-semibold text-white">27.1%</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
