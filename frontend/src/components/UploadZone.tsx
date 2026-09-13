import React, { useCallback, useState } from 'react';
import { UploadCloud, Image as ImageIcon } from 'lucide-react';

interface Props {
  onImageSelect: (file: File) => void;
  isLoading: boolean;
}

export const UploadZone: React.FC<Props> = ({ onImageSelect, isLoading }) => {
  const [isDragging, setIsDragging] = useState(false);

  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.type.startsWith('image/')) onImageSelect(file);
    }
  }, [onImageSelect]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (file.type.startsWith('image/')) onImageSelect(file);
    }
  };

  return (
    <div 
      onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
      className={`glass-card border-dashed border-2 flex flex-col items-center justify-center p-12 text-center transition-all duration-300 min-h-[400px] relative overflow-hidden ${
        isLoading 
          ? 'opacity-50 pointer-events-none border-slate-700' 
          : isDragging 
            ? 'border-solar-500 bg-solar-500/5 scale-[1.02]' 
            : 'border-slate-700/50 hover:border-solar-500/30 hover:bg-slate-800/40 cursor-pointer'
      }`}
      onClick={() => !isLoading && document.getElementById('image-upload')?.click()}
    >
      <input type="file" id="image-upload" className="hidden" accept="image/*" onChange={handleChange} />
      
      {/* Pulse effect rings */}
      <div className={`absolute inset-0 flex items-center justify-center pointer-events-none ${isDragging ? 'opacity-100' : 'opacity-0'} transition-opacity duration-500`}>
        <div className="w-64 h-64 rounded-full border border-solar-500/20 animate-pulse-slow"></div>
        <div className="absolute w-48 h-48 rounded-full border border-solar-500/30 animate-pulse-slow" style={{ animationDelay: '1s' }}></div>
      </div>

      <div className={`w-20 h-20 rounded-2xl bg-slate-800/80 flex items-center justify-center mb-6 border border-slate-700 shadow-xl relative z-10 transition-transform duration-300 ${isDragging ? 'scale-110 shadow-solar-500/20 border-solar-500/40' : ''}`}>
        <UploadCloud className={`w-10 h-10 transition-colors duration-300 ${isDragging ? 'text-solar-400' : 'text-ai-400'}`} />
      </div>
      
      <h3 className="text-2xl font-bold text-white mb-3 relative z-10">Upload Panel Image</h3>
      <p className="text-slate-400 mb-8 max-w-sm relative z-10">
        Drag and drop a high-resolution solar panel image, or click to browse.
      </p>
      
      <button 
        disabled={isLoading} 
        className="relative z-10 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-600 hover:border-solar-500/50 font-medium px-8 py-3.5 rounded-xl transition-all duration-300 disabled:opacity-50 flex items-center gap-2 hover:shadow-[0_0_15px_rgba(234,179,8,0.15)]"
      >
        <ImageIcon className="w-5 h-5 text-ai-400" />
        {isLoading ? 'Analyzing...' : 'Select Image'}
      </button>
    </div>
  );
};
