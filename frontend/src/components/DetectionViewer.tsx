import React, { useRef, useEffect, useState } from 'react';
import { Detection } from '../types';

interface Props {
  imageUrl: string;
  detections: Detection[];
}

const colors: Record<string, string> = {
  'Bird Drop': '#ef4444',
  'Defective': '#f97316',
  'Dusty': '#eab308',
  'Non Defective': '#10b981',
  'Physical Damage': '#8b5cf6',
  'Snow': '#38bdf8',
};

export const DetectionViewer: React.FC<Props> = ({ imageUrl, detections }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [image, setImage] = useState<HTMLImageElement | null>(null);

  useEffect(() => {
    const img = new Image();
    img.onload = () => setImage(img);
    img.src = imageUrl;
  }, [imageUrl]);

  useEffect(() => {
    if (!image || !canvasRef.current || !containerRef.current) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const resizeObserver = new ResizeObserver(() => {
      const containerWidth = containerRef.current?.clientWidth || 800;
      const scale = containerWidth / image.width;
      const canvasWidth = containerWidth;
      const canvasHeight = image.height * scale;
      
      canvas.width = canvasWidth;
      canvas.height = canvasHeight;

      ctx.drawImage(image, 0, 0, canvasWidth, canvasHeight);

      detections.forEach(det => {
        const color = colors[det.class_name] || '#0ea5e9';
        const box = det.bounding_box;
        
        const x = box.x1 * scale;
        const y = box.y1 * scale;
        const w = (box.x2 - box.x1) * scale;
        const h = (box.y2 - box.y1) * scale;

        // Translucent fill
        ctx.fillStyle = color + '20'; // ~12% opacity
        ctx.fillRect(x, y, w, h);

        // Border
        ctx.strokeStyle = color;
        ctx.lineWidth = 1.5;
        ctx.strokeRect(x, y, w, h);
        
        // Technical Corner Accents
        const cl = Math.min(12, w/4, h/4); // corner length
        ctx.lineWidth = 3;
        ctx.beginPath();
        // Top-left
        ctx.moveTo(x, y + cl); ctx.lineTo(x, y); ctx.lineTo(x + cl, y);
        // Top-right
        ctx.moveTo(x + w - cl, y); ctx.lineTo(x + w, y); ctx.lineTo(x + w, y + cl);
        // Bottom-right
        ctx.moveTo(x + w, y + h - cl); ctx.lineTo(x + w, y + h); ctx.lineTo(x + w - cl, y + h);
        // Bottom-left
        ctx.moveTo(x + cl, y + h); ctx.lineTo(x, y + h); ctx.lineTo(x, y + h - cl);
        ctx.stroke();
        
        // Label Background
        ctx.fillStyle = color + 'e6'; // 90% opacity
        const label = `${det.class_name.toUpperCase()} ${(det.confidence * 100).toFixed(1)}%`;
        ctx.font = 'bold 11px Inter, sans-serif';
        const textMetrics = ctx.measureText(label);
        ctx.fillRect(x, y - 26, textMetrics.width + 16, 26);
        
        // Label Text
        ctx.fillStyle = '#ffffff';
        ctx.fillText(label, x + 8, y - 8);
      });
    });

    resizeObserver.observe(containerRef.current);
    return () => resizeObserver.disconnect();
  }, [image, detections]);

  return (
    <div ref={containerRef} className="w-full relative rounded-lg overflow-hidden border border-slate-700 bg-slate-900 shadow-2xl animate-fade-in">
      {image ? (
        <canvas ref={canvasRef} className="w-full h-auto block" />
      ) : (
        <div className="w-full aspect-video flex flex-col items-center justify-center text-slate-500 bg-slate-950">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-solar-400 mb-4"></div>
          <p className="text-sm font-medium tracking-widest text-solar-500/80 animate-pulse">RENDERING PREVIEW...</p>
        </div>
      )}
    </div>
  );
};
