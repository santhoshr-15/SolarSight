import React, { useState } from 'react';
import { BrainCircuit, MessageSquare, AlertTriangle, ShieldCheck, HelpCircle } from 'lucide-react';
import { api } from '../api';
import { ReasoningResponse } from '../types';

interface Props {
  imageFile: File | null;
}

const PRESET_QUESTIONS = [
  "How many Physical Damage detections are present?",
  "Is there any Defective panel?",
  "How many Dusty regions were detected?",
  "What is a solar panel?"
];

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
    <div className="glass-panel p-6 flex flex-col gap-6">
      <div className="flex items-center gap-3 border-b border-slate-700/50 pb-4">
        <div className="p-2 bg-purple-500/20 rounded-lg border border-purple-500/30">
          <BrainCircuit className="w-6 h-6 text-purple-400" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-white">Ask SolarSight</h2>
          <p className="text-sm text-slate-400">Ask constrained questions about the visual evidence.</p>
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        {PRESET_QUESTIONS.map((pq, idx) => (
          <button 
            key={idx}
            onClick={() => { setQuestion(pq); handleSubmit(pq); }}
            className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-1.5 rounded-full border border-slate-700 transition-colors"
          >
            {pq}
          </button>
        ))}
      </div>

      <div className="flex gap-3">
        <div className="relative flex-1">
          <MessageSquare className="absolute left-3 top-3 w-5 h-5 text-slate-500" />
          <input 
            type="text" 
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSubmit(question)}
            placeholder="What do you want to know?"
            className="w-full bg-slate-900 border border-slate-700 rounded-lg py-3 pl-10 pr-4 text-white focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500"
          />
        </div>
        <button 
          onClick={() => handleSubmit(question)}
          disabled={isThinking || !question.trim()}
          className="bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white px-6 py-3 rounded-lg font-medium transition-colors"
        >
          {isThinking ? 'Analyzing...' : 'Ask'}
        </button>
      </div>

      {error && (
        <div className="bg-rose-500/10 border border-rose-500/30 p-4 rounded-lg flex gap-3 text-rose-400">
          <AlertTriangle className="w-5 h-5 flex-shrink-0" />
          <p className="text-sm">{error}</p>
        </div>
      )}

      {result && (
        <div className="bg-slate-900/50 border border-slate-700 rounded-xl overflow-hidden">
          <div className="bg-slate-800/50 px-4 py-3 border-b border-slate-700 flex justify-between items-center">
            <h3 className="text-sm font-semibold text-slate-300">Reasoning Result</h3>
            <span className="text-xs font-mono bg-slate-900 px-2 py-1 rounded text-slate-400">POST /reason</span>
          </div>
          
          <div className="p-5 space-y-4">
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                <div className="text-xs text-slate-500 mb-1">Intent</div>
                <div className="text-sm font-medium text-white">{result.intent}</div>
              </div>
              <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                <div className="text-xs text-slate-500 mb-1">Detector Used</div>
                <div className="text-sm font-medium text-white">{result.detector_invoked ? 'Yes' : 'Bypassed'}</div>
              </div>
              <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                <div className="text-xs text-slate-500 mb-1">Guardrail Status</div>
                <div className="text-sm font-medium flex items-center gap-1">
                  {result.guardrail_triggered ? (
                    <span className="text-yellow-500"><AlertTriangle className="w-4 h-4 inline" /> Triggered</span>
                  ) : (
                    <span className="text-emerald-400"><ShieldCheck className="w-4 h-4 inline" /> Passed</span>
                  )}
                </div>
              </div>
            </div>

            {result.guardrail_triggered ? (
              <div className="mt-4 p-4 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
                <div className="text-yellow-500 font-bold mb-1 flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5" /> INSUFFICIENT EVIDENCE
                </div>
                <p className="text-yellow-400/90">{result.answer}</p>
              </div>
            ) : (
              <div className="mt-4 p-4 bg-slate-800/30 border border-slate-700/50 rounded-lg">
                <div className="text-slate-400 font-medium mb-2 text-xs uppercase tracking-wider">Generated Answer</div>
                <p className="text-white text-lg">{result.answer}</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
