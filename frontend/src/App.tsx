import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { UploadZone } from './components/UploadZone';
import { DetectionViewer } from './components/DetectionViewer';
import { SidebarMetrics } from './components/SidebarMetrics';
import { ReasoningConsole } from './components/ReasoningConsole';
import { EvaluationPanel } from './components/EvaluationPanel';
import { api } from './api';
import { DetectionResponse } from './types';
import { AlertTriangle, Info, ArrowRight, Code, Code2, Activity } from 'lucide-react';

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [detectionResult, setDetectionResult] = useState<DetectionResponse | null>(null);
  const [isDetecting, setIsDetecting] = useState(false);
  const [latency, setLatency] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [apiStatus, setApiStatus] = useState<'checking' | 'online' | 'offline'>('checking');

  useEffect(() => {
    // Health check on load
    api.get('/health')
      .then(() => setApiStatus('online'))
      .catch(() => setApiStatus('offline'));
  }, []);

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

  const scrollToUpload = () => {
    document.getElementById('inspection-zone')?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col relative overflow-x-hidden selection:bg-ai-900 selection:text-ai-100">
      
      {/* Background Image & Cinematic Gradient */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        <img 
          src="/assets/hero-bg.jpg" 
          alt="Solar Background" 
          className="absolute inset-0 w-full h-full object-cover opacity-40 object-center"
        />
        <div className="absolute inset-0 bg-hero-overlay"></div>
        {/* Animated subtle light sweep */}
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-ai-400/5 to-transparent w-[200%] animate-[scan_8s_ease-in-out_infinite] -skew-x-12 opacity-50"></div>
      </div>
      
      <div className="z-10 flex flex-col flex-1">
        <Header apiStatus={apiStatus} />
        
        <main className="flex-1 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full flex flex-col gap-16 mt-16 mb-24">
          
          <section className="flex flex-col items-center text-center max-w-5xl mx-auto space-y-8 animate-fade-in-up stagger-1 py-12">
            <div className="flex flex-wrap items-center justify-center gap-3">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full glass-card text-xs font-medium text-ai-400 border border-ai-500/30 shadow-[0_0_15px_rgba(14,165,233,0.2)]">
                <span className={`w-2 h-2 rounded-full ${apiStatus === 'online' ? 'bg-emerald-400 animate-pulse' : 'bg-rose-500'}`}></span>
                {apiStatus === 'online' ? 'API CONNECTED' : 'API OFFLINE'}
              </div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full glass-card text-xs font-medium text-slate-300 border border-slate-700/50">
                <Activity className="w-3.5 h-3.5" />
                RT-DETR-L ENGINE
              </div>
              <div className="hidden sm:inline-flex items-center gap-2 px-3 py-1 rounded-full glass-card text-xs font-medium text-slate-300 border border-slate-700/50">
                6 FAULT CLASSES
              </div>
              <div className="hidden sm:inline-flex items-center gap-2 px-3 py-1 rounded-full glass-card text-xs font-medium text-slate-300 border border-slate-700/50">
                REAL-TIME ANALYSIS
              </div>
            </div>
            
            <h1 className="text-5xl sm:text-7xl lg:text-8xl font-extrabold text-transparent bg-clip-text bg-gradient-to-br from-white via-slate-100 to-slate-400 tracking-tight leading-[1.1] pb-2">
              See Every Fault.<br/>
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-solar-400 to-solar-600">Understand Every Panel.</span>
            </h1>
            
            <p className="text-slate-400 text-lg sm:text-xl max-w-2xl leading-relaxed">
              AI-powered solar panel inspection using RT-DETR object detection and constrained visual reasoning. Built for precision.
            </p>
            
            <div className="flex flex-col sm:flex-row items-center justify-center gap-5 pt-8 w-full sm:w-auto">
              <button 
                onClick={scrollToUpload}
                className="w-full sm:w-auto px-10 py-4 rounded-xl bg-solar-500 hover:bg-solar-400 text-slate-950 text-lg font-bold tracking-wide transition-all duration-300 flex items-center justify-center gap-3 shadow-[0_0_20px_rgba(234,179,8,0.4)] hover:shadow-[0_0_35px_rgba(234,179,8,0.6)] transform hover:-translate-y-1 group relative overflow-hidden"
              >
                <div className="absolute inset-0 bg-white/20 -translate-x-full group-hover:translate-x-full transition-transform duration-700 skew-x-12"></div>
                Inspect a Panel
                <ArrowRight className="w-6 h-6 group-hover:translate-x-1 transition-transform" />
              </button>
              
              <a 
                href="https://github.com/santhoshr-15/SolarSight" 
                target="_blank" 
                rel="noreferrer"
                className="w-full sm:w-auto px-8 py-4 rounded-xl glass-panel glass-panel-hover text-white font-medium flex items-center justify-center gap-2 border border-slate-600/50 hover:bg-slate-800/80 transition-all duration-300"
              >
                <Code className="w-5 h-5" />
                View on GitHub
              </a>
            </div>
          </section>

          {/* Core App Layout */}
          <section id="inspection-zone" className="flex flex-col xl:flex-row items-start gap-8 animate-fade-in-up stagger-2 scroll-mt-24">
            
            {/* Left Column: Vision & Reasoning */}
            <div className="w-full xl:w-2/3 flex flex-col gap-8">
              
              {/* Inspection Card */}
              <div className="glass-panel p-1 rounded-xl shadow-2xl relative overflow-hidden group">
                {/* Animated gradient border effect */}
                <div className="absolute inset-0 bg-gradient-to-r from-solar-500/20 via-ai-500/20 to-slate-800/20 opacity-0 group-hover:opacity-100 transition-opacity duration-1000 blur-xl"></div>
                
                <div className="bg-slate-900/90 rounded-lg p-6 relative z-10">
                  <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
                    <div>
                      <h2 className="text-xl font-bold text-white flex items-center gap-2">
                        <div className="w-1.5 h-6 bg-solar-500 rounded-full"></div>
                        Visual Inspection
                      </h2>
                      <p className="text-sm text-slate-400 mt-1">Upload infrared or visible-spectrum panel imagery.</p>
                    </div>
                    {!file && (
                      <button onClick={handleDemoMode} className="flex-shrink-0 text-xs bg-slate-800/80 hover:bg-slate-700 text-slate-300 px-4 py-2.5 rounded-lg border border-slate-700 transition-colors flex items-center gap-2 shadow-lg">
                        <Info className="w-4 h-4 text-ai-400" />
                        Load Demo Sample
                      </button>
                    )}
                  </div>

                  {error && (
                    <div className="mb-6 bg-rose-500/10 border border-rose-500/30 p-4 rounded-lg flex items-start gap-3 text-rose-400 animate-fade-in">
                      <AlertTriangle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                      <p className="text-sm">{error}</p>
                    </div>
                  )}

                  {!file ? (
                    <UploadZone onImageSelect={handleImageSelect} isLoading={isDetecting} />
                  ) : (
                    <div className="relative rounded-lg overflow-hidden border border-slate-700/50 bg-slate-950/50">
                      <div className="absolute top-4 right-4 z-20 flex gap-2">
                        <button 
                          onClick={() => { setFile(null); setPreviewUrl(null); setDetectionResult(null); }}
                          className="bg-slate-900/80 hover:bg-slate-800 text-white px-3 py-1.5 rounded-md text-xs font-medium border border-slate-700 backdrop-blur transition-colors shadow-lg"
                        >
                          Clear Image
                        </button>
                      </div>
                      
                      {detectionResult && previewUrl ? (
                        <DetectionViewer imageUrl={previewUrl} detections={detectionResult.detections} />
                      ) : (
                        <div className="w-full aspect-video flex flex-col items-center justify-center relative overflow-hidden">
                          <img src={previewUrl!} alt="Preview" className="absolute inset-0 w-full h-full object-contain opacity-30" />
                          
                          {/* Animated Scanning Beam */}
                          <div className="absolute inset-0 z-10 pointer-events-none">
                            <div className="w-full h-1 bg-solar-400 shadow-[0_0_15px_rgba(234,179,8,1)] animate-scan"></div>
                          </div>
                          
                          <div className="z-20 glass-card px-6 py-4 flex flex-col items-center gap-3 backdrop-blur-xl border-solar-500/30">
                            <div className="relative">
                              <div className="w-12 h-12 border-2 border-slate-700 border-t-solar-400 rounded-full animate-spin"></div>
                              <div className="absolute inset-0 flex items-center justify-center text-solar-400">
                                <Activity className="w-5 h-5" />
                              </div>
                            </div>
                            <p className="text-sm font-bold tracking-widest text-transparent bg-clip-text bg-gradient-to-r from-solar-400 to-ai-400 animate-pulse">
                              ANALYZING PANEL...
                            </p>
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>

              {/* Reasoning Card */}
              <div className="glass-panel p-1 rounded-xl shadow-2xl relative overflow-hidden">
                <div className="bg-slate-900/90 rounded-lg p-6 relative z-10 h-full">
                  <div className="flex items-center gap-2 mb-6">
                    <div className="w-1.5 h-6 bg-ai-500 rounded-full"></div>
                    <h2 className="text-xl font-bold text-white">Ask SolarSight</h2>
                  </div>
                  <ReasoningConsole imageFile={file} />
                </div>
              </div>
            </div>
            
            {/* Right Column: Dashboard & Metrics */}
            <div className="w-full xl:w-1/3 flex flex-col gap-8 h-full">
              {detectionResult ? (
                <div className="animate-fade-in-up stagger-3 h-full">
                  <SidebarMetrics result={detectionResult} latencyMs={latency} />
                </div>
              ) : (
                <div className="glass-panel p-8 h-[400px] flex flex-col items-center justify-center text-center border-dashed border-2 border-slate-700/50 bg-slate-900/30">
                  <div className="w-16 h-16 rounded-2xl bg-slate-800/50 flex items-center justify-center mb-4 border border-slate-700/50">
                    <Activity className="w-8 h-8 text-slate-500" />
                  </div>
                  <h3 className="text-lg font-medium text-slate-300 mb-2">Awaiting Image</h3>
                  <p className="text-sm text-slate-500 max-w-[240px]">
                    Upload a panel image to view the detection dashboard, confidence metrics, and class profiles.
                  </p>
                </div>
              )}
            </div>
          </section>

          {/* Bottom Evaluation Section */}
          <section className="animate-fade-in-up stagger-4">
            <EvaluationPanel />
          </section>
          
        </main>
      </div>
    </div>
  );
}

export default App;

