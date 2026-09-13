import React, { useState } from 'react';
import { BrainCircuit, MessageSquare, AlertTriangle, ShieldCheck, HelpCircle, ArrowRight, CheckCircle2 } from 'lucide-react';
import { api } from '../api';
import { ReasoningResponse } from '../types';

interface Props {
  imageFile: File | null;
}

const PRESET_QUESTIONS = [
  "How many Physical Damage detections are present?",
  "Is there any Defective panel?",
  "Which fault has the highest confidence?",
  "Where is the physical damage located?",
  "What types of faults are detected?",
  "What is a solar panel?"
];

const formatIntent = (intent: string) => {
  return intent
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
};

export const ReasoningConsole: React.FC<Props> = ({ imageFile }) => {
  const [question, setQuestion] = useState('');
  const [isThinking, setIsThinking] = useState(false);
  const [result, setResult] = useState<ReasoningResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (q: string) => {
    if (!q.trim()) return;
    setIsThinking(true);
    setError(null);
    setResult(null);
    
    try {
      const formData = new FormData();
      formData.append('question', q);
      if (imageFile) {
        formData.append('file', imageFile);
      }

      const res = await api.post<ReasoningResponse>('/reason', formData);
      setResult(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Reasoning request failed.");
    } finally {
      setIsThinking(false);
    }
  };

  return (
    <div className="flex flex-col gap-6">
      
      <div className="flex flex-wrap gap-2 mb-2">
        {PRESET_QUESTIONS.map((pq, idx) => (
          <button 
            key={idx}
            onClick={() => { setQuestion(pq); handleSubmit(pq); }}
            className="text-xs bg-slate-900 hover:bg-slate-800 text-ai-400/80 hover:text-ai-400 px-4 py-2 rounded-full border border-ai-500/20 hover:border-ai-500/50 transition-all duration-300"
          >
            {pq}
          </button>
        ))}
      </div>

      <div className="flex gap-3">
        <div className="relative flex-1 group">
          <MessageSquare className="absolute left-4 top-3.5 w-5 h-5 text-slate-500 group-focus-within:text-ai-400 transition-colors" />
          <input 
            type="text" 
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSubmit(question)}
            placeholder="What do you want to know about this panel?"
            className="w-full bg-slate-900/80 border border-slate-700/50 rounded-xl py-3.5 pl-12 pr-4 text-white focus:outline-none focus:border-ai-500 focus:ring-1 focus:ring-ai-500 transition-all shadow-inner"
          />
        </div>
        <button 
          onClick={() => handleSubmit(question)}
          disabled={isThinking || !question.trim()}
          className="bg-ai-600 hover:bg-ai-500 disabled:opacity-50 disabled:hover:bg-ai-600 text-white px-8 py-3.5 rounded-xl font-bold tracking-wide transition-all duration-300 flex items-center gap-2 shadow-[0_0_15px_rgba(14,165,233,0.2)] hover:shadow-[0_0_25px_rgba(14,165,233,0.4)]"
        >
          {isThinking ? (
            <><BrainCircuit className="w-5 h-5 animate-pulse" /> Thinking...</>
          ) : (
            'Ask AI'
          )}
        </button>
      </div>

      {error && (
        <div className="bg-rose-500/10 border border-rose-500/30 p-4 rounded-lg flex items-start gap-3 text-rose-400 animate-fade-in-up">
          <AlertTriangle className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <p className="text-sm">{error}</p>
        </div>
      )}

      {result && (
        <div className="bg-slate-900/60 border border-slate-700/50 rounded-xl overflow-hidden animate-fade-in-up shadow-2xl">
          <div className="bg-slate-800/80 px-5 py-3 border-b border-slate-700/50 flex justify-between items-center">
            <h3 className="text-sm font-semibold text-slate-300 flex items-center gap-2">
              <BrainCircuit className="w-4 h-4 text-ai-400" />
              Reasoning Pipeline Execution
            </h3>
            <span className="text-xs font-mono bg-slate-950 px-2.5 py-1 rounded-md text-ai-400 border border-ai-500/20">POST /reason</span>
          </div>
          
          <div className="p-6 space-y-6">
            
            {/* Visual Pipeline */}
            <div className="flex items-center justify-between gap-2 overflow-x-auto pb-2">
              <div className="flex flex-col items-center gap-2 min-w-[80px]">
                <div className="w-8 h-8 rounded-full bg-ai-500/20 border border-ai-500/50 flex items-center justify-center text-ai-400">
                  <MessageSquare className="w-4 h-4" />
                </div>
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest text-center">Query</span>
              </div>
              
              <div className="h-[2px] flex-1 bg-slate-700 relative"><div className="absolute inset-0 bg-ai-500/50 w-full animate-pulse"></div></div>
              
              <div className="flex flex-col items-center gap-2 min-w-[80px]">
                <div className="w-8 h-8 rounded-full bg-ai-500/20 border border-ai-500/50 flex items-center justify-center text-ai-400">
                  <BrainCircuit className="w-4 h-4" />
                </div>
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest text-center">Intent</span>
              </div>

              <div className="h-[2px] flex-1 bg-slate-700 relative"><div className="absolute inset-0 bg-ai-500/50 w-full animate-pulse" style={{ animationDelay: '200ms' }}></div></div>
              
              <div className="flex flex-col items-center gap-2 min-w-[80px]">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${result.detector_invoked ? 'bg-solar-500/20 border border-solar-500/50 text-solar-400' : 'bg-slate-800 border border-slate-700 text-slate-500'}`}>
                  <HelpCircle className="w-4 h-4" />
                </div>
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest text-center">Vision</span>
              </div>

              <div className="h-[2px] flex-1 bg-slate-700 relative"><div className="absolute inset-0 bg-ai-500/50 w-full animate-pulse" style={{ animationDelay: '400ms' }}></div></div>
              
              <div className="flex flex-col items-center gap-2 min-w-[80px]">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${result.guardrail_triggered ? 'bg-rose-500/20 border border-rose-500/50 text-rose-400' : 'bg-emerald-500/20 border border-emerald-500/50 text-emerald-400'}`}>
                  {result.guardrail_triggered ? <AlertTriangle className="w-4 h-4" /> : <ShieldCheck className="w-4 h-4" />}
                </div>
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest text-center">Guardrail</span>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="glass-card p-4 bg-slate-950/50">
                <div className="text-[11px] font-semibold text-slate-500 mb-1.5 uppercase tracking-wider">Detected Intent</div>
                <div className="text-sm font-medium text-white break-words">{formatIntent(result.intent)}</div>
              </div>
              <div className="glass-card p-4 bg-slate-950/50">
                <div className="text-[11px] font-semibold text-slate-500 mb-1.5 uppercase tracking-wider">Vision Detection</div>
                <div className="text-sm font-medium text-white flex items-center gap-2">
                  {result.detector_invoked ? (
                    <><span className="w-2 h-2 rounded-full bg-solar-400"></span> Invoked (Found {result.detections_used})</>
                  ) : (
                    <><span className="w-2 h-2 rounded-full bg-slate-600"></span> Bypassed</>
                  )}
                </div>
              </div>
              <div className="glass-card p-4 bg-slate-950/50">
                <div className="text-[11px] font-semibold text-slate-500 mb-1.5 uppercase tracking-wider">Safety Guardrail</div>
                <div className="text-sm font-medium flex items-center gap-1.5">
                  {result.guardrail_triggered ? (
                    <span className="text-rose-400 flex items-center gap-1.5"><AlertTriangle className="w-4 h-4" /> Triggered</span>
                  ) : (
                    <span className="text-emerald-400 flex items-center gap-1.5"><ShieldCheck className="w-4 h-4" /> Passed</span>
                  )}
                </div>
              </div>
            </div>

            {result.evidence && (
              <div className="glass-card p-4 bg-slate-900/80 border border-slate-700/50 shadow-inner">
                <div className="text-[11px] font-semibold text-slate-400 mb-3 uppercase tracking-wider flex items-center gap-2">
                  <BrainCircuit className="w-3.5 h-3.5 text-ai-500" /> Structured Evidence
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                  <div>
                    <div className="text-xs text-slate-500 mb-1">Relevant Class</div>
                    <div className="text-sm font-medium text-slate-200">{result.evidence.relevant_class || "N/A"}</div>
                  </div>
                  <div>
                    <div className="text-xs text-slate-500 mb-1">Detection Count</div>
                    <div className="text-sm font-medium text-slate-200">{result.evidence.count}</div>
                  </div>
                  <div>
                    <div className="text-xs text-slate-500 mb-1">Max Confidence</div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-slate-200">
                        {result.evidence.max_confidence > 0 ? `${(result.evidence.max_confidence * 100).toFixed(0)}%` : "N/A"}
                      </span>
                      {result.evidence.confidence_tier !== "N/A" && (
                        <span className={`text-[10px] px-1.5 py-0.5 rounded-sm font-bold tracking-wider ${
                          result.evidence.confidence_tier === 'HIGH' ? 'bg-emerald-500/20 text-emerald-400' :
                          result.evidence.confidence_tier === 'MEDIUM' ? 'bg-amber-500/20 text-amber-400' :
                          'bg-rose-500/20 text-rose-400'
                        }`}>
                          {result.evidence.confidence_tier}
                        </span>
                      )}
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-slate-500 mb-1">Spatial Location</div>
                    <div className="text-sm font-medium text-slate-200 capitalize">{result.evidence.location?.replace('-', ' ') || "N/A"}</div>
                  </div>
                </div>
                {result.evidence.overlapping_detections && (
                  <div className="mt-4 bg-amber-500/10 border border-amber-500/20 rounded-md p-2.5 flex items-start gap-2 text-amber-400/90 text-xs">
                    <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                    <p>Overlapping bounding boxes detected. Repeated counts for the same physical fault are possible.</p>
                  </div>
                )}
              </div>
            )}

            {result.guardrail_triggered ? (
              <div className="p-5 bg-rose-500/10 border border-rose-500/30 rounded-xl relative overflow-hidden">
                <div className="absolute top-0 right-0 w-32 h-32 bg-rose-500/10 rounded-full blur-2xl -mr-16 -mt-16 pointer-events-none"></div>
                <div className="text-rose-500 font-bold mb-2 flex items-center gap-2 text-sm uppercase tracking-wider relative z-10">
                  <AlertTriangle className="w-5 h-5" /> Insufficient Visual Evidence
                </div>
                <p className="text-rose-200/90 leading-relaxed relative z-10">{result.answer}</p>
              </div>
            ) : (
              <div className="p-6 bg-slate-800/40 border border-ai-500/20 rounded-xl relative overflow-hidden shadow-[inset_0_0_20px_rgba(14,165,233,0.05)]">
                <div className="absolute top-0 right-0 w-32 h-32 bg-ai-500/10 rounded-full blur-2xl -mr-16 -mt-16 pointer-events-none"></div>
                <div className="text-ai-400 font-bold mb-3 text-xs uppercase tracking-widest flex items-center gap-2 relative z-10">
                  <CheckCircle2 className="w-4 h-4" /> Generated Answer
                </div>
                <p className="text-white text-lg leading-relaxed relative z-10">{result.answer}</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
