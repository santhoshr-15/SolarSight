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
  'Non Defective': '#22c55e',
  'Physical Damage': '#a855f7',
  'Snow': '#3b82f6',
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
        const color = colors[det.class_name] || '#06b6d4';
        const box = det.bounding_box;
        
        const x = box.x1 * scale;
        const y = box.y1 * scale;
        const w = (box.x2 - box.x1) * scale;
        const h = (box.y2 - box.y1) * scale;

        ctx.strokeStyle = color;
        ctx.lineWidth = 2;
        ctx.strokeRect(x, y, w, h);
        
        ctx.fillStyle = color;
        const label = `${det.class_name} ${Math.round(det.confidence * 100)}%`;
        ctx.font = 'bold 12px sans-serif';
        const textMetrics = ctx.measureText(label);
        ctx.fillRect(x, y - 24, textMetrics.width + 12, 24);
        
        ctx.fillStyle = '#ffffff';
        ctx.fillText(label, x + 6, y - 8);
      });
    });

    resizeObserver.observe(containerRef.current);
    return () => resizeObserver.disconnect();
  }, [image, detections]);

  return (
    <div ref={containerRef} className="w-full relative rounded-xl overflow-hidden glass-panel border border-slate-700 bg-slate-900/80 shadow-2xl">
      {image ? (
        <canvas ref={canvasRef} className="w-full h-auto block" />
      ) : (
        <div className="w-full aspect-video flex flex-col items-center justify-center text-slate-500">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-cyan-400 mb-4"></div>
          <p className="text-sm font-medium">Processing image...</p>
        </div>
      )}
    </div>
  );
};
