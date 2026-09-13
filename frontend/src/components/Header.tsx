import React from 'react';
import { Activity, BookOpen, Code2 } from 'lucide-react';
import { API_BASE_URL } from '../api';

interface Props {
  apiStatus: 'checking' | 'online' | 'offline';
}

export const Header: React.FC<Props> = ({ apiStatus }) => {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-6 py-4 bg-slate-950/80 backdrop-blur-xl border-b border-slate-800/50 shadow-lg">
      <div className="flex items-center space-x-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-solar-500/10 border border-solar-500/30 flex items-center justify-center relative group overflow-hidden">
            <div className="absolute inset-0 bg-solar-500/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300"></div>
            <Activity className="w-6 h-6 text-solar-400 relative z-10" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
              SolarSight <span className="text-[10px] font-black bg-ai-500 text-white px-2 py-0.5 rounded uppercase tracking-widest">AI</span>
            </h1>
            <p className="text-xs text-slate-400 font-medium tracking-wider uppercase mt-0.5">Vision Intelligence</p>
          </div>
        </div>
        
        <div className="hidden sm:flex items-center space-x-2 bg-slate-900/50 px-3 py-1.5 rounded-full border border-slate-700/50 backdrop-blur-md">
          <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">System Status</span>
          {apiStatus === 'checking' && <span className="flex items-center text-xs font-semibold text-yellow-500 gap-1.5"><span className="w-2 h-2 rounded-full bg-yellow-500 animate-pulse"></span> Connecting</span>}
          {apiStatus === 'online' && <span className="flex items-center text-xs font-semibold text-emerald-400 gap-1.5"><span className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.8)]"></span> Online</span>}
          {apiStatus === 'offline' && <span className="flex items-center text-xs font-semibold text-rose-500 gap-1.5"><span className="w-2 h-2 rounded-full bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.8)]"></span> Offline</span>}
        </div>
      </div>

      <div className="flex items-center space-x-4">
        <a 
          href="https://github.com/santhoshr-15/SolarSight" 
          target="_blank" 
          rel="noreferrer" 
          className="hidden sm:flex items-center space-x-2 text-sm font-medium text-slate-400 hover:text-white transition-colors"
        >
          <Code2 className="w-4 h-4" />
          <span>GitHub</span>
        </a>
      </div>
    </header>
  );
};
