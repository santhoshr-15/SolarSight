import React from 'react';
import { BarChart2, CheckCircle2, AlertOctagon } from 'lucide-react';

export const EvaluationPanel: React.FC = () => {
  return (
    <div className="glass-panel p-8 relative overflow-hidden group">
      <div className="absolute top-0 right-0 w-64 h-64 bg-ai-500/5 rounded-full blur-3xl -mr-32 -mt-32 pointer-events-none transition-opacity duration-700 group-hover:bg-ai-500/10"></div>
      
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-6 mb-8 relative z-10">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-slate-800/80 rounded-xl border border-slate-700 shadow-lg shadow-black/50">
            <BarChart2 className="w-6 h-6 text-ai-400" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-white tracking-tight">Model Performance</h2>
            <p className="text-slate-400 mt-1">Evaluated on the Solar Panel Fault Dataset (8,730 images)</p>
          </div>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900/50 border border-slate-700/50 text-xs font-medium text-slate-300">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          Held-out Set Verified
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 relative z-10">
        {/* Validation Set */}
        <div className="space-y-5">
          <div className="flex items-center gap-3">
            <div className="w-8 h-[1px] bg-slate-700"></div>
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest">Validation Split</h3>
            <div className="flex-1 h-[1px] bg-slate-800"></div>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div className="glass-card p-5 hover:border-slate-600 transition-colors">
              <div className="text-xs font-medium text-slate-500 mb-2 uppercase tracking-wider">Precision</div>
              <div className="text-3xl font-light text-white flex items-baseline gap-1">
                52.9<span className="text-lg text-slate-500">%</span>
              </div>
            </div>
            <div className="glass-card p-5 hover:border-slate-600 transition-colors">
              <div className="text-xs font-medium text-slate-500 mb-2 uppercase tracking-wider">Recall</div>
              <div className="text-3xl font-light text-white flex items-baseline gap-1">
                56.0<span className="text-lg text-slate-500">%</span>
              </div>
            </div>
            <div className="glass-card p-5 hover:border-slate-600 transition-colors">
              <div className="text-xs font-medium text-solar-500/80 mb-2 uppercase tracking-wider">mAP@50</div>
              <div className="text-3xl font-light text-white flex items-baseline gap-1">
                51.1<span className="text-lg text-slate-500">%</span>
              </div>
            </div>
            <div className="glass-card p-5 hover:border-slate-600 transition-colors">
              <div className="text-xs font-medium text-ai-500/80 mb-2 uppercase tracking-wider">mAP@50-95</div>
              <div className="text-3xl font-light text-white flex items-baseline gap-1">
                34.8<span className="text-lg text-slate-500">%</span>
              </div>
            </div>
          </div>
        </div>

        {/* Test Set */}
        <div className="space-y-5">
          <div className="flex items-center gap-3">
            <div className="w-8 h-[1px] bg-slate-700"></div>
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest">Test Split (Unseen)</h3>
            <div className="flex-1 h-[1px] bg-slate-800"></div>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div className="glass-card p-5 bg-slate-800/40 hover:border-slate-600 transition-colors">
              <div className="text-xs font-medium text-slate-500 mb-2 uppercase tracking-wider">Precision</div>
              <div className="text-3xl font-light text-white flex items-baseline gap-1">
                44.2<span className="text-lg text-slate-500">%</span>
              </div>
            </div>
            <div className="glass-card p-5 bg-slate-800/40 hover:border-slate-600 transition-colors">
              <div className="text-xs font-medium text-slate-500 mb-2 uppercase tracking-wider">Recall</div>
              <div className="text-3xl font-light text-white flex items-baseline gap-1">
                51.4<span className="text-lg text-slate-500">%</span>
              </div>
            </div>
            <div className="glass-card p-5 bg-slate-800/40 border-solar-500/20 hover:border-solar-500/40 transition-colors relative overflow-hidden">
              <div className="absolute inset-0 bg-solar-500/5"></div>
              <div className="relative z-10 text-xs font-semibold text-solar-400 mb-2 uppercase tracking-wider">mAP@50</div>
              <div className="relative z-10 text-3xl font-medium text-white flex items-baseline gap-1">
                42.4<span className="text-lg text-solar-500/50">%</span>
              </div>
            </div>
            <div className="glass-card p-5 bg-slate-800/40 border-ai-500/20 hover:border-ai-500/40 transition-colors relative overflow-hidden">
              <div className="absolute inset-0 bg-ai-500/5"></div>
              <div className="relative z-10 text-xs font-semibold text-ai-400 mb-2 uppercase tracking-wider">mAP@50-95</div>
              <div className="relative z-10 text-3xl font-medium text-white flex items-baseline gap-1">
                27.1<span className="text-lg text-ai-500/50">%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div className="mt-8 p-4 rounded-xl bg-slate-900/60 border border-slate-700/50 flex items-start gap-4">
        <AlertOctagon className="w-5 h-5 text-slate-400 flex-shrink-0 mt-0.5" />
        <p className="text-sm text-slate-400 leading-relaxed">
          <strong className="text-slate-300">Model Limitation:</strong> The generalization gap between validation and test sets reflects the challenge of identifying ambiguous visual faults. Bounding-box localization precision (indicated by the mAP@50-95 drop) is constrained by the conversion of source polygon annotations into axis-aligned boxes.
        </p>
      </div>
    </div>
  );
};
