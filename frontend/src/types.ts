export interface BoundingBox {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

export interface Detection {
  class_id: number;
  class_name: string;
  confidence: number;
  bounding_box: BoundingBox;
}

export interface DetectionResponse {
  total_detections: number;
  counts: Record<string, number>;
  detections: Detection[];
}

export interface ReasoningResponse {
  question: string;
  intent: string;
  guardrail_triggered: boolean;
  detections_used: number;
  detector_invoked: boolean;
  answer: string;
}

export interface HealthResponse {
  status: string;
  model: string;
}
