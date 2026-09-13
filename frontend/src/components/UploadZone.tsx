import React, { useCallback } from 'react';
import { UploadCloud, Image as ImageIcon } from 'lucide-react';

interface Props {
  onImageSelect: (file: File) => void;
  isLoading: boolean;
}

export const UploadZone: React.FC<Props> = ({ onImageSelect, isLoading }) => {
  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
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
      onDrop={handleDrop} 
      onDragOver={(e) => e.preventDefault()}
      className={`glass-panel border-dashed border-2 flex flex-col items-center justify-center p-12 text-center transition-all min-h-[400px] ${isLoading ? 'opacity-50 pointer-events-none border-slate-700' : 'border-slate-700 hover:border-cyan-500 hover:bg-slate-800/50 cursor-pointer'}`}
      onClick={() => !isLoading && document.getElementById('image-upload')?.click()}
    >
      <input type="file" id="image-upload" className="hidden" accept="image/*" onChange={handleChange} />
      <div className="w-16 h-16 rounded-full bg-slate-800 flex items-center justify-center mb-4">
        <UploadCloud className="w-8 h-8 text-cyan-400" />
      </div>
      <h3 className="text-xl font-semibold text-white mb-2">Upload Solar Panel Image</h3>
      <p className="text-sm text-slate-400 mb-8 max-w-sm">Drag and drop or click to browse your files. Supported formats: PNG, JPEG, WebP.</p>
      
      <button disabled={isLoading} className="bg-cyan-600 hover:bg-cyan-500 text-white font-medium px-8 py-3 rounded-lg transition-colors disabled:opacity-50 flex items-center gap-2 shadow-lg shadow-cyan-900/50">
        <ImageIcon className="w-5 h-5" />
        {isLoading ? 'Analyzing...' : 'Select Image'}
      </button>
    </div>
  );
};
