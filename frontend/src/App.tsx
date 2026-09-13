import React, { useState } from 'react';
import { Header } from './components/Header';
import { UploadZone } from './components/UploadZone';
import { DetectionViewer } from './components/DetectionViewer';
import { SidebarMetrics } from './components/SidebarMetrics';
import { ReasoningConsole } from './components/ReasoningConsole';
import { EvaluationPanel } from './components/EvaluationPanel';
import { api } from './api';
import { DetectionResponse } from './types';
import { AlertTriangle, Info } from 'lucide-react';

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [detectionResult, setDetectionResult] = useState<DetectionResponse | null>(null);
  const [isDetecting, setIsDetecting] = useState(false);
  const [latency, setLatency] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const handleImageSelect = async (selectedFile: File) => {
    setFile(selectedFile);
    setPreviewUrl(URL.createObjectURL(selectedFile));
    setDetectionResult(null);
    setError(null);
    setIsDetecting(true);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      
      const start = performance.now();
      const res = await api.post<DetectionResponse>('/detect', formData);
      const end = performance.now();
      
      setLatency(Math.round(end - start));
      setDetectionResult(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Detection failed. Please check backend connection.");
    } finally {
      setIsDetecting(false);
    }
  };

  const handleDemoMode = async () => {
    try {
      const response = await fetch('/real_world_solar_test.png');
      const blob = await response.blob();
      const demoFile = new File([blob], 'real_world_solar_test.png', { type: 'image/png' });
      handleImageSelect(demoFile);
    } catch (e) {
      setError("Demo image not found on server.");
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col">
      <Header />
      
      <main className="flex-1 p-6 max-w-7xl mx-auto w-full flex flex-col gap-8">
        
        <div className="flex flex-col lg:flex-row items-start gap-6">
          <div className="w-full lg:w-2/3 flex flex-col gap-6">
            <div className="glass-panel p-6 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
              <div>
                <h2 className="text-xl font-bold text-white">AI-Powered Solar Panel Inspection</h2>
                <p className="text-sm text-slate-400">Detect panel faults, inspect model confidence, and ask constrained questions.</p>
              </div>
              {!file && (
                <button onClick={handleDemoMode} className="flex-shrink-0 text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-4 py-2 rounded-lg border border-slate-700 transition-colors flex items-center gap-2">
                  <Info className="w-4 h-4 text-cyan-400" />
                  Run Demo Image
                </button>
              )}
            </div>

            {error && (
              <div className="bg-rose-500/10 border border-rose-500/30 p-4 rounded-lg flex gap-3 text-rose-400">
                <AlertTriangle className="w-5 h-5 flex-shrink-0" />
                <p className="text-sm">{error}</p>
              </div>
            )}

            {!file ? (
              <UploadZone onImageSelect={handleImageSelect} isLoading={isDetecting} />
            ) : (
              <div className="relative group">
                <button 
                  onClick={() => { setFile(null); setPreviewUrl(null); setDetectionResult(null); }}
                  className="absolute top-4 right-4 z-10 bg-slate-900/80 hover:bg-slate-800 text-white px-3 py-1.5 rounded-md text-xs font-medium border border-slate-700 backdrop-blur opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  Clear Image
                </button>
                {detectionResult && previewUrl ? (
                  <DetectionViewer imageUrl={previewUrl} detections={detectionResult.detections} />
                ) : (
                  <div className="w-full aspect-video glass-panel flex flex-col items-center justify-center border-slate-700 text-slate-500">
                    <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-cyan-400 mb-4"></div>
                    <p className="text-sm font-medium">Running RT-DETR-L...</p>
                  </div>
                )}
              </div>
            )}

            <ReasoningConsole imageFile={file} />
          </div>
          
          <div className="w-full lg:w-1/3">
            {detectionResult ? (
              <SidebarMetrics result={detectionResult} latencyMs={latency} />
            ) : (
              <div className="glass-panel p-6 h-full min-h-[400px] flex items-center justify-center border-dashed border-2 border-slate-800">
                <p className="text-sm text-slate-500 text-center max-w-[200px]">Upload an image to view detection metrics and confidence profiles.</p>
              </div>
            )}
          </div>
        </div>

        <EvaluationPanel />
        
      </main>
    </div>
  );
}

export default App;
