from ultralytics import YOLO

class YoloDetector:
    def __init__(self, model_name='yolov5s'):
        self.model = YOLO(model_name + '.pt')  # e.g., yolov5s.pt

    def detect(self, frame):
        results = self.model(frame)  # run inference
        detections = []
        for result in results[0].boxes.data.tolist():
            x1, y1, x2, y2, conf, cls = result
            detections.append({
                'bbox': (x1, y1, x2, y2),
                'confidence': conf,
                'class_name': self.model.names[int(cls)],
                'center': ((x1+x2)/2, (y1+y2)/2)
            })
        return detections

