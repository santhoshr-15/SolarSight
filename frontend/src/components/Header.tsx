import React, { useEffect, useState } from 'react';
import { Activity, BookOpen, Code } from 'lucide-react';
import { api, API_BASE_URL } from '../api';
import { HealthResponse } from '../types';

export const Header: React.FC = () => {
  const [health, setHealth] = useState<'checking' | 'online' | 'offline'>('checking');

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await api.get<HealthResponse>('/health');
        if (res.data.status === 'ok') {
          setHealth('online');
        } else {
          setHealth('offline');
        }
      } catch (e) {
        setHealth('offline');
      }
    };
    
    checkHealth();
    // Poll every 30s
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="flex items-center justify-between px-6 py-4 bg-slate-900 border-b border-slate-800">
      <div className="flex items-center space-x-6">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            <Activity className="w-5 h-5 text-cyan-400" />
            SolarSight
          </h1>
          <p className="text-xs text-slate-400 font-medium tracking-wider uppercase mt-0.5">Solar Panel Intelligence</p>
        </div>
        
        <div className="flex items-center space-x-2 bg-slate-950 px-3 py-1.5 rounded-full border border-slate-800">
          <span className="text-xs font-semibold text-slate-400">API Status:</span>
          {health === 'checking' && <span className="flex items-center text-xs text-yellow-500 gap-1"><span className="w-2 h-2 rounded-full bg-yellow-500 animate-pulse"></span> Checking</span>}
          {health === 'online' && <span className="flex items-center text-xs text-emerald-400 gap-1"><span className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]"></span> Online</span>}
          {health === 'offline' && <span className="flex items-center text-xs text-rose-500 gap-1"><span className="w-2 h-2 rounded-full bg-rose-500"></span> Offline</span>}
        </div>
      </div>

      <div className="flex items-center space-x-4">
        <a href="https://github.com/santhoshr-15/SolarSight" target="_blank" rel="noreferrer" className="flex items-center space-x-2 text-sm font-medium text-slate-300 hover:text-white transition-colors">
          <Code className="w-4 h-4" />
          <span>GitHub</span>
        </a>
        <a href={`${API_BASE_URL}/docs`} target="_blank" rel="noreferrer" className="flex items-center space-x-2 text-sm font-medium bg-cyan-950/40 text-cyan-400 hover:bg-cyan-900/60 border border-cyan-800/50 px-3 py-1.5 rounded-md transition-colors">
          <BookOpen className="w-4 h-4" />
          <span>API Docs</span>
        </a>
      </div>
    </header>
  );
};
